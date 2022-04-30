import snscrape.modules.twitter as sntwitter
from multiprocessing import Pool
from ptracking.database.database import Fetcher, cursor
from ptracking.database.models import Tweet
from pandas import DataFrame
from tqdm import tqdm
import dataclasses
from typing import Iterable
import pandas as pd


def _run_imap_multiprocessing(func, argument_list, num_processes=None):
    result_list_tqdm = []

    with Pool(num_processes) as pool:
        for result in tqdm(pool.imap(func=func, iterable=argument_list),
                           total=len(argument_list)):
            result_list_tqdm.append(result)

    return result_list_tqdm


def _get_tweets(petition_id):
    tweets = list()
    old_string = "http://epetitions.direct.gov.uk/petitions/" + str(
        petition_id)
    new_string = "https://petition.parliament.uk/petitions/" + str(petition_id)
    search_string = "(" + old_string + " OR " + new_string + ")"
    for i, tweet in enumerate(
            sntwitter.TwitterSearchScraper(search_string).get_items()):
        # if i>10000:
        #     break
        user = tweet.user
        date = tweet.date
        no_replies = tweet.replyCount
        no_likes = tweet.likeCount
        no_retweets = tweet.retweetCount
        tweets.append((user, date, no_likes, no_retweets, no_replies))

    return tweets


def get_tweets_info_all_petitions():
    data = Fetcher().select_columns('signatures')
    petition_ids = list(data.index.values) 
    result = _run_imap_multiprocessing(_get_tweets, petition_ids, 8)
    out = dict()
    for id, tweets in zip(petition_ids, result):
        out[id] = tweets

    return out


class TwitterFetcher:
    @classmethod
    def select(self, *columns) -> DataFrame:
        TwitterFetcher.verify_columns(columns)
        with cursor() as curr:
            curr.execute(f"SELECT tweet_id, {', '.join(columns)} FROM tweet")
            res = curr.fetchall()
            column_names = [col.name for col in curr.description]
        dataset = DataFrame(res, columns=column_names)
        dataset.set_index("tweet_id", inplace=True)
        return dataset

    @classmethod
    def select_aggregated(self) -> DataFrame:
        data = Fetcher().select_columns('signatures')
        with cursor() as curr:
            curr.execute(
                """SELECT petition_id, count(*) as total_tweets, count(distinct user_id) as individual_users, 
                   sum(likes) as total_likes, sum(retweets) as total_retweets, sum(replies) as total_replies 
                   FROM tweet GROUP BY petition_id"""
            )
            db_keys = curr.fetchall()
            column_names = [col.name for col in curr.description]
            res = pd.DataFrame(db_keys, columns=column_names)
            res.set_index("petition_id", inplace=True)
        res = data.join(res).fillna(0)
        res = res.drop(columns='signatures')
        return res

    def select_distinct_verified(self) -> DataFrame:
        data = Fetcher().select_columns('signatures')
        with cursor() as curr:
            curr.execute(
                """SELECT petition_id, count(distinct user_id) as total_verified 
                from tweet where verified = true group by petition_id"""
            )
            db_keys = curr.fetchall()
            column_names = [col.name for col in curr.description]
            res = pd.DataFrame(db_keys, columns=column_names)
            res.set_index("petition_id", inplace=True)
        res = data.join(res).fillna(0)
        res = res.drop(columns='signatures')
        return res

    def select_most_tweets_in_a_day(self) -> DataFrame:
        data = Fetcher().select_columns('signatures')
        with cursor() as curr:
            curr.execute(
                """select petition_id, max(count) as max_day from 
                (select petition_id, date_trunc('day',created_at), count(*) as count 
                from tweet group by (petition_id, date_trunc('day',created_at))) as foo 
                group by petition_id"""
            )
            db_keys = curr.fetchall()
            column_names = [col.name for col in curr.description]
            res = pd.DataFrame(db_keys, columns=column_names)
            res.set_index("petition_id", inplace=True)
        res = data.join(res).fillna(0)
        res = res.drop(columns='signatures')
        return res

    def get_twitter_features(self) -> DataFrame:
        data1 = self.select_aggregated()
        data2 = self.select_distinct_verified()
        data3 = self.select_most_tweets_in_a_day()
        data = data1.join(data2.join(data3))

        return data

    @classmethod
    def verify_columns(self, columns: Iterable[str]):
        if not columns:
            raise ValueError("Must select at least one column in dataset")

        fields = {f.name for f in dataclasses.fields(Tweet)}
        not_found = [col for col in columns if col not in fields]
        if not_found:
            raise ValueError(
                f"Cannot select column(s) from database: {', '.join(not_found)}"
            )