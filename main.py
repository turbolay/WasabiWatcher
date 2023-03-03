from threading import Thread
from core import core
from stats import stats

if __name__ == '__main__':
    tcore = Thread(target=core)
    tstats = Thread(target=stats)
    tcore.start()
    tstats.start()
    tcore.join()
    tstats.join()