import math
from collections import Counter

def compute_binary_tf(word_list):
    word_counts = Counter(word_list)
    tf = {word: 1 if count > 0 else 0 for word, count in word_counts.items()}
    return tf

