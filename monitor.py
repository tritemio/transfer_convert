#!/usr/bin/env python

import sys
from pathlib import Path
import time
from multiprocessing import Pool

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


def start_monitoring(folder, dry_run=False, nproc=4, inplace=False, analyze=True,
                     remove=True, analyze_kws=None):
    title_msg = 'Monitoring files in folder: %s' % folder.name
    print('\n\n%s' % title_msg)

    init_filelist = get_new_files(folder)

    print('- The following files are present at startup and will be skipped:')
    for f in init_filelist:
        print('  %s' % f)
    print()

    args = [dry_run, inplace, analyze, remove, analyze_kws]
    with Pool(processes=nproc) as pool:
        try:
            while True:
                transfer.timestamp()
                for i in range(20):
                    time.sleep(3)
                    newfiles = get_new_files(folder, init_filelist)
                    for newfile in newfiles:
                        pool.apply_async(transfer.process_int,
                                         [newfile] + args,
                                         callback=complete_task)
                    init_filelist += newfiles
        except KeyboardInterrupt:
            print('\n>>> Got keyboard interrupt.\n', flush=True)
    print('Closing subprocess pool.', flush=True)


def batch_process(folder, dry_run=False, nproc=4, inplace=False, analyze=True,
                  remove=True, analyze_kws=None):
    assert folder.is_dir(), 'Path not found: %s' % folder

    title_msg = 'Processing files in folder: %s' % folder.name
    print('\n\n%s' % title_msg)

    filelist = get_new_files(folder)

    print('- The following files will be processed in batch:')
    for f in filelist:
        print('  %s' % f)
    print()

    args = [dry_run, inplace, analyze, remove, analyze_kws]
    with Pool(processes=nproc) as pool:
        try:
            pool.starmap(transfer.process_int, [[f] + args for f in filelist])
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

    msg = """\
        No processing (copy, conversion, analysis) is perfomed.
        Used for debugging."""
    parser.add_argument('--dry-run', action='store_true', help=msg)

    msg = """\
        Process all the DAT/YML files in the folder (batch-mode). Without
        this option only new files created after the monitor started are
        processed."""
    parser.add_argument('--batch', action='store_true', help=msg)

    msg = "Perform conversion creating an additional temporary HDF5 file."
    parser.add_argument('--tempfile', action='store_true', help=msg)

    parser.add_argument('folder',
                        help='Source folder with files to be processed.')
    parser.add_argument('--num-processes', '-n', metavar='N', type=int, default=4,
                        help='Number of multiprocess workers to use.')
    parser.add_argument('--analyze', action='store_true',
                        help='Run smFRET analysis after files are converted.')
    msg = ("Notebook used for smFRET data analysis. If not specified, the "
           "default is '%s'." % transfer.default_notebook_name)
    parser.add_argument('--notebook', metavar='NB_NAME',
                        default=transfer.default_notebook_name, help=msg)
    parser.add_argument('--working-dir', metavar='PATH', default=None,
                        help='Working dir for the kernel executing the notebook.')
    parser.add_argument('--save-html', action='store_true',
                        help='Save a copy of the smFRET notebooks in HTML.')
    parser.add_argument('--keep-temp-files', action='store_true',
                        help='Do not delete files from temporary work folder.')
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        sys.exit('\nFolder not found: %s\n' % folder)
    elif not folder.is_dir():
        sys.exit('\nYou must provide a folder (not a file) as an argument.\n')
    analyze_kws = dict(input_notebook=args.notebook, save_html=args.save_html,
                       working_dir=args.working_dir)
    kwargs = dict(dry_run=args.dry_run, nproc=args.num_processes,
                  inplace=not args.tempfile, analyze=args.analyze,
                  remove=not args.keep_temp_files, analyze_kws=analyze_kws)
    if args.batch:
        batch_process(folder, **kwargs)
    else:
        start_monitoring(folder, **kwargs)
    print('Monitor execution end.', flush=True)
