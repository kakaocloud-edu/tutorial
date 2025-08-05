import os
import boto3
import io
import pyarrow.parquet as pq
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

def load_data():
    bucket       = os.environ["S3_BUCKET"]
    key          = os.environ["S3_KEY"]
    access_key   = os.environ["ACC_KEY"]
    secret_key   = os.environ["SEC_KEY"]
    region       = os.getenv("REGION", "kr-central-2")
    endpoint_url = os.getenv("S3_ENDPOINT_URL",
                             "https://objectstorage.kr-central-2.kakaocloud.com")

    s3 = boto3.client(
        service_name="s3",
        region_name=region,
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    obj = s3.get_object(Bucket=bucket, Key=key)
    buf = io.BytesIO(obj["Body"].read())
    return pq.read_table(buf).to_pandas()

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
