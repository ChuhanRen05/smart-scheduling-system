import cosineSimularity
import textTokenize
import tf_idf
import re
import CalendarManagement
from sentimentClassification import predict_user_feeling_positive
intents = {
    "greeting": ["Hello", "Hi", "How are you", "Hey", "Thank you"],
    "discover": ["What can you do?",  "may i ask a question"],
    "idendity": ["my name", "Amy", "Jason", "Tenny", "Bob", "my name is"],
    "question": ["hi, how are you doing", "Can eating too fast cause digestive problems", "Does drinking cold water burn more calories",
                  "What are", "time","does","how","Does drinking warm milk really help you sleep","should"],
    "calender_management": ["calendar", "schedule", "add event", "delete event", "view my schedule",
                             "management system", "date", "meeting", "check", "cancel", "discord", "remove","withdraw",
                             "erase","plan","book","set","show schedule","open", "see"]
}
username = ''
def identity():
    global username
    print("Do you want to change user? (press Y to continue current progress, type other things to remain current user)")
    yOrN = input(f"{username}: ")
    if yOrN == 'Y':
        print("Sure! Who's our new friend? (Add @ before your name)")
        userinput = getUserName()
        while True:
            if userinput:
                username = userinput
                print(f"Hello {username}! How can I help you today?")
                break
            else:
                print("No name provided, please try again.")
                userinput = getUserName()
    else:
        print(f"Keep current user. How can I help you {username}")
def discover(tokenized_userinput):
    document = "discover.csv"
    tokenized_document = textTokenize.tokenize_pipeline_csv(document)

    query_tf = tf_idf.compute_tf(tokenized_userinput)

    most_similar_sentence = None
    most_similar_sentence_index = -1
    max_similarity = -1

    for idx, word_list in enumerate(tokenized_document):
        tf = tf_idf.compute_tf(word_list)
        similarity = cosineSimularity.compute_cosine_similarity(query_tf, tf)

        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_sentence = word_list
            most_similar_sentence_index = idx
    if most_similar_sentence_index == -1:
        print("Sorry, I can not provide any idea.")
    else:
        print(textTokenize.get_answer_csv("discover.csv", most_similar_sentence_index))

def greeting(tokenized_userinput):
    document = "greeting-Dataset.csv"
    tokenized_document = textTokenize.tokenize_pipeline_csv(document)

    query_tf = tf_idf.compute_tf(tokenized_userinput)

    most_similar_sentence = None
    most_similar_sentence_index = -1
    max_similarity = -1

    for idx, word_list in enumerate(tokenized_document):
        tf = tf_idf.compute_tf(word_list)
        similarity = cosineSimularity.compute_cosine_similarity(query_tf, tf)

        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_sentence = word_list
            most_similar_sentence_index = idx
    if most_similar_sentence_index == -1:
        print("Sorry, I can't say hi.")
    else:
        print(textTokenize.get_answer_csv("greeting-Dataset.csv", most_similar_sentence_index))
def questionAnswering(tokenized_userinput):
    document = "dataset_QA.csv"
    tokenized_document = textTokenize.tokenize_pipeline_csv(document)

    idf = tf_idf.compute_idf(tokenized_document)
    query_tfidf = tf_idf.compute_tfidf(tokenized_userinput, idf)

    most_similar_sentence = None
    most_similar_sentence_index = -1
    max_similarity = -1

    for idx, word_list in enumerate(tokenized_document):
        tfidf = tf_idf.compute_tfidf(word_list, idf)
        similarity = cosineSimularity.compute_cosine_similarity(query_tfidf, tfidf)

        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_sentence = word_list
            most_similar_sentence_index = idx
    if most_similar_sentence_index == -1 and most_similar_sentence == None:
        print("Sorry, I can't understand your question.")
    else:
        print(textTokenize.get_answer_csv("dataset_QA.csv", most_similar_sentence_index))
def greeting_message():
    print("Hello! I'm Lee, your personal timetable management robot. What's your name? (Add @ before your name)")
    matches = getUserName()
    while True:
        if matches:
            global username
            username = matches
            print(f"Hello {username}! I'm here to assist you with your event management.")
            print("I can help you find a schedule for a specific date or add "
                    "or remove a schedule for a particular day.")
            print("I can also answer some general questions. How can I help you today?")
            break
        else:
            print("No name provided, please try again.")
            matches = getUserName()
def getUserName():
    userinput = input("User: ")
    pattern = r'@(\w+)'
    matches = re.findall(pattern, userinput)
    if matches:
        return matches[0]
    else:
        return False
def intent_matching(tokenized_userinput):
    max_similarity = -1
    matched_intent = None

    for intent, examples in intents.items():
        query_tf = tf_idf.compute_tf(tokenized_userinput)
        for example in examples:
            preprocessed_example = textTokenize.tokenize_sentence(example)
            tf = tf_idf.compute_tf(preprocessed_example)
            similarity = cosineSimularity.compute_cosine_similarity(query_tf, tf)

            if similarity > max_similarity:
                max_similarity = similarity
                matched_intent = intent
    if max_similarity < 0.3:
        return "sorry"
    return matched_intent


def main():
    global username
    greeting_message()
    first_time_use_management = True
    while True:

        userInput = input(f"{username}: ")
        if userInput.lower() == "exit" or userInput.lower() == "quit":
            print("Goodbye!")
            break
        tokenized_userinput = textTokenize.tokenize_sentence(userInput)
        intent = intent_matching(tokenized_userinput)
        if intent == "greeting":
            greeting(tokenized_userinput)
        elif intent == "question":
            questionAnswering(tokenized_userinput)
            print("Does the above answer meet your expectations?")
            user_input = input(f"{username}: ")
            if predict_user_feeling_positive(user_input):
                print("Thank you for your reply. It has been very helpful to me.")
            else:
                print("Sorry for not meeting your expectations. I will continue to work hard to improve myself. "
                      "Please continue with the next conversation")
        elif intent == "discover":
            discover(tokenized_userinput)
        elif intent == "sorry":
            print("Sorry, I can't understand your question."
                  "Please try to use 'What is...' or 'I want to see my schedule'")
        elif intent == "calender_management":
            result = CalendarManagement.main_loop(username, first_time_use_management, userInput)
            if first_time_use_management:
                first_time_use_management = False
            if result == 0:
                print("Goodbye!")
                break
            elif result == 1:
                print("Exited from the current process. Feel free to start a new conversation.")
            else:
                print("Successfully completed the current process! Let's start the next conversation!")
        else:
            identity()



if __name__ == "__main__":
    main()
