import tomotopy as tp
from ptracking.database import Fetcher
import pandas as pd
import os

def tomoto_topics(n, iterations, tw=tp.TermWeight.IDF, rm_top=0, gvmt_period='all'):
    res = Fetcher.select_columns("processed_content", gvmt_period=gvmt_period)
    model = tp.LDAModel(k=n, tw=tw, rm_top=rm_top)
    docs = res['processed_content'].to_list()

    for text in docs:
        model.add_doc(text)

    print("Topic Model Training...\n\n")

    iterations = iterations
    for i in range(0, 100):
        model.train(iterations)
        print(f'Iteration: {i}\tLog-likelihood: {model.ll_per_word}')
    
    rows = []
    
    for petition_id, doc in zip(list(res.index.values),model.docs):
        rows.append((petition_id, *doc.get_topic_dist()))

    columns = ["petition_id"] + ["topic_" + str(i) for i in range(model.k)]
    df = pd.DataFrame(rows, columns=columns)
    df.set_index('petition_id', inplace=True)
    return df, model

def tomoto_load_model(gvmt_period='first'):
    file = os.path.dirname(__file__)
    if gvmt_period == 'first':
        model = tp.LDAModel.load(file+"/models/first.mdl")
    elif gvmt_period == 'second':
        model = tp.LDAModel.load(file+"/models/second.mdl")
    elif gvmt_period == 'third':
        model = tp.LDAModel.load(file+"/models/third.mdl")
    else:
        model = tp.LDAModel.load(file+"/models/fourth.mdl")

    res = Fetcher.select_columns("processed_content", gvmt_period=gvmt_period)

    rows = []
    
    for petition_id, doc in zip(list(res.index.values),model.docs):
        rows.append((petition_id, *doc.get_topic_dist()))

    columns = ["petition_id"] + ["topic_" + str(i) for i in range(model.k)]
    df = pd.DataFrame(rows, columns=columns)
    df.set_index('petition_id', inplace=True)
    return df, model
