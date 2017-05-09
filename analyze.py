
import nbrun

default_notebook_name = 'smFRET-Quick-Test-Server.ipynb'


def run_analysis(data_filename, input_notebook=None, save_html=False,
                 dry_run=False):
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
                           save_html=save_html)
    print('   [COMPLETED ANALYSIS] %s' % (data_filename.stem), flush=True)
