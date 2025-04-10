import asyncio
import websockets
import re
import cosineSimularity
import textTokenize
import tf_idf

intents = {
    "greeting": ["Hello", "Hi", "How are you", "Hey", "Thank you"],
    "discover": ["What can you do?", "May I ask a question"],
    "identity": ["my name", "Amy", "Jason", "Tenny", "Bob", "my name is"],
    "question": ["Mental", "illness", "mean", "feel", "hurt", "What can I do?"]
}

username = ''

async def handler(websocket):
    global username
    await greeting_message(websocket)

    async for message in websocket:
        print("Received message:", message)
        tokenized_userinput = textTokenize.tokenize_sentence(message)
        intent = intent_matching(tokenized_userinput)
        
        if intent == "greeting":
            await greeting(websocket, tokenized_userinput)
        elif intent == "question":
            await questionAnswering(websocket, tokenized_userinput)
        elif intent == "discover":
            await discover(websocket, tokenized_userinput)
        elif intent == "identity":
            await identity(websocket)
        else:
            await websocket.send("Sorry, I can't understand your question. Please try again.")

async def greeting_message(websocket):
    #await websocket.send("Hello! I'm Lee, your personal Mental Health robot. What's your name? (Add @ before your name)")

    userinput = await websocket.recv()
    matches = getUserName(userinput)
    if matches:
        global username
        username = matches
        await websocket.send(f"Hello {username}! I'm here to help you.")
        await websocket.send("If you have any questions about mental health, please don't hesitate to ask me.")
        await websocket.send("How can I help you today?")
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
    document = "mentalhealth.csv"
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

    if most_similar_sentence_index == -1 and most_similar_sentence is None:
        await websocket.send("Sorry, I can't understand your question.")
    else:
        answer = textTokenize.get_answer_csv("mentalhealth.csv", most_similar_sentence_index)
        await websocket.send(answer)

async def start_server():
    async with websockets.serve(handler, "localhost", 8090):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(start_server())
