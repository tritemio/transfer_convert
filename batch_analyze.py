#!/usr/bin/env python

from pathlib import Path
from multiprocessing import Pool

import nbrun

default_notebook_name = 'smFRET-Quick-Test-Server.ipynb'


def get_file_list(folder, init_filelist=None):
    folder = Path(folder)
    if init_filelist is None:
        init_filelist = []
    return [f for f in folder.glob('**/*.hdf5')
            if not f.stem.endswith('_cache')]


def run_notebook(data_filename, input_notebook=None):
    if input_notebook is None:
        input_notebook = default_notebook_name
    nbrun.run_notebook(input_notebook,
                       out_notebook_path=data_filename.with_suffix('ipynb'),
                       nb_kwargs={'fname': data_filename})


def batch_process(folder, nproc=4, notebook=None):
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
            pool.starmap(run_notebook, [(f, notebook) for f in filelist])
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
    args = parser.parse_args()

    folder = Path(args.folder)
    assert folder.is_dir(), 'Path not found: %s' % folder
    batch_process(folder, nproc=args.num_processes, notebook=args.notebook)
    print('Batch analysis completed.', flush=True)
