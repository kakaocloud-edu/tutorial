import boto3
import io
import pyarrow.parquet as pq
import pandas as pd
import argparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

def load_data(bucket, key, access_key, secret_key):
    s3 = boto3.client(
        service_name="s3",
        region_name="kr-central-2",
        endpoint_url="https://objectstorage.kr-central-2.kakaocloud.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    obj = s3.get_object(Bucket=bucket, Key=key)
    buf = io.BytesIO(obj["Body"].read())
    return pq.read_table(buf).to_pandas()

def train_and_log(df, n_estimators, max_depth):
    # 레이블: next_state, 피처: 나머지 컬럼
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

    # Katib이 읽을 로그 포맷으로 저장
    with open("/tmp/metrics.log", "w") as f:
        f.write(f"{{metricName: accuracy, metricValue: {acc}}}\n")

    print(f"[Train] n_estimators={n_estimators}, max_depth={max_depth}, accuracy={acc:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--s3-bucket",    required=True)
    parser.add_argument("--s3-key",       required=True)
    parser.add_argument("--aws-access-key", required=True)
    parser.add_argument("--aws-secret-key", required=True)
    parser.add_argument("--n_estimators", type=int, default=100)
    parser.add_argument("--max_depth",    type=int, default=None)
    args = parser.parse_args()

    df = load_data(
        args.s3_bucket,
        args.s3_key,
        args.aws_access_key,
        args.aws_secret_key
    )
    train_and_log(df, args.n_estimators, args.max_depth)
