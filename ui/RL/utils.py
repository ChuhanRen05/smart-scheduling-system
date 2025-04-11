import numpy as np

# ✅ generate_recommendation()
def generate_recommendation(env, model):
    obs, _ = env.reset()
    done = False
    current_hour_pointer = 0
    recommended_schedule = []

    while not done:
        action, _ = model.predict(obs)
        activity_id, duration_idx = action
        duration = duration_idx + 1
        activity = env.unwrapped.inverse_activity_map[activity_id]


        recommended_schedule.append({
            "activity": activity,
            "start": current_hour_pointer,
            "duration": duration
        })

        obs, _, done, _, _ = env.step(action)
        current_hour_pointer += duration

    return recommended_schedule

def fill_blank(schedule, default="Sleep"):
    filled = []
    for item in schedule:
        new_item = item.copy()
        if new_item["activity"] == "None":
            new_item["activity"] = default
        filled.append(new_item)
    return filled



# ✅ score_user_schedule()
def score_user_schedule(env, user_schedule: list[dict]) -> float:
    """
    将用户 schedule 转为完整 24h 数组，并打分
    user_schedule 格式：[{"activity": str, "start": int, "duration": int}]
    """
    full_schedule = np.full(env.total_hours, env.unwrapped.activity_map["None"], dtype=np.int32)

    for item in user_schedule:
        activity_id = env.unwrapped.activity_map.get(item["activity"], env.unwrapped.activity_map["None"])
        start = item["start"]
        duration = item.get("duration", 1)
        for h in range(start, min(start + duration, env.total_hours)):
            full_schedule[h] = activity_id

    score = env.calculate_reward(full_schedule)
    return round(score, 2)


# recommended = generate_recommendation(env, model)
# recommended = fill_blank(recommended)