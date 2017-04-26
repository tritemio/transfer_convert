#!/usr/bin/env python

import sys
import os
from pathlib import Path
import subprocess as sp
import time

from nbrun import run_notebook


convert_notebook_name = 'Convert to Photon-HDF5 48-spot smFRET from YAML - tempfile.ipynb'
# convert_notebook_name = 'Convert to Photon-HDF5 48-spot smFRET from YAML - inplace.ipynb'
analysis_notebook_name = 'smFRET-Quick-Test-Server.ipynb'

remote_origin_basedir = '/mnt/Antonio/'           # Remote dir containing the original acquisition data
temp_basedir = '/mnt/ramdisk/'                    # Local temp dir with very fast access
local_archive_basedir = '/mnt/archive/Antonio/'   # Local dir for archiving data
remote_archive_basedir = '/mnt/wAntonio/'         # Remote dir for archiving data

DRY_RUN = False     # Set to True for a debug dry-run


def timestamp():
    print('\n-- TIMESTAMP %s\n' % time.ctime(), flush=True)


def replace_basedir(path, orig_basedir, new_basedir):
    return Path(str(path.parent).replace(orig_basedir, new_basedir), path.name)


def filecopy(source, dest, msg=''):
    print('* Copying %s ...' % msg, flush=True)
    if not DRY_RUN:
        ret = sp.call(['cp', '-av', source, dest])
    else:
        ret = 'DRY RUN'
    print('  [DONE]. Return code %s\n' % ret, flush=True)


def copy_files_to_ramdisk(fname, orig_basedir, dest_basedir=temp_basedir):
    """
    Copy a DAT and YML file pair to ramdisk folder.

    Arguments:
        fname (Path): full path of DAT file to be copied.
    """
    # Create destination folder if not existing
    dest_fname = replace_basedir(fname, orig_basedir, dest_basedir)
    dest_fname.parent.mkdir(parents=True, exist_ok=True)

    # Copy data
    filecopy(fname, dest_fname, msg='DAT file to ramdisk')

    # Copy metadata
    filecopy(fname.with_suffix('.yml'), dest_fname.with_suffix('.yml'),
             msg='YAML file to ramdisk')

    return dest_fname


def copy_files_to_archive(h5_fname, orig_fname, nb_conv_fname):
    """
    Copy Photon-HDF5, YML, DAT, and conversion notebooks to archive folder.

    Arguments:
        h5_fname (Path): full path of HDF5 file to be copied into archive
        orig_fname (Path): full path of DAT file to be copied into archive
        nb_conv_fname (Path): full path of the executed conversion notebook
    """
    # Create destination folder if not existing and compute filenames
    dest_h5_fname = replace_basedir(h5_fname, temp_basedir, local_archive_basedir)
    dest_h5_fname.parent.mkdir(parents=True, exist_ok=True)
    dest_nb_conv_fname = replace_basedir(nb_conv_fname, temp_basedir, local_archive_basedir)
    dest_orig_fname = replace_basedir(orig_fname, temp_basedir, local_archive_basedir)

    # Copy HDF5 file
    filecopy(h5_fname, dest_h5_fname, msg='HDF5 file to archive')

    # Copy metadata
    filecopy(orig_fname.with_suffix('.yml'), dest_orig_fname.with_suffix('.yml'),
             msg='YAML file to archive')

    # Copy DAT file
    filecopy(orig_fname, dest_orig_fname, msg='DAT file to archive')

    # Copy conversion notebook
    filecopy(nb_conv_fname, dest_nb_conv_fname,
             msg='conversion notebook to archive')


def convert(filepath, basedir):
    """
    Convert a DAT file to Photon-HDF5.

    Arguments:
        filepath (Path): full path of DAT file to be converted.
    """
    print('* Converting input file to Photon-HDF5...', flush=True)

    # Name of the output notebook
    suffix = 'inplace' if 'inplace' in convert_notebook_name else 'tf'
    nb_out_path = Path(filepath.parent, filepath.stem + '_%s_conversion.ipynb' % suffix)

    # Compute input file name relative to the basedir
    # This is the format of the input file-name required by the conversion notebook
    fname_nb_input = str(replace_basedir(filepath, basedir, ''))

    # Convert file to Photon-HDF5
    if not DRY_RUN:
        run_notebook(convert_notebook_name, out_notebook_path=nb_out_path,
                     nb_kwargs={'fname': fname_nb_input})

    print('  [DONE].\n', flush=True)

    h5_fname = Path(filepath.parent, filepath.stem + '_%s.hdf5' % suffix)
    return h5_fname, nb_out_path


def run_analysis(fname):
    """
    Run basic smFRET analysis on the passed Photon-HDF5 file.

    Arguments:
        fname (Path): full path of HDF5 file to be analyzed.
    """
    print('* Running smFRET analysis...', flush=True)
    # Name of the output notebook is the same of data file
    nb_out_path = fname.with_suffix('.ipynb')

    # Convert file to Photon-HDF5
    if not DRY_RUN:
        run_notebook(analysis_notebook_name, out_notebook_path=nb_out_path,
                     nb_kwargs={'fname': str(fname)})
    print('  [DONE].\n', flush=True)


def remove_temp_files(dat_fname):
    """Remove temporary files."""
    # Safety checks
    folder = dat_fname.parent
    assert remote_archive_basedir not in str(folder)
    assert local_archive_basedir not in str(folder)
    print('* Removing temp files in "%s" (waiting 5 seconds to cancel) ' % folder,
          end='', flush=True)
    try:
        for i in range(1, 6):
            time.sleep(1)
            print('%d ' % i, end='', flush=True)
        time.sleep(1)
        print()
    except KeyboardInterrupt:
        print('\n- Removing files canceled!\n', flush=True)
    else:
        # Remove files
        if not DRY_RUN:
            os.remove(dat_fname)
            extensions = ('_tf.hdf5', '_inplace.hdf5', '.yml')
            for ext in extensions:
                curr_file = Path(dat_fname.parent, dat_fname.stem + ext)
                if curr_file.is_file():
                    os.remove(curr_file)

        print('  [DONE]. \n', flush=True)


def process(fname, dry_run=False):
    """
    This is the main function to all to copy the input DAT file to the temp
    folder, convert it to Photon-HDF5, copy all the files to the archive folder
    and run a basic smFRET analysis.
    """
    global DRY_RUN
    DRY_RUN = DRY_RUN or dry_run

    assert fname.is_file(), 'File not found: %s' % fname

    title_msg = 'PROCESSING: %s' % fname.name
    print('\n\n%s' % title_msg, flush=True)

    timestamp()
    assert remote_origin_basedir in str(fname)
    copied_fname = copy_files_to_ramdisk(fname, remote_origin_basedir, temp_basedir)

    timestamp()
    assert temp_basedir in str(copied_fname)
    h5_fname, nb_conv_fname = convert(copied_fname, temp_basedir)

    timestamp()
    copy_files_to_archive(h5_fname, copied_fname, nb_conv_fname)

    timestamp()
    remove_temp_files(copied_fname)

    #timestamp()
    #h5_fname_archive = replace_basedir(h5_fname, temp_basedir, local_archive_basedir)
    #assert h5_fname_archive.is_file()
    #run_analysis(h5_fname_archive)
    timestamp()
    return fname


def process_int(fname, dry_run=False):
    ret = None
    try:
        ret = process(fname, dry_run=dry_run)
    except Exception as e:
        print('Worker for "%s" got exception:\n%s' % (fname, str(e)), flush=True)
    print('Completed processing for "%s" (worker)' % fname, flush=True)
    return ret


if __name__ == '__main__':
    msg = '1 or 2 command-line arguments expected. Received %d instead.'
    assert 2 <= len(sys.argv) <= 3, msg % (len(sys.argv) - 1)

    if len(sys.argv) == 3:
        assert sys.argv[2] == '--dry-run', 'Second argument can only be "--dry-run".'
        dry_run = True

    fname = Path(sys.argv[1])
    process_int(fname, dry_run=dry_run)
    print('Closing worker for "%s"' % fname, flush=True)
