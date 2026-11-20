
import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest

# Reproducible training data
np.random.seed(42)

# Simulate normal operating conditions
normal_data = pd.DataFrame({
    "cpu_usage": np.random.normal(10, 5, 1000).clip(0, 40),
    "memory_usage": np.random.normal(83, 2, 1000).clip(75, 90),
    "disk_usage": np.random.normal(87.4, 0.3, 1000).clip(85, 90)
})

# Train anomaly detection model
model = IsolationForest(
    n_estimators=200,
    contamination=0.02,
    random_state=42
)

model.fit(normal_data)

# Save model
joblib.dump(model, "nexus_model.pkl")

print("NEXUS GUARD AI MODEL TRAINED")
print("Training records:", len(normal_data))
print("Model saved successfully: nexus_model.pkl")
