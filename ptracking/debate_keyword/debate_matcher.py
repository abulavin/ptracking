from ptracking.database import cursor
from datetime import timedelta
import pandas as pd

class DebateKeyword:
    def __init__(self, lda_model, num_words) -> None:

        self.words_per_topic = dict()

        for k in range(lda_model.k):
            self.words_per_topic["topic_"+str(k)] = list(map(lambda x: x[0],lda_model.get_topic_words(k, top_n=num_words)))

    def _getProminentTopics(self, topics, petitionID, threshold):
            return dict(filter(lambda elem: elem[1] >= threshold, topics.loc[petitionID].to_dict().items()))

    def _select_scores(self, topics, petition, threshold, weeksBefore, weeksAfter):
        with cursor() as curr:
            curr.execute("select created_at from petition where petition_id = %s", (int(petition),))
            created_at = curr.fetchone()[0]

            start = created_at - timedelta(weeks=weeksBefore)
            end = created_at + timedelta(weeks=weeksAfter)
            prominent_topics = self._getProminentTopics(topics, petition, threshold)
            no_similar_debates = 0

            for topic in prominent_topics:
                words = self.words_per_topic[topic]
                curr.execute("select count(*) from debate where date between %s and %s and debate ==> %s",(start,end,' '.join(words)))
                no_similar_debates += curr.fetchone()[0]
        
        return no_similar_debates

    def addDebateFeature(self, topics, threshold, weeksBefore, weeksAfter):
        rows = []
        for petition_id in topics.index.values[0:10]:
            rows.append((petition_id, self._select_scores(topics, petition_id, threshold, weeksBefore, weeksAfter)))
        
        columns = ["petition_id","debates"]
        df = pd.DataFrame(rows, columns=columns)
        df.set_index('petition_id', inplace=True)
        return df