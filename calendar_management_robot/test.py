import asyncio
import websockets
import json
import cosineSimularity
import textTokenize
import tf_idf
import CalendarManagement  # Ensure this is correctly imported
from sentimentClassification import predict_user_feeling_positive
import warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


intents = {
    "greeting": ["Hello", "Hi", "How are you", "Hey", "Thank you"],
    "discover": ["What can you do?",  "may i ask a question"],
    "idendity": ["my name", "Amy", "Jason", "Tenny", "Bob", "my name is"],
    "question": ["what is the average american income", "where is osaka japan", "who is mary matalin married to",
                  "What are", "time"],
    "calender_management": ["calendar", "schedule", "add event", "delete event", "view my schedule",
                             "management system", "date", "meeting", "check", "cancel", "discord", "remove","withdraw",
                             "erase","plan","book","set","show schedule","open", "see"]
}

username = ''

async def handler(websocket):
    global username
    await greeting_message(websocket)

    async for message in websocket:
        data = json.loads(message)
        user_input = data.get('message')
        print("Received message:", user_input)
        tokenized_userinput = textTokenize.tokenize_sentence(user_input)
        intent = intent_matching(tokenized_userinput)
        
        if intent == "greeting":
            await greeting(websocket, tokenized_userinput)
        elif intent == "question":
            await questionAnswering(websocket, tokenized_userinput)
        elif intent == "discover":
            await discover(websocket, tokenized_userinput)
        elif intent == "identity":
            await identity(websocket)
        elif intent == "calendar_management":
            await handle_calendar_management(websocket, username, user_input)
        else:
            await websocket.send("Sorry, I can't understand your question. Please try again.")

async def greeting_message(websocket):
    await websocket.send("Hello! I'm Lee, your personal timetable management robot. What's your name? (Add @ before your name)")
    userinput = await websocket.recv()
    username = getUserName(userinput)
    if username:
        await websocket.send(f"Hello {username}! I'm here to assist you with your event management.")
        await websocket.send("I can help you find a schedule for a specific date or add "
                             "or remove a schedule for a particular day.")
        await websocket.send("I can also answer some general questions. How can I help you today?")
    else:
        await websocket.send("No name provided, please try again.")
def getUserName(userinput):
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

async def questionAnswering(websocket, tokenized_userinput):
    document = "COMP3074-CW1-Dataset.csv"
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

    if most_similar_sentence_index == -1:
        await websocket.send("I'm sorry, I can't seem to find an answer to your question.")
    else:
        answer = textTokenize.get_answer_csv("COMP3074-CW1-Dataset.csv", most_similar_sentence_index)
        await websocket.send(answer)
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
async def handle_calendar_management(websocket, username, user_input):
    # Initialize or get state for first time use management
    # Assuming a dictionary to track state per user/session
    if username not in session_states:
        session_states[username] = {
            "first_time_use": True
        }
    
    first_time_use = session_states[username]["first_time_use"]
    
    # Asynchronous call to process calendar management
    result = await CalendarManagement.main_loop(username, first_time_use, user_input)
    
    # Update session state based on interaction
    session_states[username]["first_time_use"] = False

    # Handle different outcomes based on the result from calendar management
    if result == 0:
        await websocket.send("Goodbye!")
        # Optionally close the WebSocket connection if needed
        # await websocket.close()
    elif result == 1:
        await websocket.send("Exited from the current process. Feel free to start a new conversation.")
    else:
        await websocket.send("Successfully completed the current process! Let's start the next conversation!")
async def discover(websocket, tokenized_userinput):
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
        await websocket.send("I'm sorry, I cannot provide any information on that topic.")
    else:
        response = textTokenize.get_answer_csv("discover.csv", most_similar_sentence_index)
        await websocket.send(response)

session_states = {}
async def start_server():
    async with websockets.serve(handler, "localhost", 8090):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(start_server())
