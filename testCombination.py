import textTokenize
import tf_idf
import binaryTermWeighting

import cosineSimularity
import jaccardIndex
import euclideanDistance
import pandas as pd
def questionAnswering(tokenized_userinput, bow_choice, sim_choice):
    document = "FAQ.csv"
    tokenized_document = textTokenize.tokenize_pipeline_csv(document)
    idf = tf_idf.compute_idf(tokenized_document)

    most_similar_sentence = None
    most_similar_sentence_index = -1
    max_similarity = -1
    if bow_choice == 'tf_idf':
        d1 = tf_idf.compute_tfidf(tokenized_userinput, idf)
    elif bow_choice == 'tf':
        d1 = tf_idf.compute_tf(tokenized_userinput)
    else:
        d1 = binaryTermWeighting.compute_binary_tf(tokenized_userinput)

    for idx, word_list in enumerate(tokenized_document):
        if bow_choice == 'tf_idf':
            d2 = tf_idf.compute_tfidf(word_list, idf)
        elif bow_choice == 'tf':
            d2 = tf_idf.compute_tf(word_list)
        else:
            d2 = binaryTermWeighting.compute_binary_tf(word_list)


        if sim_choice == 'cos':
            similarity = cosineSimularity.compute_cosine_similarity(d1, d2)
        elif sim_choice == 'euclidean':
            similarity = euclideanDistance.compute_euclidean_distance(d1, d2)
        else:
            similarity = jaccardIndex.compute_jaccard_index(d1,d2)


        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_sentence = word_list
            most_similar_sentence_index = idx
    if most_similar_sentence_index == -1 and most_similar_sentence == None:
        return -1
        print("Sorry, I can't understand your question.")
    else:
        return most_similar_sentence_index
        print(textTokenize.get_answer_csv("FAQ.csv", most_similar_sentence_index))

document = "FAQ.csv"
data = pd.read_csv(document)
questions = data['Question']
total = len(questions)
bow_choices = ['tf', 'tf_idf','binary']
non_binary_sim_choices = ['cos','euclidean']
binary_sim_choices = ['jaccard', 'cos', 'euclidean']

for bow_choice in bow_choices:
    if bow_choice == 'binary':
        for binary_sim_choice in binary_sim_choices:
            correct_amount = 0
            for t_idx, question in enumerate(questions):
                tokenized_userinput = textTokenize.tokenize_sentence(question)
                r_idx = questionAnswering(tokenized_userinput, bow_choice, binary_sim_choice)
                if r_idx == t_idx:
                    correct_amount += 1
            result = correct_amount/total
            print(f'{bow_choice}, {binary_sim_choice}: {result}')
    else:
        for non_binary_sim_choice in non_binary_sim_choices:
            correct_amount = 0
            for t_idx, question in enumerate(questions):
                tokenized_userinput = textTokenize.tokenize_sentence(question)
                r_idx = questionAnswering(tokenized_userinput, bow_choice, non_binary_sim_choice)
                if r_idx == t_idx:
                    correct_amount += 1
            result = correct_amount / total
            print(f'{bow_choice}, {non_binary_sim_choice}: {result}')


