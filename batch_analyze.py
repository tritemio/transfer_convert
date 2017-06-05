#!/usr/bin/env python

import sys
from pathlib import Path
from multiprocessing import Pool

from analyze import run_analysis, default_notebook_name


def get_file_list(folder, glob='*.hdf5'):
    folder = Path(folder)
    return [f for f in folder.glob(glob)
            if not f.stem.endswith('_cache')]


def batch_process(folder, nproc=4, notebook=None, save_html=False,
                  working_dir='./', interactive=False, glob='*.hdf5'):
    assert folder.is_dir(), 'Path not found: %s' % folder

    title_msg = 'Processing files in folder: %s' % folder.name
    print('\n\n%s' % title_msg)

    if interactive:
        filelist = get_file_selection_from_user(folder, glob=glob)
    else:
        filelist = get_file_list(folder, glob=glob)

    print('\n- The following files will be processed:')
    for f in filelist:
        print('  %s' % f)
    print()

    with Pool(processes=nproc) as pool:
        try:
            pool.starmap(run_analysis,
                         [(f, notebook, save_html, working_dir) for f in filelist])
        except KeyboardInterrupt:
            print('\n>>> Got keyboard interrupt.\n', flush=True)
    print('Closing subprocess pool.', flush=True)


def get_file_selection_from_user(path, glob='*.hdf5'):
    """Get file selection interactively from the user."""
    filelist = sorted(get_file_list(path, glob=glob))
    print('Data files in %s:\n' % path)
    for i, f in enumerate(filelist):
        print('  [%d] %s' % (i, f.name), flush=True)
    print("\nChoose the file to analyze (integer, 'all' or ENTER to "
          "finish selection).", flush=True)

    selection_confirmed = False
    while not selection_confirmed:
        selection = []
        while True:
            res = input("Select file to analyze (ENTER to finish): ")
            if res.strip() == '':
                break
            elif res.strip().lower() == 'all':
                selection = filelist
                break
            elif res.isdigit():
                index = int(res)
                if index >= len(filelist):
                    print('Index out of range (max valid value is %d).'
                          % (len(filelist) - 1), flush=True)
                    continue
                newfile = filelist[int(res)]
                if newfile not in selection:
                    selection.append(newfile)
                else:
                    print('File already selected.', flush=True)
            else:
                print("Invalid value: selection must be an integer [0-%d], "
                      "'all' or ENTER." % (len(filelist) - 1), flush=True)
            if len(selection) >= len(filelist):
                break

        if len(selection) == 0:
            print('\nNo file selected, please select at least one file.',
                  flush=True)
            continue

        print('\nFiles selected:')
        for i, f in enumerate(selection):
            print('  [%d] %s' % (i, f.name), flush=True)

        valid_answer = False
        while not valid_answer:
            res = input('Do you want to continue [Yn]: ')
            if res.lower().startswith('y') or res.strip() == '':
                selection_confirmed = True
                valid_answer = True
            elif res.lower().startswith('n'):
                valid_answer = True
    return selection


if __name__ == '__main__':
    import argparse
    descr = """\
        This script executes an analysis notebook on all the HDF5 files
        in the passed folder (excluding files ending with '_cache').
        """
    parser = argparse.ArgumentParser(description=descr, epilog='\n')
    parser.add_argument('folder',
                        help='Source folder with files to be processed.')
    parser.add_argument('--num-processes', '-n', metavar='N', type=int, default=4,
                        help='Number of multiprocess workers to use.')
    msg = ("Notebook used for smFRET data analysis. If not specified, the "
           "default is '%s'." % default_notebook_name)
    parser.add_argument('--notebook', metavar='NB_NAME',
                        default=default_notebook_name, help=msg)
    parser.add_argument('--save-html', action='store_true',
                        help='Save a copy of the output notebooks in HTML.')
    parser.add_argument('--choose-files', action='store_true',
                        help='Select files interactively.')
    msg = ('Working dir for the kernel executing the notebook.\n'
           'By default, uses the folder containing the data files.')
    parser.add_argument('--working-dir', metavar='PATH', default=None, help=msg)
    msg = ("Pattern to select data files to be processed (globbing). "
           "Default is '*.hdf5' (including quotes), which selects all "
           "files with hdf5 extension. To process all the .sm files "
           "use '*.sm'. To process all the hdf5 in the specified folder and "
           "all subfolders use '**/*.hdf5'. The pattern can be anything "
           "accepted by pathlib.Path.glob().")
    parser.add_argument('--glob', metavar='PATTERN', default="'*.hdf5'",
                        help=msg)
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        sys.exit('\nFolder not found: %s\n' % folder)
    elif not folder.is_dir():
        sys.exit('\nYou must provide a folder (not a file) as an argument.\n')

    try:
        batch_process(folder, nproc=args.num_processes, notebook=args.notebook,
                      save_html=args.save_html, working_dir=args.working_dir,
                      interactive=args.choose_files, glob=args.glob[1:-1])
        print('Batch analysis completed.', flush=True)
    except KeyboardInterrupt:
        sys.exit('\n\nExecution terminated.\n')
