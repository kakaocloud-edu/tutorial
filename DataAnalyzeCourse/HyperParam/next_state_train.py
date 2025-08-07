# train.py
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

def load_data():
    # 로컬 Parquet 파일 경로 (기본값)
    local_path = os.getenv("/home/jovyan", "processed_user_behavior.parquet")
    return pd.read_parquet(local_path)

def train_and_log(df, n_estimators, max_depth):
    y = df["next_state"]
    X = df.drop(columns=["next_state"])
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42
    )
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)

    # 메트릭 로그
    with open("/tmp/metrics.log", "w") as f:
        f.write(f"{{metricName: accuracy, metricValue: {acc}}}\n")

    print(f"[Train] n_estimators={n_estimators}, max_depth={max_depth}, accuracy={acc:.4f}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--n_estimators",
        type=int,
        default=int(os.getenv("N_ESTIMATORS", "100")),
        help="Number of trees"
    )
    parser.add_argument(
        "--max_depth",
        type=lambda x: int(x) if x not in ("", "None") else None,
        default=os.getenv("MAX_DEPTH", None),
        help="Max tree depth"
    )
    args = parser.parse_args()

    df = load_data()
    train_and_log(df, args.n_estimators, args.max_depth)
