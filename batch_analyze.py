#!/usr/bin/env python

from pathlib import Path
from multiprocessing import Pool

from analyze import run_analysis, default_notebook_name


def get_file_list(folder, init_filelist=None):
    folder = Path(folder)
    if init_filelist is None:
        init_filelist = []
    return [f for f in folder.glob('**/*.hdf5')
            if not f.stem.endswith('_cache')]


def batch_process(folder, nproc=4, notebook=None, save_html=False, working_dir='./'):
    assert folder.is_dir(), 'Path not found: %s' % folder

    title_msg = 'Processing files in folder: %s' % folder.name
    print('\n\n%s' % title_msg)

    filelist = get_file_list(folder)

    print('- The following files will be processed:')
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
    msg = ("Filename of the analysis notebook. If not specified, the default "
           "notebook is '%s'." % default_notebook_name)
    parser.add_argument('--notebook', metavar='NB_NAME',
                        default=default_notebook_name, help=msg)
    parser.add_argument('--save-html', action='store_true',
                        help='Save a copy of the output notebooks in HTML.')
    parser.add_argument('--working-dir', metavar='PATH', default='./',
                        help='Working dir for the kernel executing the notebook.')
    args = parser.parse_args()

    folder = Path(args.folder)
    assert folder.is_dir(), 'Path not found: %s' % folder
    batch_process(folder, nproc=args.num_processes, notebook=args.notebook,
                  save_html=args.save_html, working_dir=args.working_dir)
    print('Batch analysis completed.', flush=True)
