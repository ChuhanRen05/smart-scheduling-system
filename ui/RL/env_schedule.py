# ✅ env_schedule.py
import numpy as np
from gymnasium import Env
from gymnasium.spaces import MultiDiscrete

class ScheduleEnv(Env):
    def __init__(self, df, activity_map):
        self.df = df
        self.activity_map = activity_map
        self.inverse_activity_map = {v: k for k, v in activity_map.items()}
        self.total_hours = 24
        self.max_duration = 4

        self.action_space = MultiDiscrete([len(activity_map), self.max_duration])  # activity + duration idx
        self.observation_space = MultiDiscrete([len(activity_map)] * self.total_hours)

        self.reset()

    def reset(self, *, seed=None, options=None):
        self.current_hour = 0
        self.schedule = np.full(self.total_hours, self.activity_map["None"], dtype=np.int32)
        return self.schedule.copy(), {}

    def step(self, action):
        activity_id, duration_idx = action

        # ✅ 映射为 1~4 小时
        duration = duration_idx + 1

        for _ in range(duration):
            if self.current_hour >= self.total_hours:
                break
            self.schedule[self.current_hour] = activity_id
            self.current_hour += 1

        done = self.current_hour >= self.total_hours
        reward = self.calculate_reward(self.schedule)
        return self.schedule.copy(), reward, done, False, {}

    def calculate_reward(self, schedule: np.ndarray) -> float:
        reward = 0
        sleep_hours = set(range(22, 24)) | set(range(0, 6))  # 夜间时段
        none_count = 0
        sleep_streak = 0
        max_sleep_streak = 0

        for hour, act_id in enumerate(schedule):
            act = self.inverse_activity_map[act_id]

            # 🌙 夜间睡觉加分 / 不睡觉扣分
            if hour in sleep_hours:
                if act == "Sleep":
                    reward += 10
                else:
                    reward -= 5

            # 💤 睡眠连续检测
            if act == "Sleep":
                sleep_streak += 1
                max_sleep_streak = max(max_sleep_streak, sleep_streak)
            else:
                sleep_streak = 0

            # 🧠 时间段奖励逻辑
            if act == "Work" and 9 <= hour < 17:
                reward += 3
            elif act == "Study" and 9 <= hour < 17:
                reward += 3
            elif act == "Gym Workout" and 6 <= hour < 9:
                reward += 4
            elif act == "Gaming":
                reward -= 2
            elif act == "Reading":
                reward += 2
            elif act == "None":
                none_count += 1
                reward += 1
            elif act == "Socializing":
                reward += 2
            elif act == "Meditation":
                reward += 2

        # 🌙 连续睡眠额外奖励
        if max_sleep_streak >= 6:
            reward += 20

        # 🚫 太多空白惩罚
        if none_count > 8:
            reward -= (none_count - 8) * 2

        return reward


# ✅ generate_recommendation()
def generate_recommendation(env, model):
    obs, _ = env.reset()
    done = False
    actions_taken = []

    while not done:
        action, _ = model.predict(obs)
        actions_taken.append((env.current_hour, action))
        obs, _, done, _, _ = env.step(action)

    recommended_schedule = []
    for start_hour, (act_id, duration_idx) in actions_taken:
        duration = duration_idx + 1
        activity = env.inverse_activity_map[act_id]
        recommended_schedule.append({
            "activity": activity,
            "start": start_hour,
            "duration": duration
        })

    return recommended_schedule
