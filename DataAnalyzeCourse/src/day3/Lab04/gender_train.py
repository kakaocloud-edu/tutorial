# train.py
import argparse, json, unicodedata, warnings, os
import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score, accuracy_score, average_precision_score
from sklearn.calibration import CalibratedClassifierCV

warnings.filterwarnings("ignore")


def norm_series(s: pd.Series) -> pd.Series:
    s = s.astype("string").str.strip()
    return s.apply(lambda x: unicodedata.normalize("NFKC", x) if pd.notna(x) else x)


def build_dataset(input_path: str, min_prelogin_events: int, known_cats: list[str]):
    df = pd.read_csv(input_path, low_memory=False)

    # --- 공통 정렬/타임스탬프 ---
    df["ts"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["session_id", "ts"]).copy()
    sort_cols = ["session_id", "ts"]
    if "event_id" in df.columns:
        sort_cols.append("event_id")
    df = df.sort_values(sort_cols).reset_index(drop=True)

    # --- 로그인 이전(pre-login) 구간 추출 ---
    uid_str = df.get("user_id", pd.Series([""] * len(df))).astype("string").str.strip()
    anon_like = {"", "0", "-1", "None", "none", "NULL", "null", "NaN", "nan"}
    has_uid = uid_str.notna() & ~uid_str.isin(anon_like)
    appeared = has_uid.groupby(df["session_id"]).cummax()
    pre = df.loc[~appeared].copy()

    # 세션 최소 이벤트 수 필터
    pre_counts = pre.groupby("session_id").size()
    valid_sessions = pre_counts.index[pre_counts >= int(min_prelogin_events)]
    pre = pre[pre["session_id"].isin(valid_sessions)].copy()

    # --- 라벨(성별) by 세션 (로그인 이후에서 확인) ---
    df_gender = df.copy()
    df_gender["gender_norm"] = (
        df_gender.get("gender", pd.Series([np.nan] * len(df_gender)))
        .astype("string").str.strip().str.upper()
        .replace({"FEMALE": "F", "MALE": "M"})
    )
    lab_full = (
        df_gender[df_gender["gender_norm"].isin(["M", "F"])]
        .groupby("session_id")["gender_norm"].agg(lambda s: s.iloc[0])
    )

    # --- 수치 집계 피처 ---
    # 안전: 없는 컬럼 기본값 처리
    if "last_action_elapsed" not in pre.columns:
        pre["last_action_elapsed"] = 0.0
    if "resolved_category" not in pre.columns:
        pre["resolved_category"] = ""

    agg_num = pre.groupby("session_id").agg(
        n_events=("session_id", "size"),
        search_count_sum=("search_count", "sum"),
        cart_item_count_sum=("cart_item_count", "sum"),
        page_depth_mean=("page_depth", "mean"),
        last_elapsed_mean=("last_action_elapsed", "mean"),
        unique_pages=("current_state", "nunique"),
        unique_categories=("resolved_category", "nunique"),
    ).fillna(0.0)

    first_ts = pre.groupby("session_id")["ts"].min()
    agg_num["start_hour"] = first_ts.dt.hour
    agg_num["start_weekday"] = first_ts.dt.weekday

    keep_sessions = agg_num.index.intersection(lab_full.index)
    X_num = agg_num.loc[keep_sessions].copy()
    y = lab_full.loc[keep_sessions].rename("gender").copy()

    # --- 카테고리 파생(카운트/비율/log) ---
    known_cats_norm = [unicodedata.normalize("NFKC", c.strip()) for c in known_cats]
    norm_to_orig = {unicodedata.normalize("NFKC", c.strip()): c for c in known_cats}

    pre_cat_norm = norm_series(pre["resolved_category"])
    mask = pre_cat_norm.isin(known_cats_norm)
    pre_kept = pre[mask].copy()
    pre_kept["cat_norm"] = pre_cat_norm[mask].values
    pre_kept["one"] = 1

    cat_cnt = pre_kept.pivot_table(
        index="session_id", columns="cat_norm", values="one", aggfunc="sum", fill_value=0
    )
    # 고정 컬럼 순서
    cat_cnt = cat_cnt.reindex(columns=known_cats_norm, fill_value=0)
    cat_cnt.columns = [norm_to_orig[c] for c in cat_cnt.columns]
    cat_cnt.columns = [f"cat_cnt::{c}" for c in cat_cnt.columns]
    cat_cnt = cat_cnt.reindex(X_num.index).fillna(0).astype(int)
    cat_cnt_cols = list(cat_cnt.columns)

    # 비율/로그
    cat_prop = cat_cnt.div(X_num["n_events"].replace(0, 1), axis=0)
    cat_prop.columns = [c.replace("cat_cnt::", "cat_prop::") for c in cat_cnt_cols]
    cat_log = np.log1p(cat_cnt)
    cat_log.columns = [c.replace("cat_cnt::", "cat_log::") for c in cat_cnt_cols]

    # 최종 X, y
    X = (
        X_num
        .join(cat_cnt, how="left")
        .join(cat_prop, how="left")
        .join(cat_log, how="left")
    ).fillna(0)

    y_bin = y.astype("string").str.strip().str.upper().replace({"FEMALE":"F","MALE":"M"}).map({"F":0,"M":1}).astype(int)
    return X, y_bin


def tune_threshold(proba, y_true, lo: float, hi: float, steps: int):
    ths = np.linspace(lo, hi, steps)
    best_t, best_f1 = 0.5, -1.0
    for t in ths:
        pred = (proba >= t).astype(int)
        f1 = f1_score(y_true, pred, average="macro")
        if f1 > best_f1:
            best_t, best_f1 = float(t), float(f1)
    return best_t, best_f1


def main():
    p = argparse.ArgumentParser()
    # 데이터/전처리
    p.add_argument("--input-path", type=str, default="datasets/gender/processed_user_behavior.joined.csv")
    p.add_argument("--min-prelogin-events", type=int, default=2)
    p.add_argument("--known-cats", type=str, default="Books,Electronics,Gaming,Home,Fashion")
    p.add_argument("--valid-size", type=float, default=0.2)
    p.add_argument("--random-state", type=int, default=42)

    # 모델/튜닝 인자 (Katib가 건네줌)
    p.add_argument("--penalty", type=str, choices=["l1","l2","elasticnet"], default="l2")
    p.add_argument("--C", type=float, default=1.0)
    p.add_argument("--l1-ratio", type=float, default=0.5)
    p.add_argument("--scaler", type=str, choices=["standard","robust"], default="standard")
    p.add_argument("--class-weight", type=str, choices=["balanced","none"], default="balanced")

    p.add_argument("--calib-method", type=str, choices=["isotonic","sigmoid"], default="isotonic")
    p.add_argument("--calib-cv", type=int, default=5)

    p.add_argument("--threshold-strategy", type=str, choices=["prod","tuned"], default="prod")
    p.add_argument("--prod-threshold", type=float, default=0.444)
    p.add_argument("--tune-t-lo", type=float, default=0.3)
    p.add_argument("--tune-t-hi", type=float, default=0.7)
    p.add_argument("--tune-t-steps", type=int, default=61)

    # (선택) 아티팩트 저장
    p.add_argument("--artifacts-dir", type=str, default="models/gender")

    args, _unknown = p.parse_known_args()

    known_cats = [c.strip() for c in args.known_cats.split(",") if c.strip()]

    # 데이터셋 구성
    X, y = build_dataset(args.input_path, args.min_prelogin_events, known_cats)

    sss = StratifiedShuffleSplit(n_splits=1, test_size=args.valid_size, random_state=args.random_state)
    tr_idx, va_idx = next(sss.split(X, y))
    X_tr, X_va = X.iloc[tr_idx], X.iloc[va_idx]
    y_tr, y_va = y.iloc[tr_idx], y.iloc[va_idx]

    # 파이프라인 구성
    scaler = StandardScaler(with_mean=True, with_std=True) if args.scaler == "standard" \
             else RobustScaler(with_centering=True, with_scaling=True)

    class_weight = None if args.class_weight == "none" else "balanced"

    clf = LogisticRegression(
        solver="saga",
        penalty=args.penalty,
        C=float(args.C),
        l1_ratio=(float(args.l1_ratio) if args.penalty == "elasticnet" else None),
        class_weight=class_weight,
        max_iter=5000,
        random_state=args.random_state,
    )

    pipe = Pipeline([("scaler", scaler), ("clf", clf)])

    # 보정
    try:
        cal = CalibratedClassifierCV(estimator=pipe, method=args.calib_method, cv=args.calib_cv)
    except TypeError:
        cal = CalibratedClassifierCV(base_estimator=pipe, method=args.calib_method, cv=args.calib_cv)

    cal.fit(X_tr, y_tr)

    proba_va = cal.predict_proba(X_va)[:, 1]

    # 임계값 선택
    if args.threshold_strategy == "tuned":
        th = float(args.prod_threshold)
    else:
        th, _ = tune_threshold(proba_va, y_va, args.tune_t_lo, args.tune_t_hi, args.tune_t_steps)

    y_pred = (proba_va >= th).astype(int)

    # 지표
    macro_f1 = f1_score(y_va, y_pred, average="macro")
    acc = accuracy_score(y_va, y_pred)
    pr_auc = average_precision_score(y_va, proba_va)

    # Katib StdOut 수집용 출력 (키 이름 엄수)
    print(f"Valid-macroF1={macro_f1:.6f}")
    print(f"Valid-accuracy={acc:.6f}")
    print(f"PR-AUC={pr_auc:.6f}")
    print(f"Used-threshold={th:.6f}")

    # (선택) 아티팩트 저장
    os.makedirs(args.artifacts_dir, exist_ok=True)
    try:
        from joblib import dump
        dump(cal, os.path.join(args.artifacts_dir, "logistic_calibrated.joblib"))
        meta = {
            "penalty": args.penalty,
            "C": args.C,
            "l1_ratio": (args.l1_ratio if args.penalty == "elasticnet" else None),
            "scaler": args.scaler,
            "class_weight": args.class_weight,
            "calibration": {"method": args.calib_method, "cv": args.calib_cv},
            "threshold": {"strategy": args.threshold_strategy, "value": th},
            "min_prelogin_events": args.min_prelogin_events,
            "valid_size": args.valid_size,
            "random_state": args.random_state,
        }
        with open(os.path.join(args.artifacts_dir, "logistic_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[warn] artifact save failed: {e}")


if __name__ == "__main__":
    main()
