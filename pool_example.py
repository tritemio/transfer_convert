"""
Test/mockup for the multiprocessing scheme.
"""

from multiprocessing import Pool
from functools import partial
import time
import sys
import random


def get_new_files():
    print('getting new files ...', flush=True)
    num_files = random.randint(0, 1)
    wait = random.randint(1, 3)
    time.sleep(wait)
    fname = [] if num_files == 0 else [random.randint(1, 10000)]
    print(fname, flush=True)
    return fname


def process(newfile):
    sys.stdout = open("%s.txt" % newfile, "w")
    print(' - Processing %d ...' % newfile, flush=True)
    wait = random.randint(1, 3)
    time.sleep(wait)
    print(' * DONE %d' % newfile, flush=True)
    return newfile


def copy_log(res, dry_run=False):
    print('callback for file %d () dry_run=%s' % (res, dry_run), flush=True)
    with open('%s.txt' % res) as f:
        print(f.readlines(), flush=True)


if __name__ == '__main__':
    dry_run = True
    copy_log = partial(copy_log, dry_run=dry_run)
    # start 4 worker processes
    with Pool(processes=4) as pool:
        for i in range(5):
            time.sleep(1)
            newfiles = get_new_files()
            for newfile in newfiles:
                pool.apply_async(process, (newfile,), callback=copy_log)

        print("For the moment, the pool remains available for more work")

    # exiting the 'with'-block has stopped the pool
    print("Now the pool is closed and no longer available")
