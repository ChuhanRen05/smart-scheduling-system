import os
import pandas as pd
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor
from env_schedule import ScheduleEnv
from utils import generate_recommendation, score_user_schedule

# ========= Load dataset ==========
# ========= Loading csv ==========
df = pd.read_csv("/Users/nicolesong/smart-scheduling-system/RL/calendar_activity_dataset_1000_rows.csv")
unique_activities = df["Activity Name"].unique().tolist()

# ✅ 补全默认活动
for extra in ["Sleep", "Free"]:
    if extra not in unique_activities:
        unique_activities.append(extra)

activity_map = {name: i for i, name in enumerate(unique_activities)}
df["Activity Code"] = df["Activity Name"].map(activity_map)


# ========= Create env ==========
base_env = ScheduleEnv(df, activity_map)
env = Monitor(base_env)  # wrapped env for training logs

# ========= Load or create model ==========
if os.path.exists("ppo_schedule_model.zip"):
    print("📂 Loading your model: ppo_schedule_model.zip")
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./logs/tb/")
else:
    print("🆕 Creating new PPO model")
    model = PPO("MlpPolicy", env, verbose=1)

# ========= EvalCallback ==========
eval_callback = EvalCallback(
    env,
    best_model_save_path="./logs/",
    log_path="./logs/",
    eval_freq=5000,
    deterministic=True,
    render=False
)

# ========= Train model ==========
model.learn(total_timesteps=100000, callback=eval_callback, tb_log_name="schedule_run_1")
model.save("ppo_schedule_model")
print("✅ Your model is saved as ppo_schedule_model.zip")

# ========= Generate recommended schedule ==========
recommended = generate_recommendation(base_env, model)

print("\n📅 推荐日程：")
for item in recommended:
    print(f"{item['hour']:02d}:00 → {item['activity']}")

# ========= Score a sample user schedule ==========
user_schedule = [
    {"hour": 9, "activity": "Work"},
    {"hour": 10, "activity": "Work"},
    {"hour": 13, "activity": "Gym Workout"},
    {"hour": 20, "activity": "Gaming"},
]

user_score = score_user_schedule(base_env, user_schedule)
print("\n🧠 用户上传日程得分：", user_score)
