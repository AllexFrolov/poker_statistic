import os
from .statistic import Statistic
from .utils import wait_for_it

__all__ = [
    'Statistic',
    'wait_for_it'
    ]


DB_PARAMS = {
    'host': os.environ['POSTGRES_HOST'],
    'port': os.environ['POSTGRES_PORT'],
    'user': os.environ['POSTGRES_USER'],
    'password': os.environ['POSTGRES_PASSWORD'],
    'database': os.environ['POSTGRES_DB']
}

STATS = wait_for_it(DB_PARAMS)
