import numpy as np

def score_user_schedule(env, user_events: list[dict]) -> float:
    """
    给用户上传的不完整日程打分（自动补齐空白时段）
    user_events: e.g. [{"hour": 9, "activity": "Work"}, {"hour": 13, "activity": "Gym Workout"}]
    """
    # 1. 初始化完整 24 小时 schedule
    full_schedule = []
    for h in range(24):
        if h < 8 or h >= 22:
            full_schedule.append("Sleep")  # 默认睡觉时间
        else:
            full_schedule.append("Free")   # 默认空白时段

    # 2. 插入用户填入的活动
    for event in user_events:
        hour = event.get("hour")
        act = event.get("activity")
        if 0 <= hour < 24 and act:
            full_schedule[hour] = act

    # 3. 转换为 activity code
    schedule_codes = [env.activity_map.get(a, 0) for a in full_schedule]

    # 4. 设置环境状态并打分
    env.schedule = np.array(schedule_codes, dtype=np.int32)
    score = env._calculate_reward()

    return round(score, 2)


def generate_recommendation(env, model) -> list[dict]:
    """
    使用 RL 模型生成推荐的健康日程
    返回格式：[{ "hour": 0, "activity": "Sleep" }, ...]
    """
    obs, _ = env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs)
        obs, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated

    recommended_schedule = [
        {"hour": h, "activity": env.inverse_activity_map[int(a)]}
        for h, a in enumerate(obs)
    ]
    return recommended_schedule
