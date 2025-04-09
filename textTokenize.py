import nltk
import nltk, re, pprint, string
from nltk import word_tokenize , sent_tokenize
from nltk.util import pad_sequence
from nltk.lm import MLE, Laplace
from collections import Counter
from nltk.lm.preprocessing import pad_both_ends, padded_everygram_pipeline
import pandas as pd
def tokenize_pipeline_csv(document):
    data = pd.read_csv(document)
    questions = data['Question']
    tokenized_questions = [word_tokenize(question.lower()) for question in questions]
    return tokenized_questions
def get_answer_csv(document, idx):
    data = pd.read_csv(document)
    answers = data['Answer']
    return answers[idx]

def tokenize_sentence(sentence):
    # nltk.download('punkt')
    # nltk.download('punkt_tab')
    tokenized_sentence = word_tokenize(sentence.lower())
    return tokenized_sentence
def tokenize_sentences(sentences):
    tokenized_sentences = [word_tokenize(sentence.lower()) for sentence in sentences]
    return tokenized_sentences