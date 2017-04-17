#!/usr/bin/env python

import sys
from pathlib import Path
import time
from multiprocessing import Pool
from functools import partial
import subprocess as sp

import transfer


monitor_path = '/mnt/Antonio/data/manta/'


def get_new_files(folder, init_filelist=None):
    if init_filelist is None:
        init_filelist = []
    return [f for f in folder.glob('**/*.yml')
            if f.with_suffix('.dat').is_file and f not in init_filelist]


def spawn_process(filename):
    cmd = 'python transfer.py "%s"' % filename
    if dry_run:
        cmd += ' --dry-run'
    sp.Popen([cmd], shell=False)


def copy_log(fname, dry_run=False):
    print('Processing finished for "%d"' % fname, flush=True)
    dest = transfer.replace_basedir(fname, transfer.temp_basedir,
                                    transfer.local_archive_basedir)
    transfer.filecopy(fname, dest)


def start_monitoring(folder, dry_run=False):
    assert folder.is_dir(), 'Path not found: %s' % folder
    copy_log = partial(copy_log, dry_run=dry_run)
    title_msg = 'Monitoring %s' % folder.name
    print('\n\n%s' % title_msg)

    init_filelist = get_new_files(folder)

    print('- The following files are present at startup and will be skipped:')
    print(init_filelist)
    print()

    with Pool(processes=4) as pool:
        while True:
            transfer.timestamp()
            for i in range(20):
                time.sleep(3)
                newfiles = get_new_files(folder, init_filelist)
                for newfile in newfiles:
                    pool.apply_async(transfer.process, (newfile, dry_run),
                                     callback=copy_log)


if __name__ == '__main__':
    msg = '1 or 2 command-line arguments expected. Received %d instead.'
    assert 2 <= len(sys.argv) <= 3, msg % (len(sys.argv) - 1)

    if len(sys.argv) == 3:
        assert sys.argv[2] == '--dry-run', 'Second argument can only be "--dry-run".'
        dry_run = True

    folder = Path(sys.argv[1])
    start_monitoring(folder, dry_run)
