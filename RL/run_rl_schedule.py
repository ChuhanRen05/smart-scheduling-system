import os
import pandas as pd
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor
from env_schedule import ScheduleEnv

# ========= Loading csv ==========
df = pd.read_csv("/Users/nicolesong/smart-scheduling-system/RL/calendar_activity_dataset_1000_rows.csv")
unique_activities = df["Activity Name"].unique().tolist()
activity_map = {name: i for i, name in enumerate(unique_activities)}
df["Activity Code"] = df["Activity Name"].map(activity_map)

# ========= Set up env ==========
base_env = ScheduleEnv(df, activity_map)
env = Monitor(base_env)  # reward log

# ========= Loading existing model or creat one if there is none ==========
if os.path.exists("ppo_schedule_model.zip"):
    print("Loading your model ppo_schedule_model.zip")
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./logs/tb/")
else:
    print("Creating new model")
    model = PPO("MlpPolicy", env, verbose=1)

# ========= eval call back ==========
eval_callback = EvalCallback(
    env,
    best_model_save_path="./logs/",
    log_path="./logs/",
    eval_freq=5000,  
    deterministic=True,
    render=False
)

# ========= train ==========
model.learn(total_timesteps=100000, callback=eval_callback, tb_log_name="schedule_run_1")
model.save("ppo_schedule_model")
print("Your model is saved ppo_schedule_model.zip")

# ========= user trained model ==========
obs, _ = env.reset()
done = False
while not done:
    action, _ = model.predict(obs)
    obs, reward, terminated, truncated, _ = env.step(action)
    done = terminated or truncated

# ========= print ==========
print("\nYour Recommended Shedule：")
for hour, act in enumerate(obs):
    act_name = base_env.inverse_activity_map[int(act)]
    print(f"{hour:02d}:00 - {act_name}")

print("\nYour Health Score is：", round(reward, 2))

