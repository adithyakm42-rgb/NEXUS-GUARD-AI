
import joblib
import pandas as pd

model = joblib.load("nexus_model.pkl")

test_cases = pd.DataFrame([
    {
        "cpu_usage": 10,
        "memory_usage": 83,
        "disk_usage": 87.4
    },
    {
        "cpu_usage": 98,
        "memory_usage": 96,
        "disk_usage": 99
    },
    {
        "cpu_usage": 15,
        "memory_usage": 84,
        "disk_usage": 87.4
    },
    {
        "cpu_usage": 95,
        "memory_usage": 99,
        "disk_usage": 98
    }
])

predictions = model.predict(test_cases)
scores = model.decision_function(test_cases)

for i, prediction in enumerate(predictions):

    status = "NORMAL" if prediction == 1 else "ANOMALY"

    print("\nTest Case:", i + 1)
    print("CPU:", test_cases.iloc[i]["cpu_usage"])
    print("RAM:", test_cases.iloc[i]["memory_usage"])
    print("DISK:", test_cases.iloc[i]["disk_usage"])
    print("AI RESULT:", status)
    print("ANOMALY SCORE:", round(float(scores[i]), 4))
