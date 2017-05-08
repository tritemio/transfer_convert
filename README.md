# transfer_convert

A collection of scripts for automating conversion to Photon-HDF5, 
archival and analysis of smFRET measurements using multiprocessing (each file
is processed in a different CPU).

A brief description of each script follows.

## monitor.py

Monitor a given folder. When a new YAML file appears and there is a DAT file with the same
name in the same folder it starts these processing steps:

- copy the data to a temp folder
- convert data to Photon-HDF5 using the metadata from the YAML file
- copy all files to and archival folder
- optionally run smFRET analysis

Many files can be processed in parallel if a new file appears when the processing
of the previous file is not finished yet.

Type `./monitor -h` for more info on how to use the script.

## batch_analysis.py

Analyze all the Photon-HDF5 files in a given folder using a default notebook
or any other specified notebook. Multiple files can be processed in parallel.
For optimal performances it is suggested to do not exceed the number of CPUs.

Type `./batch_analysis -h` for more info on how to use the script.

## transfer.py

Module used for processing a single file (copy, conversion, analysis).
The script `monitor.py` build a multiprocessing pool and calls functions 
defined in `transfer.py` to process several files in parallel. 

# Installation

Download the repository and run the scripts directly from the repo folder
(no installation).

## Dependencies

- python 3.6 (older versions may work)
- jupyter notebook 5+
- jupyter nbconvert 5+
- [pyyaml](http://pyyaml.org/)
- [tqdm](https://github.com/tqdm/tqdm) (progress bar)
- [FRETBursts](http://tritemio.github.io/FRETBursts/) 0.6.3+
- [phconvert](https://photon-hdf5.github.io/phconvert/) 0.7.3+
- [niconverter](https://github.com/tritemio/niconverter/tree/master)

See also [conda_environment_linux.yml](https://github.com/tritemio/transfer_convert/blob/master/conda_environment_linux.yml).
