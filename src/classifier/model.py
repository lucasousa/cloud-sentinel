import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold
from sklearn.tree import DecisionTreeClassifier

from src.classifier.utils import classify_full_metrics, get_sla_values

MODEL_PATH = Path(__file__).parent / "model.pkl"
TRAINING_PATH = Path(__file__).parent / "data" / "training.json"


async def train():
    sla = await get_sla_values()
    dataset = pd.read_json(TRAINING_PATH)
    dataset["status"] = dataset.apply(classify_full_metrics, axis=1, sla=sla)
    dataset = dataset.drop(
        columns=[
            "timestamp",
            "provider",
            "service",
            "service_type",
            "cost",
            "throughput",
        ]
    )
    y = dataset["status"]
    X = dataset.drop(columns=["status"])
    kf = KFold(n_splits=4, shuffle=True, random_state=42)

    best_model = None
    best_accuracy = 0

    for train_index, test_index in kf.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        clf = DecisionTreeClassifier()
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)

        if acc > best_accuracy:
            best_accuracy = acc
            best_model = clf

    joblib.dump(best_model, MODEL_PATH)
    print(f"Best fold accuracy: {best_accuracy:.4f}")


async def predict(cpu, mem, resp, avail, rtt, latency):
    clf = joblib.load(MODEL_PATH)
    X = np.array([[cpu, mem, resp, avail, rtt, latency]])
    print(">>> ", clf.predict(X))
    return int(clf.predict(X)[0])
