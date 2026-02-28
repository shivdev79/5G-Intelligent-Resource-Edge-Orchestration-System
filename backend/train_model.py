import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.multioutput import MultiOutputClassifier
import joblib

# Synthetic Data Generation
NUM_SAMPLES = 5000

# Features:
# 1. user_type (0: IoT, 1: Mobile Video, 2: AR/VR, 3: Emergency)
# 2. bandwidth_need (Mbps)
# 3. latency_tolerance (ms)
# 4. task_size (MB)
# 5. battery_level (%)

# Targets:
# 1. slice_type (0: eMBB, 1: URLLC, 2: mMTC)
# 2. offloading_decision (0: Local, 1: Edge, 2: Cloud)
# 3. resource_allocation (1-100 %)

data = []

for _ in range(NUM_SAMPLES):
    user_type = random.choice([0, 1, 2, 3])
    
    if user_type == 0:  # IoT Sensor
        bandwidth = random.uniform(0.1, 5)
        latency = random.uniform(100, 500)
        task_size = random.uniform(0.1, 2)
        battery = random.uniform(10, 100)
        
        slice_target = 2  # mMTC
        offload_target = 2 if battery < 50 else 0  # Cloud if low battery, Local if decent
        allocation = random.uniform(1, 10)
        
    elif user_type == 1:  # Mobile Video
        bandwidth = random.uniform(20, 100)
        latency = random.uniform(50, 150)
        task_size = random.uniform(50, 500)
        battery = random.uniform(10, 100)
        
        slice_target = 0  # eMBB
        offload_target = 1 if latency < 100 else 2  # Edge if latency sensitive, else Cloud
        allocation = random.uniform(20, 50)
        
    elif user_type == 2:  # AR/VR
        bandwidth = random.uniform(50, 200)
        latency = random.uniform(5, 20)
        task_size = random.uniform(100, 1000)
        battery = random.uniform(10, 100)
        
        slice_target = 0  # eMBB
        offload_target = 1  # Always Edge for AR/VR
        allocation = random.uniform(40, 80)
        
    else:  # Emergency Vehicle (URLLC)
        bandwidth = random.uniform(10, 50)
        latency = random.uniform(1, 10)
        task_size = random.uniform(5, 50)
        battery = random.uniform(50, 100)
        
        slice_target = 1  # URLLC
        offload_target = 1  # Always Edge for ultra low latency
        allocation = random.uniform(10, 30)

    # Add some noise to make model learn generalizing
    allocation = min(100, max(1, allocation + random.uniform(-5, 5)))
    
    data.append([
        user_type, bandwidth, latency, task_size, battery,
        slice_target, offload_target, allocation
    ])

df = pd.DataFrame(data, columns=[
    'user_type', 'bandwidth', 'latency', 'task_size', 'battery',
    'slice_type', 'offloading_decision', 'resource_allocation'
])

# Features and Targets
X = df[['user_type', 'bandwidth', 'latency', 'task_size', 'battery']]
y_class = df[['slice_type', 'offloading_decision']]
y_reg = df['resource_allocation']

# Train-Test Split
X_train, X_test, y_class_train, y_class_test, y_reg_train, y_reg_test = train_test_split(
    X, y_class, y_reg, test_size=0.2, random_state=42
)

# Train Classifier for Slice and Offloading
clf = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42))
clf.fit(X_train, y_class_train)

# Train Regressor for Resource Allocation
reg = RandomForestRegressor(n_estimators=100, random_state=42)
reg.fit(X_train, y_reg_train)

print(f"Classification Score: {clf.score(X_test, y_class_test)}")
print(f"Regression Score: {reg.score(X_test, y_reg_test)}")

# Save Models
joblib.dump(clf, 'orchestration_classifier.joblib')
joblib.dump(reg, 'orchestration_regressor.joblib')

print("Models saved successfully to orchestration_classifier.joblib and orchestration_regressor.joblib")
