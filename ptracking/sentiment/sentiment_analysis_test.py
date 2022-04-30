import json
import string
import numpy as np

# load json file into object
with open('petition.json') as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

# extract petition details from json object
details = jsonObject['data']['attributes']['background']

# open SentiWordNet
dataset = open('SentiWordNet_3.0.0.txt', 'r')

word_scores = []

# load word scores into array
for i in range(117659):
    line = dataset.readline().split()
    word = line[4].split('#')[0]
    pos_score = line[2]
    neg_score = line[3]

    word_scores.append((word, pos_score, neg_score))

dataset.close()

word_scores = np.asarray(word_scores)

# remove punctuation
details = details.replace(',', '')
details = details.replace('.', '')
details = details.replace('!', '')
details = details.replace('?', '')

petition_words = details.split()

total_pos_score = 0
total_neg_score = 0

# find total positive and negative scores
for word in petition_words:
    location = np.where(word_scores == word)[0]
    if len(location) > 0:
        print("Word", word, "has positive score", word_scores[location[0]][1], "and negative score", word_scores[location[0]][2])
        total_pos_score += float(word_scores[location[0]][1])
        total_neg_score += float(word_scores[location[0]][2])

print("Positive score:", total_pos_score)
print("Negative score:", total_neg_score)
