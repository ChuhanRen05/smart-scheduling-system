import math
from collections import Counter
#compute tf
def compute_tf(word_list):
    word_counts = Counter(word_list)
    total_words = len(word_list)
    tf = {word: count / total_words for word, count in word_counts.items()}
    return tf
#compute idf
def compute_idf(corpus):
    document_count = len(corpus)
    idf = {}
    all_words = [word for word_list in corpus for word in word_list]
    word_counts = Counter(all_words)
    for word, count in word_counts.items():
        idf[word] = math.log(document_count / count)
    return idf
#compute tf*idf
def compute_tfidf(word_list, idf):
    tf = compute_tf(word_list)
    tfidf = {word: tf[word] * idf[word] for word in tf.keys() if word in idf}
    return tfidf