
import nbrun

default_notebook_name = 'smFRET-Quick-Test-Server.ipynb'


def run_notebook(data_filename, input_notebook=None):
    if input_notebook is None:
        input_notebook = default_notebook_name
    nbrun.run_notebook(input_notebook,
                       out_notebook_path=data_filename.with_suffix('.ipynb'),
                       nb_kwargs={'fname': str(data_filename)})
