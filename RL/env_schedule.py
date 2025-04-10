import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class ScheduleEnv(gym.Env):
    def __init__(self, df, activity_map):
        super(ScheduleEnv, self).__init__()

        self.df = df
        self.activity_map = activity_map
        self.inverse_activity_map = {v: k for k, v in activity_map.items()}
        self.num_activities = len(activity_map)
        self.hours_per_day = 24

        self.action_space = spaces.Discrete(self.num_activities)
        self.observation_space = spaces.Box(low=0, high=self.num_activities - 1,
                                            shape=(self.hours_per_day,), dtype=np.int32)

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.schedule = np.zeros(self.hours_per_day, dtype=np.int32)
        self.current_hour = 0
        return self.schedule.copy(), {}  # gymnasium 需要返回 observation 和 info（空字典）


    def step(self, action):
        self.schedule[self.current_hour] = action
        self.current_hour += 1

        terminated = self.current_hour == self.hours_per_day
        truncated = False  # 我们暂时不考虑截断

        reward = self._calculate_reward() if terminated else 0
        return self.schedule.copy(), reward, terminated, truncated, {}


    def _calculate_reward(self):
        reward = 0
        work_streak = 0

        def is_sleep(name): return any(k in name.lower() for k in ["sleep", "nap"])
        def is_eat(name): return any(k in name.lower() for k in ["eat", "lunch", "dinner", "meal", "snack"])
        def is_work(name): return any(k in name.lower() for k in ["work", "study"])
        def is_exercise(name): return any(k in name.lower() for k in ["gym", "workout", "run", "walk", "yoga", "cycling"])
        def is_break(name): return any(k in name.lower() for k in ["meditation", "rest", "free", "social", "read", "break"])
        def is_gaming(name): return "gaming" in name.lower()

        print("\n📋 Schedule Evaluation:")

        for hour in range(self.hours_per_day):
            act = self.schedule[hour]
            act_name = self.inverse_activity_map[int(act)]
            hour_reward = 0

            # 睡觉奖励
            if is_sleep(act_name):
                if 21 <= hour or hour < 7:
                    hour_reward += 10
                else:
                    hour_reward += 2

            # 吃饭奖励
            elif is_eat(act_name):
                if abs(hour - 12) <= 1 or abs(hour - 18) <= 1:
                    hour_reward += 5
                else:
                    hour_reward += 1

            # 工作惩罚（连续工作超过 4 小时）
            elif is_work(act_name):
                work_streak += 1
                if work_streak > 4:
                    hour_reward -= 8
            else:
                work_streak = 0

            # 运动奖励
            if is_exercise(act_name):
                if 6 <= hour <= 9:
                    hour_reward += 6
                else:
                    hour_reward += 2

            # 空档奖励
            if is_break(act_name):
                hour_reward += 3

            # 游戏奖励惩罚（鼓励适量）
            if is_gaming(act_name):
                if 18 <= hour <= 22:
                    hour_reward += 1  # 晚上玩一点 OK
                else:
                    hour_reward -= 2  # 白天玩惩罚

            # 基础探索奖励
            if hour_reward == 0:
                hour_reward += 0.2

            print(f"{hour:02d}:00 → {act_name:<15} | reward: {hour_reward:.2f}")
            reward += hour_reward

        final_score = reward / self.hours_per_day
        print(f"\n🎯 Final health score: {final_score:.2f}")
        return final_score
