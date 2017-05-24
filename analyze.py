
import nbrun

default_notebook_name = 'smFRET-Quick-Test-Server.ipynb'


def run_analysis(data_filename, input_notebook=None, save_html=False,
                 working_dir='./', dry_run=False):
    """
    Run analysis notebook on the passed data file.

    Arguments:
        data_filename (Path): path data file to be analyzed.
        input_notebook (Path): path of the analysis notebook.
        save_html (bool): if True save a copy of the output notebook in HTML.
        dry_run (bool): just pretenting. Do not run or save any notebook.
    """
    if input_notebook is None:
        input_notebook = default_notebook_name
    print(' * Running analysis for %s' % (data_filename.stem), flush=True)
    if not dry_run:
        nbrun.run_notebook(input_notebook, display_links=False,
                           out_notebook_path=data_filename.with_suffix('.ipynb'),
                           nb_kwargs={'fname': str(data_filename)},
                           save_html=save_html, working_dir=working_dir)
    print('   [COMPLETED ANALYSIS] %s' % (data_filename.stem), flush=True)


if __name__ == '__main__':
    import argparse
    from pathlib import Path

    descr = """\
        This script executes an analysis notebook on the specified HDF5 file.
        """
    parser = argparse.ArgumentParser(description=descr, epilog='\n')
    parser.add_argument('datafile',
                        help='Source folder with files to be processed.')
    msg = ("Filename of the analysis notebook. If not specified, the default "
           "notebook is '%s'." % default_notebook_name)
    parser.add_argument('--notebook', metavar='NB_NAME',
                        default=default_notebook_name, help=msg)
    parser.add_argument('--save-html', action='store_true',
                        help='Save a copy of the output notebooks in HTML.')
    parser.add_argument('--working-dir', metavar='PATH', default='./',
                        help='Working dir for the kernel executing the notebook.')
    args = parser.parse_args()

    datafile = Path(args.datafile)
    assert datafile.is_file(), 'Data file not found: %s' % datafile
    notebook = Path(args.notebook)
    assert notebook.is_file(), 'Notebook not found: %s' % notebook
    run_analysis(datafile, input_notebook=notebook,
                 save_html=args.save_html, working_dir=args.working_dir)
