import pickle
from textTokenize import tokenize_sentence
# Load the sentiment_model generated in sentimentModelTraining.py
with open('sentiment_model.pkl', 'rb') as file:
    clf = pickle.load(file)

# Load CountVectorizer
with open('count_vectorizer.pkl', 'rb') as file:
    count_vect = pickle.load(file)

# Load TfidfTransformer
with open('tfidf_transformer.pkl', 'rb') as file:
    tfidf_transformer = pickle.load(file)


def predict_user_feeling_positive(user_input):
    preprocessed_text = user_input
    text_vector = count_vect.transform([preprocessed_text])
    text_tfidf = tfidf_transformer.transform(text_vector)
    predicted = clf.predict(text_tfidf)
    if predicted[0] == "positive":
        return True
    else:
        return False