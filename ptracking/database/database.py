import dataclasses
from contextlib import contextmanager
from typing import Callable, Iterable, List

from pandas import DataFrame
from psycopg2 import connect
from ptracking import config
from ptracking.database.models import Petition

__all__ = ["cursor", "Fetcher", "ColumnFetcher"]

ColumnFetcher = Callable[[List[str]], DataFrame]


@contextmanager
def cursor():
    conn = connect(**config['Database'])
    try:
        yield conn.cursor()
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


class Fetcher:

    @classmethod
    def select_columns(self, *columns, gvmt_period='all') -> DataFrame:
        Fetcher.verify_columns(columns)
        with cursor() as curr:
            if gvmt_period == 'first':
                curr.execute(
                    f"SELECT petition_id, {', '.join(columns)} FROM petition WHERE petition_id between 10 and 76138 ORDER BY created_at ASC"
                )
            elif gvmt_period == 'second':
                curr.execute(
                    f"SELECT petition_id, {', '.join(columns)} FROM petition WHERE petition_id between 104309 AND 195680 ORDER BY created_at ASC"
                )
            elif gvmt_period == 'third':
                curr.execute(
                    f"SELECT petition_id, {', '.join(columns)} FROM petition WHERE petition_id between 200000 AND 278636 ORDER BY created_at ASC"
                )
            elif gvmt_period == 'fourth':
                curr.execute(
                    f"SELECT petition_id, {', '.join(columns)} FROM petition WHERE petition_id between 300000 AND 599673 ORDER BY created_at ASC"
                )
            else:
                curr.execute(
                    f"SELECT petition_id, {', '.join(columns)} FROM petition ORDER BY created_at ASC"
                )
            res = curr.fetchall()
            column_names = [col.name for col in curr.description]
        dataset = DataFrame(res, columns=column_names)
        dataset.set_index("petition_id", inplace=True)
        return dataset

    @classmethod
    def verify_columns(self, columns: Iterable[str]):
        if not columns:
            raise ValueError("Must select at least one column in dataset")

        fields = {f.name for f in dataclasses.fields(Petition)}
        not_found = [col for col in columns if col not in fields]
        if not_found:
            raise ValueError(
                f"Cannot select column(s) from database: {', '.join(not_found)}"
            )

    @classmethod
    def number_of_petitions_on_same_day(self):
        stmt = """SELECT closed.petition_id, count(created.petition_id)-1 as n_created FROM petition AS closed 
                    JOIN petition AS created 
                    ON (date_trunc('day', closed.created_at) = date_trunc('day', created.created_at))
                    group by closed.petition_id"""
        with cursor() as curr:
            curr.execute(stmt)
            res = curr.fetchall()
            column_names = [col.name for col in curr.description]
        dataset = DataFrame(res, columns=column_names)
        dataset.set_index("petition_id", inplace=True)
        return dataset
