import pickle
import cosineSimularity
import textTokenize
import tf_idf

activity = {
    "physical_high_mental_high": [
        "running",
        "high-intensity interval training",
        "competitive sports",
        "martial arts",
        "dance (e.g., hip-hop)"
    ],
    "physical_medium_mental_high": [
        "cycling",
        "brisk walking",
        "hiking",
        "aerobics",
        "playing basketball"
    ],
    "physical_low_mental_high": [
        "solving puzzles",
        "reading",
        "playing chess",
        "watching educational videos",
        "listening to podcasts"
    ],
    "physical_high_mental_medium": [
        "jump rope",
        "kickboxing",
        "dance fitness classes",
        "rowing",
        "rock climbing"
    ],
    "physical_medium_mental_medium": [
        "light jogging",
        "walking",
        "strength training",
        "yoga",
        "playing tennis"
    ],
    "physical_low_mental_medium": [
        "stretching",
        "gardening",
        "casual walking",
        "mindfulness exercises",
        "light reading"
    ],
    "physical_high_mental_low": [
        "running",
        "high-intensity workouts",
        "spinning",
        "sports training",
        "dance classes"
    ],
    "physical_medium_mental_low": [
        "leisurely cycling",
        "slow jogging",
        "walking in nature",
        "gentle yoga",
        "playing casual sports"
    ],
    "physical_low_mental_low": [
        "watching TV",
        "listening to music",
        "casual reading",
        "mindful relaxation",
        "simple crafts"
    ]
}


def activity_grading(start_time, end_time, event):
    # Load the model from the file
    with open('decision_tree_model.pkl', 'rb') as file:
        loaded_model = pickle.load(file)

    start_time = convert_to_minutes(start_time)
    end_time = convert_to_minutes(end_time)
    physical_score = 2
    mental_score = 2
    tokenized_event = textTokenize.tokenize_sentence(event)
    matched_activity = activity_matching(tokenized_event)
    # Example inputs for prediction (replace with actual input values)
    if matched_activity == "physical_high_mental_high":
        physical_score = 3
        mental_score = 3
    elif matched_activity == "physical_medium_mental_high":
        physical_score = 2
        mental_score = 3
    elif matched_activity == "physical_low_mental_high":
        physical_score = 1
        mental_score = 3
    elif matched_activity == "physical_high_mental_medium":
        physical_score = 3
        mental_score = 2
    elif matched_activity == "physical_low_mental_medium":
        physical_score = 1
        mental_score = 2
    elif matched_activity == "physical_high_mental_low":
        physical_score = 3
        mental_score = 1
    elif matched_activity == "physical_medium_mental_low":
        physical_score = 2
        mental_score = 1
    elif matched_activity == "physical_low_mental_low":
        physical_score = 1
        mental_score = 1
    else:
        physical_score = 2
        mental_score = 2

    input_data = [[start_time, end_time, physical_score, mental_score]]

    # Make predictions
    predicted_health_score = loaded_model.predict(input_data)
    print("Your activity's predicted health score is:", predicted_health_score[0],"(from 0 to 100)")


def convert_to_minutes(time_str):
    # Split the time string into hours and minutes
    hours, minutes = map(int, time_str.split(':'))
    # Convert total time into minutes
    total_minutes = hours * 60 + minutes
    return str(total_minutes)


def activity_matching(tokenized_event):
    max_similarity = -1
    matched_activity = None

    for intent, examples in activity.items():
        query_tf = tf_idf.compute_tf(tokenized_event)
        for example in examples:
            preprocessed_example = textTokenize.tokenize_sentence(example)
            tf = tf_idf.compute_tf(preprocessed_example)
            similarity = cosineSimularity.compute_cosine_similarity(query_tf, tf)

            if similarity > max_similarity:
                max_similarity = similarity
                matched_activity = intent
    if max_similarity < 0.3:
        return "sorry"
    return matched_activity




# with open('decision_tree_model.pkl', 'rb') as file:
#     loaded_model = pickle.load(file)
# # Example inputs for prediction (replace with actual input values)
# input_data = [['411', '471', 3, 3]]
#
# # Make predictions
# predicted_health_score = loaded_model.predict(input_data)
#
# print("Predicted Health Score:", predicted_health_score[0])
