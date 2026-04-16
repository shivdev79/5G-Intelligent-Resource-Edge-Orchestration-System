import time
import random
import requests

API_URL = "https://fiveg-intelligent-resource-edge.onrender.com/api/orchestrate"

def generate_user():
    user_type = random.choice([0, 1, 2, 3])
    user_id = f"UE-{random.randint(1000, 9999)}"
    
    # 0: IoT Sensor
    # 1: Mobile Video
    # 2: AR/VR
    # 3: Emergency Vehicle
    
    if user_type == 0:
        bandwidth = random.uniform(0.1, 5)
        latency = random.uniform(100, 500)
        task_size = random.uniform(0.1, 2)
        battery = random.uniform(10, 100)
    elif user_type == 1:
        bandwidth = random.uniform(20, 100)
        latency = random.uniform(50, 150)
        task_size = random.uniform(50, 500)
        battery = random.uniform(10, 100)
    elif user_type == 2:
        bandwidth = random.uniform(50, 200)
        latency = random.uniform(5, 20)
        task_size = random.uniform(100, 1000)
        battery = random.uniform(10, 100)
    else: # 3: Emergency Vehicle
        bandwidth = random.uniform(10, 50)
        latency = random.uniform(1, 10)
        task_size = random.uniform(5, 50)
        battery = random.uniform(50, 100)

    # Some realistic variation
    return {
        "user_id": user_id,
        "user_type": user_type,
        "bandwidth_need": bandwidth,
        "latency_tolerance": latency,
        "task_size": task_size,
        "battery_level": battery
    }


def push_traffic():
    print("Starting 5G Traffic Simulator...")
    while True:
        try:
            # Generate 1 to 3 simultaneous requests to simulate varying load
            num_reqs = random.randint(1, 3)
            for _ in range(num_reqs):
                user_req = generate_user()
                response = requests.post(API_URL, json=user_req)
                if response.status_code == 200:
                    dec = response.json()
                    print(f"Sent {user_req['user_id']} ({['IoT', 'Video', 'AR/VR', 'Emergency'][user_req['user_type']]}) -> "
                          f"Allocated: {dec['slice_type']}, {dec['offloading_decision']}")
            
            # Sleep for between 0.5 to 2.5 seconds
            time.sleep(random.uniform(0.5, 2.5))
        except requests.exceptions.ConnectionError:
            print("Backend not available yet. Retrying in 2 seconds...")
            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    push_traffic()
