#!/usr/bin/env python

import sys
from pathlib import Path
import time
from multiprocessing import Pool
from functools import partial
from textwrap import dedent

import transfer


def get_new_files(folder, init_filelist=None):
    folder = Path(folder)
    if init_filelist is None:
        init_filelist = []
    return [f for f in folder.glob('**/*.dat')
            if (f.with_suffix('.yml').is_file() and f not in init_filelist)]


def complete_task(fname, dry_run=False):
    print('Completed processing for "%s" (callback)' % fname, flush=True)
    #dest = transfer.replace_basedir(fname, transfer.temp_basedir,
    #                                transfer.local_archive_basedir)
    #transfer.filecopy(fname, dest) # filecopy does not have a dry_run arg


def start_monitoring(folder, dry_run=False):
    title_msg = 'Monitoring %s' % folder.name
    print('\n\n%s' % title_msg)

    init_filelist = get_new_files(folder)

    print('- The following files are present at startup and will be skipped:')
    for f in init_filelist:
        print('  %s' % f)
    print()

    with Pool(processes=4) as pool:
        try:
            while True:
                transfer.timestamp()
                for i in range(20):
                    time.sleep(3)
                    newfiles = get_new_files(folder, init_filelist)
                    for newfile in newfiles:
                        pool.apply_async(transfer.process_int,
                                         (newfile, dry_run),
                                         callback=complete_task)
                    init_filelist += newfiles
        except KeyboardInterrupt:
            print('\n>>> Got keyboard interrupt.\n', flush=True)
    print('Closing subprocess pool.', flush=True)


def batch_process(folder, dry_run=False):
    assert folder.is_dir(), 'Path not found: %s' % folder

    title_msg = 'Monitoring %s' % folder.name
    print('\n\n%s' % title_msg)

    filelist = get_new_files(folder)

    print('- The following files will be processed in batch:')
    for f in filelist:
        print('  %s' % f)
    print()

    with Pool(processes=4) as pool:
        try:
            pool.starmap(transfer.process_int, [(f, dry_run) for f in filelist])
        except KeyboardInterrupt:
            print('\n>>> Got keyboard interrupt.\n', flush=True)
    print('Closing subprocess pool.', flush=True)


if __name__ == '__main__':
    import argparse
    descr = """\
        This script monitors a folder and converts DAT files to Photon-HDF5
        if a metadata YAML file with the same name (except extension) is found
        in the same folder."""
    parser = argparse.ArgumentParser(description=descr, epilog='\n')
    msg_dryrun = """\
        No processing (copy, conversion, analysis) is perfomed.
        Used for debugging."""
    parser.add_argument('--dry-run', action='store_true', help=msg_dryrun)
    msg_batch = """\
        Process all the DAT/YML files in the folder (batch-mode). Without
        this option only new files created after the monitor started are
        processed."""
    parser.add_argument('--batch', action='store_true', help=msg_batch)
    msg_folder = 'Source folder with files to be processed'
    parser.add_argument('folder', help=msg_folder)
    args = parser.parse_args()

    folder = Path(args.folder)
    assert folder.is_dir(), 'Path not found: %s' % folder
    if args.batch:
        batch_process(folder, args.dry_run)
    else:
        start_monitoring(folder, args.dry_run)
    print('Monitor execution end.', flush=True)
