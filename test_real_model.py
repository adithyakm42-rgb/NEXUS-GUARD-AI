
import joblib
import pandas as pd

# Load the trained model
bundle = joblib.load("nexus_model_real.pkl")

model = bundle["model"]
features = bundle["features"]

# Four test scenarios
test_cases = pd.DataFrame([
    {
        "cpu_usage": 3.0,
        "memory_usage": 80.4,
        "disk_usage": 88.0,
        "upload_mbps": 0.002,
        "download_mbps": 0.003
    },
    {
        "cpu_usage": 25.0,
        "memory_usage": 84.0,
        "disk_usage": 88.0,
        "upload_mbps": 0.5,
        "download_mbps": 1.0
    },
    {
        "cpu_usage": 98.0,
        "memory_usage": 99.0,
        "disk_usage": 99.0,
        "upload_mbps": 50.0,
        "download_mbps": 100.0
    },
    {
        "cpu_usage": 5.0,
        "memory_usage": 80.0,
        "disk_usage": 88.0,
        "upload_mbps": 100.0,
        "download_mbps": 150.0
    }
])

test_cases = test_cases[features]

predictions = model.predict(test_cases)
scores = model.decision_function(test_cases)

print("\nNEXUS GUARD AI - REAL MODEL TEST")
print("--------------------------------")

for i in range(len(test_cases)):
    status = "NORMAL" if predictions[i] == 1 else "ANOMALY"

    print(f"\nTest Case: {i + 1}")
    print(test_cases.iloc[i].to_dict())
    print("AI RESULT:", status)
    print("ANOMALY SCORE:", round(scores[i], 4))

print("\nMODEL TEST COMPLETED")
