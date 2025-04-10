import os
import pickle
from sklearn . model_selection import train_test_split
from nltk . corpus import stopwords
from sklearn . feature_extraction . text import CountVectorizer
from sklearn . feature_extraction . text import TfidfTransformer
from sklearn . linear_model import LogisticRegression
from sklearn . metrics import accuracy_score , f1_score , confusion_matrix
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
label_dir = {
    "positive": "data/positive",
    "negative": "data/negative"
}

data = []
labels = []

for label in label_dir.keys():
    for file in os.listdir(label_dir[label]):
        filepath = label_dir[label] + os.sep + file
        with open(filepath, encoding='utf8', errors = 'ignore', mode='r') as review:
            content = review.read()
            data.append(content)
            labels.append(label)

X_train, X_test, y_train, y_test = train_test_split ( data , labels , stratify = labels, test_size= 0.25, random_state=42)

count_vect = CountVectorizer ( stop_words = stopwords.words('english'))
X_train_counts = count_vect.fit_transform(X_train)
tfidf_transformer = TfidfTransformer(use_idf=True, sublinear_tf=True).fit(X_train_counts)
X_train_tf = tfidf_transformer.transform(X_train_counts)
#Logistic Regression
clf_logRegression = LogisticRegression(random_state=0).fit(X_train_tf, y_train)
X_new_counts = count_vect.transform(X_test)
X_new_tfidf = tfidf_transformer.transform(X_new_counts)

predicted_log = clf_logRegression.predict(X_new_tfidf)
print(confusion_matrix(y_test, predicted_log))
print(accuracy_score(y_test, predicted_log))
print(f1_score(y_test,predicted_log, pos_label='positive'))

# Naive Bayes Classifier
clf_Naive = MultinomialNB()
clf_Naive.fit(X_train_tf, y_train)
predicted_naive = clf_Naive.predict(X_new_tfidf)
print(confusion_matrix(y_test, predicted_naive))
print(accuracy_score(y_test, predicted_naive))
print(f1_score(y_test,predicted_naive, pos_label='positive'))

# Support Vector Machines
clf_svc = SVC(random_state=0)
clf_svc.fit(X_train_tf, y_train)
predicted_svc = clf_svc.predict(X_new_tfidf)
print(confusion_matrix(y_test, predicted_svc))
print(accuracy_score(y_test, predicted_svc))
print(f1_score(y_test,predicted_svc, pos_label='positive'))

# Decision Trees
clf_decisionTree = DecisionTreeClassifier(random_state=0)
clf_decisionTree.fit(X_train_tf, y_train)
predicted_dt = clf_decisionTree.predict(X_new_tfidf)
print(confusion_matrix(y_test, predicted_dt))
print(accuracy_score(y_test, predicted_dt))
print(f1_score(y_test,predicted_dt, pos_label='positive'))

# Random Forest
clf_rf = RandomForestClassifier(random_state=0)
clf_rf.fit(X_train_tf, y_train)
predicted_rf = clf_rf.predict(X_new_tfidf)
print(confusion_matrix(y_test, predicted_rf))
print(accuracy_score(y_test, predicted_rf))
print(f1_score(y_test,predicted_rf, pos_label='positive'))

# store the Navie Bayes model
with open('sentiment_model.pkl', 'wb') as file:
    pickle.dump(clf_Naive, file)

# store the CountVectorizer
with open('count_vectorizer.pkl', 'wb') as file:
    pickle.dump(count_vect, file)

# store the TfidfTransformer
with open('tfidf_transformer.pkl', 'wb') as file:
    pickle.dump(tfidf_transformer, file)