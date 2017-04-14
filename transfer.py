#!/usr/bin/env python

import sys
from pathlib import Path
import subprocess as sp
import tempfile
import shutil
from nbrun import run_notebook


convert_notebook_name = 'Convert to Photon-HDF5 48-spot smFRET from YAML - tempfile.ipynb'
convert_notebook_name = 'Convert to Photon-HDF5 48-spot smFRET from YAML - inplace.ipynb'
analysis_notebook_name = 'smFRET-Quick-Test-Server.ipynb'

remote_origin_basedir = '/mnt/Antonio/'           # Remote dir containing the original acquisition data
temp_basedir = '/mnt/ramdisk/'                    # Local temp dir with very fast access 
local_archive_basedir = '/mnt/archive/Antonio/'   # Local dir for archiving data
remote_archive_basedir = '/mnt/wAntonio/'         # Remote dir for archiving data


def replace_basedir(path, orig_basedir, new_basedir):
    return Path(str(path.parent).replace(orig_basedir, new_basedir), path.name)


def copy_files_to_ramdisk(fname, orig_basedir, dest_basedir):
    """
    Arguments:
        fname (Path): full path of DAT file to be copied.
    """
    # Create destination folder if not existing
    dest_fname = replace_basedir(fname, orig_basedir, dest_basedir)
    dest_fname.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy data
    print('* Copying DAT file to ramdisk...', flush=True)
    ret = sp.call(['cp', '-av', fname, dest_fname])
    print('  [DONE]. Return code %s\n' % ret)

    # Copy metadata
    print('* Copying YAML file to ramdisk...', flush=True)
    ret = sp.call(['cp', '-av', fname.with_suffix('.yml'), 
                   dest_fname.with_suffix('.yml')])
    print('  [DONE]. Return code %s\n' % ret)
    return dest_fname


def copy_files_to_archive(h5_fname, orig_fname, nb_conv_fname):
    """
    Arguments:
        fname (Path): full path of HDF5 file to be copied.
        nb_fname (Path): full path of the executed conversion notebook
    """
    # Create destination folder if not existing and compute filenames 
    dest_h5_fname = replace_basedir(h5_fname, temp_basedir, local_archive_basedir)
    dest_h5_fname.parent.mkdir(parents=True, exist_ok=True)
    dest_nb_conv_fname = replace_basedir(nb_conv_fname, temp_basedir, local_archive_basedir)
    dest_orig_fname = replace_basedir(orig_fname, temp_basedir, local_archive_basedir)
    
    # Copy HDF5 file
    print('* Copying HDF5 file to archive...', flush=True)
    ret = sp.call(['cp', '-av', h5_fname, dest_h5_fname])
    print('  [DONE]. Return code %s\n' % ret)

    # Copy metadata
    print('* Copying YAML file to archive...', flush=True)
    ret = sp.call(['cp', '-av', orig_fname.with_suffix('.yml'), 
                   dest_orig_fname.with_suffix('.yml')])
    print('  [DONE]. Return code %s\n' % ret)
    
    # Copy DAT file
    print('* Copying DAT file to archive...', flush=True)
    ret = sp.call(['cp', '-av', orig_fname, dest_orig_fname])
    print('  [DONE]. Return code %s\n' % ret)

    # Copy conversion notebook
    print('* Copying conversion notebook to archive...', flush=True)
    ret = sp.call(['cp', '-av', nb_conv_fname, dest_nb_conv_fname])
    print('  [DONE]. Return code %s\n' % ret)

    # Copy cache file if present
    cache_fname = Path(h5_fname.parents, h5_fname.stem + '_cache.hdf5')
    if cache_fname.is_file():
        dest_cache_fname = replace_basedir(cache_fname, temp_basedir, local_archive_basedir)
        print('* Copying cache file to archive...', flush=True)
        ret = sp.call(['cp', '-av', cache_fname, dest_cache_fname])
        print('  [DONE]. Return code %s\n' % ret)

    # Remove files
    print('* Removing temporary files...', flush=True)
    shutil.rmtree(fname.parent)
    print('  [DONE]. Return code %s\n' % ret)


def convert(filepath, basedir):
    """
    Arguments:
        filepath (Path): full path of DAT file to be converted.
    """
    print('* Converting input file to Photon-HDF5...', flush=True)
    
    # Name of the output notebook
    suffix = 'inplace' if 'inplace' in convert_notebook_name else 'tf'
    nb_out_path = Path(filepath.parent, filepath.stem + '_conversion_%s.ipynb' % suffix)
    
    # Compute input file name relative to the basedir
    # This is the format of the input file-name required by the conversion notebook
    fname_nb_input = str(replace_basedir(filepath, basedir, ''))
    
    # Convert file to Photon-HDF5
    run_notebook(convert_notebook_name, out_notebook_path=nb_out_path,
                 nb_kwargs={'fname': fname_nb_input})

    print('  [DONE].\n')
    
    h5_fname = Path(filepath.parent, filepath.stem + '_%s.hdf5' % suffix)
    return h5_fname, nb_out_path


def run_analysis(fname):
    """
    Arguments:
        filepath (Path): full path of HDF5 file to be analyzed.
    """
    # Name of the output notebook is the same of data file
    nb_out_path = fname.with_suffix('.ipynb')

    # Convert file to Photon-HDF5
    run_notebook(analysis_notebook_name, out_notebook_path=nb_out_path,
                 nb_kwargs={'fname': str(fname)})
    print('  [DONE].\n')
    
    
if __name__ == '__main__':
    print()
    msg = 'One command-line argument expected. Received %d instead.'
    assert len(sys.argv) == 2, msg % (len(sys.argv) - 1)

    fname = Path(sys.argv[1])
    assert fname.is_file(), 'File not found: %s' % fname
    
    assert remote_origin_basedir in str(fname)
    copied_fname = copy_files_to_ramdisk(fname, remote_origin_basedir, temp_basedir)
    
    assert temp_basedir in str(copied_fname)
    h5_fname, nb_conv_fname = convert(copied_fname, temp_basedir)
    
    assert h5_fname.is_file()
    run_analysis(h5_fname)
    
    copy_files_to_archive(h5_fname, copied_fname, nb_conv_fname)
    
    
