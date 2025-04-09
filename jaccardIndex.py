
def compute_jaccard_index(d1, d2):
    set1 = set(d1.keys())
    set2 = set(d2.keys())
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    jaccard_index = len(intersection) / len(union)
    return jaccard_index
