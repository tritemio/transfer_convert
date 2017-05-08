
import nbrun

default_notebook_name = 'smFRET-Quick-Test-Server.ipynb'


def run_notebook(data_filename, input_notebook=None):
    if input_notebook is None:
        input_notebook = default_notebook_name
    print(' * Running analysis for %s' % (data_filename.stem), flush=True)
    nbrun.run_notebook(input_notebook, display_links=False,
                       out_notebook_path=data_filename.with_suffix('.ipynb'),
                       nb_kwargs={'fname': str(data_filename)})
    print('   [COMPLETED ANALYSIS] %s' % (data_filename.stem), flush=True)
