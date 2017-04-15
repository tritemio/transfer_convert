#!/usr/bin/env python

import sys
from pathlib import Path
import time

import transfer


monitor_path = '/mnt/Antonio/data/manta/'


def get_new_files(folder, init_filelist=None):
    if init_filelist is None:
        init_filelist = []
    return [f for f in folder.glob('**/*.yml')
            if f.with_suffix('.dat').is_file and f not in init_filelist]


def start_monitoring(folder):
    assert folder.is_dir(), 'Path not found: %s' % folder

    title_msg = 'Monitoring %s' % folder.name
    print('\n\n%s' % title_msg)

    init_filelist = get_new_files(folder)

    print('- The following files are present at startup and will be skipped:')
    print(init_filelist)
    print()

    while True:
        transfer.timestamp()
        for i in range(20):
            time.sleep(3)
            newfiles = get_new_files(folder, init_filelist)
            for newfile in newfiles:
                transfer.process(newfile)


if __name__ == '__main__':
    msg = '1 or 2 command-line argument expected. Received %d instead.'
    assert 2 <= len(sys.argv) <= 3, msg % (len(sys.argv) - 1)

    if len(sys.argv) == 3:
        assert sys.argv[2] == '--dry-run', 'Second argument can only be "--dry-run".'
        dry_run = True

    folder = Path(sys.argv[1])
    start_monitoring(folder)
