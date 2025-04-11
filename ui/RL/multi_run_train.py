import os
from tqdm import tqdm
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import EvalCallback
from env_schedule import ScheduleEnv
import pandas as pd
import numpy as np

# === 加载数据 ===
df = pd.read_csv("calendar_activity_dataset_1000_rows.csv")
unique_activities = df["Activity Name"].unique().tolist()
activity_map = {name: i for i, name in enumerate(unique_activities)}
activity_map["None"] = len(activity_map)  # 添加 None 映射
df["Activity Code"] = df["Activity Name"].map(activity_map)

# === 初始化环境 ===
base_env = ScheduleEnv(df, activity_map)
env = Monitor(base_env)

# === 加载模型 ===
print("⚙️ Creating fresh model with updated observation space...")
model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./logs/tb/")


# === 循环训练 ===
start_run = 6
num_runs = 5
timesteps_per_run = 100_000

for i in tqdm(range(start_run, start_run + num_runs)):
    run_name = f"schedule_run_{i}_0"
    print(f"\n🚀 Training run {i} | tb_log_name={run_name}")

    eval_callback = EvalCallback(
        env,
        best_model_save_path="./logs/",
        log_path="./logs/",
        eval_freq=10_000,
        deterministic=True,
        render=False
    )

    model.learn(
        total_timesteps=timesteps_per_run,
        reset_num_timesteps=False,
        callback=eval_callback,
        tb_log_name=run_name
    )

    model.save("ppo_schedule_model")
    print("✅ Saved: ppo_schedule_model.zip")
