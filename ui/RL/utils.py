import numpy as np

def score_user_schedule(env, user_events: list[dict]) -> float:
    """
    grading user's incomplete schedule, fill out the rest with default setting
    user_events: e.g. [{"hour": 9, "activity": "Work"}, {"hour": 13, "activity": "Gym Workout"}]
    """
    # initialize 24 hour slot
    full_schedule = []
    for h in range(24):
        if h < 8 or h >= 22:
            full_schedule.append("Sleep")  # default sleep
        else:
            full_schedule.append("Free")   # default free time

    # 2. insert user's input agenda
    for event in user_events:
        hour = event.get("hour")
        act = event.get("activity")
        if 0 <= hour < 24 and act:
            full_schedule[hour] = act

    # 3. convert with activity code
    schedule_codes = [env.activity_map.get(a, 0) for a in full_schedule]

    # 4. set up env and grading
    env.schedule = np.array(schedule_codes, dtype=np.int32)
    score = env._calculate_reward()

    return round(score, 2)


def generate_recommendation(env, model) -> list[dict]:
    # generateds recommended schedule
    # formate：[{ "hour": 0, "activity": "Sleep" }, ...]
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
