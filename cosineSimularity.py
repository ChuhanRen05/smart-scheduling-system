import math


def compute_cosine_similarity(d1, d2):
    try:
        dot_product = sum(d1[word] * d2[word] for word in d1.keys() if word in d2)
        magnitude1 = math.sqrt(sum(d1[word] ** 2 for word in d1.keys()))
        magnitude2 = math.sqrt(sum(d2[word] ** 2 for word in d2.keys()))
        similarity = dot_product / (magnitude1 * magnitude2)
        return similarity
    except ZeroDivisionError:
        return -1


