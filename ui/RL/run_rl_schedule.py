import os
import pandas as pd
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor 
from tqdm import tqdm
from env_schedule import ScheduleEnv 
from utils import generate_recommendation, score_user_schedule, fill_blank


# ========= Load dataset ==========
# ========= Loading csv ==========
df = pd.read_csv("/Users/nicolesong/smart-scheduling-system/ui/RL/calendar_activity_dataset_1000_rows.csv")
unique_activities = df["Activity Name"].unique().tolist()

# ✅ 强制加上 "None" 类型（确保 env 中有占位）
if "None" not in unique_activities:
    unique_activities.append("None")

activity_map = {name: i for i, name in enumerate(unique_activities)}
df["Activity Code"] = df["Activity Name"].map(activity_map)

# Fill out all other hours for user with default setting
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
    # model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./logs/tb/")
    model = PPO("MlpPolicy", env, verbose=1)
    
else:
    print("🆕 Creating new PPO model")
    # model = PPO("MlpPolicy", env, verbose=1)
    model = PPO(
    "MlpPolicy",
    env,
    verbose=1,
    ent_coef=0.01,  # 增加探索倾向

)

# ========= EvalCallback ==========
eval_callback = EvalCallback(
    env,
    # best_model_save_path="./logs/",
    log_path="./logs/",
    eval_freq=5000,
    deterministic=True,
    render=False
)

# ========= Train model ==========
# model.learn(total_timesteps=100000, callback=eval_callback, tb_log_name="schedule_run_1")
# model.save("ppo_schedule_model")

for i in tqdm(range(20)):
    model.learn(
        total_timesteps=5000,
        reset_num_timesteps=False,
        callback=eval_callback,
        # tb_log_name="schedule_run_9"
    )
    model.save("ppo_schedule_model")
    print("✅ Your model is saved as ppo_schedule_model.zip")

# ========= Generate recommended schedule ==========
recommended = generate_recommendation(env, model)
filled_schedule = fill_blank(recommended)  # 可以设为 Sleep / Idle / Nap

# === 打印推荐日程 ===
print("\n📅 推荐日程：")
for item in filled_schedule:
    print(f"{item['start']:02d}:00 → {item['activity']} ({item['duration']}h)")


# ========= Score a sample user schedule ==========
user_schedule = [
    {"activity": "Work", "start": 9, "duration": 2},
    {"activity": "Gym Workout", "start": 13, "duration": 1},
    {"activity": "Gaming", "start": 20, "duration": 1},
]


user_score = score_user_schedule(base_env, user_schedule)
print(f"🧠 用户上传日程得分：{user_score}")

