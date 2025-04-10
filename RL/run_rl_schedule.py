import os
import pandas as pd
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor
from env_schedule import ScheduleEnv

# ========= STEP 1: 加载数据 ==========
df = pd.read_csv("/Users/nicolesong/smart-scheduling-system/RL/calendar_activity_dataset_1000_rows.csv")
unique_activities = df["Activity Name"].unique().tolist()
activity_map = {name: i for i, name in enumerate(unique_activities)}
df["Activity Code"] = df["Activity Name"].map(activity_map)

# ========= STEP 2: 环境设置 ==========
base_env = ScheduleEnv(df, activity_map)
env = Monitor(base_env)  # 加上 Monitor，用于记录 reward 日志

# ========= STEP 3: 加载已有模型或新建 ==========
if os.path.exists("ppo_schedule_model.zip"):
    print("📂 加载已有模型 ppo_schedule_model.zip")
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./logs/tb/")
else:
    print("🆕 新建 PPO 模型")
    model = PPO("MlpPolicy", env, verbose=1)

# ========= STEP 4: 设置评估回调 ==========
eval_callback = EvalCallback(
    env,
    best_model_save_path="./logs/",
    log_path="./logs/",
    eval_freq=5000,  # 每 5000 步评估一次
    deterministic=True,
    render=False
)

# ========= STEP 5: 训练模型 ==========
model.learn(total_timesteps=100000, callback=eval_callback, tb_log_name="schedule_run_1")
model.save("ppo_schedule_model")
print("✅ 模型已保存为 ppo_schedule_model.zip")

# ========= STEP 6: 使用训练后的模型进行预测 ==========
obs, _ = env.reset()
done = False
while not done:
    action, _ = model.predict(obs)
    obs, reward, terminated, truncated, _ = env.step(action)
    done = terminated or truncated

# ========= STEP 7: 打印推荐日程 ==========
print("\n📅 推荐日程：")
for hour, act in enumerate(obs):
    act_name = base_env.inverse_activity_map[int(act)]
    print(f"{hour:02d}:00 - {act_name}")

print("\n🧠 健康指数得分：", round(reward, 2))

