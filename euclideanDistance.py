import math

def compute_euclidean_distance(d1, d2):
    all_words = set(d1.keys()).union(set(d2.keys()))
    squared_diff_sum = sum((d1.get(word, 0) - d2.get(word, 0))**2 for word in all_words)
    euclidean_distance = math.sqrt(squared_diff_sum)
    #inverse for similarity
    sim = 1/(euclidean_distance + 1)
    return sim