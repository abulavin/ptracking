from ptracking.database import cursor
import gensim.corpora as corpora
from gensim.models import TfidfModel
from gensim.models import LdaMulticore
import tomotopy as tp
from pprint import pprint
from pytrends.request import TrendReq
import matplotlib.pyplot as plt
import pandas
import datetime
import numpy as np
import sys

from ptracking.topic.lda import topics
from ptracking.topic.lda_tomoto import tomoto_topics


def main():

    # generate LDA model and topic model
    topic_model, lda_model = tomoto_topics(30, 100)

    # set up trend search
    pytrends = TrendReq(hl='en-UK', tz=0)

    # start and end dates
    sdate = '2010-01-01'
    edate = '2022-03-01'

    # obtain dates and scores
    dates, scores = trend_scores(lda_model, sdate, edate, pytrends)

    with cursor() as cur:
        cur.execute("SELECT petition_id FROM petition WHERE state = 'closed'")
        content = cur.fetchall()

    with open('scores.txt', 'w') as f:
        sys.stdout = f

        for i in range(len(content)):
            print(content[i][0], "      ", get_relevance_score(content[i][0], lda_model, topic_model, dates, scores))

    # grab a random petition
    # petition_id = get_random_petition()

    # find relevance score for random petition
    # print(get_relevance_score(petition_id, lda_model, topic_model, dates, scores))

def get_relevance_score(petition_id, lda_model, topic_model, dates, scores):

    # collect information about petition with given id
    with cursor() as cur:
        query = "SELECT petition_id, created_at, signatures FROM petition WHERE petition_id = " + str(petition_id)
        cur.execute(query)
        content = cur.fetchall()

    # take signature count and creation date
    signature_count = [signatures for _, _, signatures in content]
    created_at = [date for _, date, _ in content]

    # create arrays for years and months
    years = dates.astype('datetime64[Y]').astype(int) + 1970
    months = dates.astype('datetime64[M]').astype(int) % 12 + 1

    # find topic weights for petition
    petition_topics = topic_model.loc[petition_id].to_numpy()

    # find timepoint for date at which petition was created
    for i in range(len(dates)):
        if created_at[0].year == years[i] and created_at[0].month == months[i]:
            timepoint_id = i

    # generate relevance score by looping through all topics and multiplying its weight by the relative search frequency
    relevance_score = 0
    for i in range(10):
        #print("Topic", i, "had weight", petition_topics[i], "and relative search frequency", scores[i][timepoint_id],", giving a contribution of", petition_topics[i] * scores[i][timepoint_id])
        relevance_score += petition_topics[i] * scores[i][timepoint_id]

    return relevance_score

def get_random_petition():

    # get petition ids for all closed petitions
    with cursor() as cur:
        cur.execute("SELECT petition_id FROM petition WHERE state = 'closed'")
        content = cur.fetchall()

    # choose a random petition id
    rand_petition_id = np.random.choice(np.transpose(content)[0])

    # return information
    return rand_petition_id

def trend_scores(lda_model, sdate, edate, pytrends):
    # generate list of dates
    dates = pandas.date_range(sdate,edate,freq='MS').to_numpy()

    # set up plot
    plt.style.use('ggplot')
    plt.ylabel('Relative Search Frequency')
    plt.xlabel('Date')

    # create timeframe
    timeframe = sdate + ' ' + edate

    # colours for plots
    #colours = ['red', 'green', 'blue']
    topic_scores = np.zeros([10, len(dates)])

    # first 3 topics
    for i in range(10):

        keywords = []
        weights = []

        # take each keyword and its weight from lda model
        for keyword in lda_model.show_topic(i):
            keywords.append(keyword[0])
            weights.append(keyword[1])

        # take first 5 (google trends only supports up to 5 at a time)
        keywords = keywords[:5]
        weights = weights[:5]

        # generate payload and extract data
        pytrends.build_payload(keywords, cat=0, timeframe=timeframe)
        data = pytrends.interest_over_time()

        # find scores for each topic
        scores = []
        for j in range(len(data)):
            score = 0
            for k in range(4):
                score += (data.iloc[j][k] * weights[k])
            scores.append(score)
            topic_scores[i][j] = score

        # plot data
        plt.plot(dates, scores)

    #plt.show()

    return dates, topic_scores

if __name__ == '__main__':
    main()
