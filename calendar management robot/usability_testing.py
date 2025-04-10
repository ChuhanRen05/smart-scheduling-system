import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
data = {
    'Question 01': [3, 4, 5, 3, 4],
    'Question 02': [1, 2, 3, 1, 1],
    'Question 03': [5, 5, 5, 4, 5],
    'Question 04': [1, 1, 2, 1, 2],
    'Question 05': [4, 3, 4, 4, 4],
    'Question 06': [1, 1, 2, 1, 1],
    'Question 07': [4, 3, 3, 5, 3],
    'Question 08': [1, 2, 1, 1, 1],
    'Question 09': [3, 3, 3, 4, 3],
    'Question 10': [2, 3, 2, 2, 2],
    'Question 11': [3, 3, 3, 2, 4],
    'Question 12': [3, 2, 2, 3, 3],
    'Question 13': [5, 4, 4, 5, 5],
    'Question 14': [1, 1, 1, 1, 1],
    'Question 15': [4, 5, 4, 4, 4],
    'Question 16': [2, 1, 1, 2, 1],
}
counter = 1
odd = 0
even = 0
result = []
for i in range(len(data["Question 01"])):
    for question, response in data.items():
        if counter == 1:
            odd += response[i]
            counter -= 1
        else:
            even += response[i]
            counter += 1
    result.append(((odd - 8) + (40-even))/64)
    odd = 0
    even = 0
average = sum(result)/len(result)
print(result, average)


df = pd.DataFrame(data)

df_long = df.melt(var_name='Question', value_name='Response')

response_pivot = df_long.pivot_table(index='Question', columns='Response', aggfunc=len, fill_value=0)

plt.figure(figsize=(12, 8))
sns.heatmap(response_pivot, annot=True, cmap="YlGnBu", fmt="d")
plt.title(f"Likert Scale Questionnaire Responses (Average: {average})")
plt.ylabel("Question")
plt.xlabel("Response")

plt.show()

