import time
from .statistic import Statistic

def wait_for_it(db_params: dict) -> Statistic:
    """wait connect to db"""
    exeption = None
    for _ in range(10):
        try:
            stats = Statistic(db_params)
            return stats
        except ConnectionError as e:
            time.sleep(2)
            exeption = e

    raise ConnectionError(exeption)
