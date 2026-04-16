from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import datetime


app = FastAPI()

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State for Metrics
metrics_state = {
    "network_load": 0.0,
    "cloud_load": 0.0,
    "edge_load": 0.0,
    "slice_utilization": {
        "eMBB": 0.0,
        "URLLC": 0.0,
        "mMTC": 0.0
    },
    "recent_decisions": []
}

# Load Models
try:
    clf = joblib.load('orchestration_classifier.joblib')
    reg = joblib.load('orchestration_regressor.joblib')
except Exception as e:
    print(f"Warning: Model files not found. Run train_model.py first. Error: {str(e)}")
    clf = None
    reg = None

class UserRequest(BaseModel):
    user_id: str
    user_type: int  # 0: IoT, 1: Mobile Video, 2: AR/VR, 3: Emergency
    bandwidth_need: float
    latency_tolerance: float
    task_size: float
    battery_level: float

class DecisionResponse(BaseModel):
    slice_type: str
    offloading_decision: str
    resource_allocation: float

slice_map = {0: "eMBB", 1: "URLLC", 2: "mMTC"}
offload_map = {0: "Local", 1: "Edge", 2: "Cloud"}

@app.post("/api/orchestrate", response_model=DecisionResponse)
async def orchestrate(req: UserRequest):
    if clf is None or reg is None:
        raise HTTPException(status_code=500, detail="Models not loaded.")

    # Prepare features
    features = pd.DataFrame([{
        "user_type": req.user_type,
        "bandwidth": req.bandwidth_need,
        "latency": req.latency_tolerance,
        "task_size": req.task_size,
        "battery": req.battery_level
    }])

    # Predict
    class_pred = clf.predict(features)[0]
    slice_idx = int(class_pred[0])
    offload_idx = int(class_pred[1])
    
    resource_alloc = max(0, min(100, float(reg.predict(features)[0])))

    decision = {
        "slice_type": slice_map.get(slice_idx, "Unknown"),
        "offloading_decision": offload_map.get(offload_idx, "Unknown"),
        "resource_allocation": round(resource_alloc, 2)
    }

    # Update state
    _update_metrics(req, decision)

    return decision

def _update_metrics(req: UserRequest, decision: dict):
    # Smooth updates for visual appeal
    decay_factor = 0.95
    
    # Update slice utilization
    metrics_state["slice_utilization"]["eMBB"] *= decay_factor
    metrics_state["slice_utilization"]["URLLC"] *= decay_factor
    metrics_state["slice_utilization"]["mMTC"] *= decay_factor
    
    if decision["slice_type"] in metrics_state["slice_utilization"]:
        metrics_state["slice_utilization"][decision["slice_type"]] += decision["resource_allocation"] * 0.1
        metrics_state["slice_utilization"][decision["slice_type"]] = min(100.0, metrics_state["slice_utilization"][decision["slice_type"]])

    # Update Edge/Cloud loads
    metrics_state["edge_load"] *= decay_factor
    metrics_state["cloud_load"] *= decay_factor
    
    if decision["offloading_decision"] == "Edge":
        metrics_state["edge_load"] += req.task_size * 0.05
        metrics_state["edge_load"] = min(100.0, metrics_state["edge_load"])
    elif decision["offloading_decision"] == "Cloud":
        metrics_state["cloud_load"] += req.task_size * 0.02
        metrics_state["cloud_load"] = min(100.0, metrics_state["cloud_load"])

    # Update total network load
    # Calculate weighted average of slices
    metrics_state["network_load"] = (
        metrics_state["slice_utilization"]["eMBB"] * 0.5 +
        metrics_state["slice_utilization"]["URLLC"] * 0.3 +
        metrics_state["slice_utilization"]["mMTC"] * 0.2
    )

    # Append to recent decisions
    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user_id": req.user_id,
        "user_type_str": ["IoT Sensor", "Mobile Video", "AR/VR", "Emergency"][req.user_type],
        **req.dict(),
        **decision
    }
    
    metrics_state["recent_decisions"].insert(0, record)
    
    # Keep only last 20 records
    if len(metrics_state["recent_decisions"]) > 20:
        metrics_state["recent_decisions"] = metrics_state["recent_decisions"][:20]

@app.get("/api/metrics")
async def get_metrics():
    # Apply time-based decay automatically when requested to simulate dynamic release of resources
    decay = 0.99
    metrics_state["edge_load"] = max(0.0, metrics_state["edge_load"] * decay)
    metrics_state["cloud_load"] = max(0.0, metrics_state["cloud_load"] * decay)
    metrics_state["slice_utilization"]["eMBB"] *= decay
    metrics_state["slice_utilization"]["URLLC"] *= decay
    metrics_state["slice_utilization"]["mMTC"] *= decay
    metrics_state["network_load"] *= decay
    
    return metrics_state

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
