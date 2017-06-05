#!/usr/bin/env python

import sys
from pathlib import Path
import time
from multiprocessing import Pool

import transfer


def get_new_files(folder, init_filelist=None, glob='**/*.dat'):
    folder = Path(folder)
    if init_filelist is None:
        init_filelist = []
    return [f for f in folder.glob(glob)
            if (f.with_suffix('.yml').is_file() and f not in init_filelist)]


def complete_task(fname, dry_run=False):
    print('Completed processing for "%s" (callback)' % fname, flush=True)


def start_monitoring(folder, dry_run=False, nproc=4, inplace=False,
                     analyze=True, remove=True, analyze_kws=None,
                     singlespot=False):
    title_msg = 'Monitoring files in folder: %s' % folder.name
    print('\n\n%s' % title_msg)

    glob = '*.sm' if singlespot else '*.dat'
    init_filelist = get_new_files(folder, glob=glob)

    print('- The following files are present at startup and will be skipped:')
    for f in init_filelist:
        print('  %s' % f)
    print()

    args = [dry_run, inplace, analyze, remove, analyze_kws, singlespot]
    with Pool(processes=nproc) as pool:
        try:
            while True:
                transfer.timestamp()
                for i in range(20):
                    time.sleep(3)
                    newfiles = get_new_files(folder, init_filelist, glob=glob)
                    for newfile in newfiles:
                        pool.apply_async(transfer.process_int,
                                         [newfile] + args,
                                         callback=complete_task)
                    init_filelist += newfiles
        except KeyboardInterrupt:
            print('\n>>> Got keyboard interrupt.\n', flush=True)
    print('Closing subprocess pool.', flush=True)


def batch_process(folder, dry_run=False, nproc=4, inplace=False, analyze=True,
                  remove=True, analyze_kws=None, singlespot=False):
    assert folder.is_dir(), 'Path not found: %s' % folder

    title_msg = 'Processing files in folder: %s' % folder.name
    print('\n\n%s' % title_msg)

    glob = '*.sm' if singlespot else '*.dat'
    filelist = get_new_files(folder, glob=glob)

    print('- The following files will be processed in batch:')
    for f in filelist:
        print('  %s' % f)
    print()

    args = [dry_run, inplace, analyze, remove, analyze_kws, singlespot]
    with Pool(processes=nproc) as pool:
        try:
            pool.starmap(transfer.process_int, [[f] + args for f in filelist])
        except KeyboardInterrupt:
            print('\n>>> Got keyboard interrupt.\n', flush=True)
    print('Closing subprocess pool.', flush=True)


if __name__ == '__main__':
    import argparse
    descr = """\
        This script converts files in batch to Photon-HDF5.
        It can also monitor a folder for new files and convert them
        on fly as they appear. For each data file there must be a metadata
        YAML file with the same name (extension .yml) in the same folder.
        The metadats file contains all the additional information required to
        create a complete Photon-HDF5 file.
        """
    parser = argparse.ArgumentParser(description=descr, epilog='\n')

    msg = """\
        No processing (copy, conversion, analysis) is perfomed.
        Used for debugging."""
    parser.add_argument('--dry-run', action='store_true', help=msg)

    msg = """\
        Monitor a folder and only convert/process new data files appearing
        after the script is launched. Without this option,
        all the data files in the specified folder will be processed."""
    parser.add_argument('--monitor', action='store_true', help=msg)

    msg = "Perform conversion creating an additional temporary HDF5 file."
    parser.add_argument('--tempfile', action='store_true', help=msg)

    parser.add_argument('folder',
                        help='Source folder with files to be processed.')
    parser.add_argument('--num-processes', '-n', metavar='N', type=int,
                        default=4, help='Number of multiprocess workers to '
                                        'use. Default 4.')
    parser.add_argument('--analyze', action='store_true',
                        help='Run smFRET analysis after files are converted.')
    parser.add_argument('--singlespot', action='store_true',
                        help=('Convert SM files of 1-spot smFRET-usALEX data. '
                              'Without this option, convert DAT files of '
                              ' 48-spot smFRET [pax or 1-laser] data.'))
    msg = ("Notebook used for smFRET data analysis. If not specified, the "
           "default is '%s'." % transfer.default_notebook_name)
    parser.add_argument('--notebook', metavar='NB_NAME',
                        default=transfer.default_notebook_name, help=msg)
    parser.add_argument('--working-dir', metavar='PATH', default=None,
                        help='Working dir for the kernel executing the smFRET '
                             'notebook.')
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
                  inplace=not args.tempfile, singlespot=args.singlespot,
                  analyze=args.analyze, analyze_kws=analyze_kws,
                  remove=not args.keep_temp_files)
    if args.monitor:
        start_monitoring(folder, **kwargs)
    else:
        batch_process(folder, **kwargs)
    print('Monitor execution end.', flush=True)
