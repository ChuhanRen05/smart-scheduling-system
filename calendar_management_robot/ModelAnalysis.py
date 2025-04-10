import os
import numpy as np
from sklearn . model_selection import train_test_split
from nltk . corpus import stopwords
from sklearn . feature_extraction . text import TfidfVectorizer
from sklearn . feature_extraction . text import TfidfTransformer
from sklearn . linear_model import LogisticRegression
from sklearn . metrics import accuracy_score , f1_score , confusion_matrix
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.pipeline import make_pipeline
from scipy.stats import kruskal
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
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

classifiers = {
    "Multinomial Naive Bayes": MultinomialNB(),
    "Logistic Regression": LogisticRegression(random_state=0),
    "Support Vector Machine": SVC(random_state=0),
    "Decision Trees": DecisionTreeClassifier(random_state=0),
    "Random Forest": RandomForestClassifier(random_state=0)
}

kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state= 42)
acc_classifier = {}
for name, classifier in classifiers.items():

    pipeline = make_pipeline(TfidfVectorizer(stop_words='english'), classifier)
    scores = cross_val_score(pipeline, data, labels, cv=kfold, scoring='accuracy')
    acc_classifier[name] = scores
    print(f"{name}")
    print(" Cross-validation score:", scores)
    print(" Average accuracy:", np.mean(scores))
    print()

df = pd.DataFrame(acc_classifier)
df_long = pd.melt(df, var_name='Classifier', value_name='Accuracy')

sns.boxplot(x='Classifier', y="Accuracy", data = df_long)
plt.title('Cross-Validation Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Classifier')
plt.show()
