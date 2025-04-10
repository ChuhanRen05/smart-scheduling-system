import asyncio
import websockets
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import json
import numpy as np

from RL.utils import generate_recommendation, score_user_schedule
from RL.env_schedule import ScheduleEnv
from stable_baselines3 import PPO

# loading model and env
print("📦 Initializing model and environment...")

import pandas as pd
df = pd.read_csv("/Users/nicolesong/smart-scheduling-system/ui/RL/calendar_activity_dataset_1000_rows.csv")
unique_activities = df["Activity Name"].unique().tolist()
for extra in ["Sleep", "Free"]:
    if extra not in unique_activities:
        unique_activities.append(extra)

activity_map = {name: i for i, name in enumerate(unique_activities)}
df["Activity Code"] = df["Activity Name"].map(activity_map)

base_env = ScheduleEnv(df, activity_map)
model = PPO.load("/Users/nicolesong/smart-scheduling-system/ui/RL/ppo_schedule_model.zip", env=base_env)

print("✅ Model loaded and ready.")

async def handle_request(websocket):
    try:
        async for message in websocket:
            print("📨 Received:", message, flush=True)
            data = json.loads(message)

            if data["type"] == "score":
                # getting user's agenda
                user_schedule = data["events"]  # [{hour: 9, activity: "Work"}, ...]
                score = score_user_schedule(base_env, user_schedule)
                await websocket.send(json.dumps({
                    "type": "score_result",
                    "score": score
                }))

            elif data["type"] == "recommend":
                # return recommended shedule
                rec = generate_recommendation(base_env, model)
                await websocket.send(json.dumps({
                    "type": "recommend_result",
                    "schedule": rec
                }))

            await websocket.send("[END]")

    except websockets.exceptions.ConnectionClosed:
        print("❌ Client disconnected")
    except Exception as e:
        print(f"💥 Error: {e}")

async def main():
    print("🚀 WebSocket server starting...")
    async with websockets.serve(handle_request, "0.0.0.0", int(os.environ.get('PORT', 8090))):
        print("✅ Server running on port 8090")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
