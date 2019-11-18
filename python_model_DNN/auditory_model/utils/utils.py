"""
Various utility functions.
"""

import json
import sys
from os import walk
from numpy import savetxt


def get_filelist(data_dir):
    """Load filelist and return sorted version of it."""
    filelist = []
    for (_, _, filenames) in walk(data_dir):
        filelist.extend(filenames)
    filelist.sort()
    return filelist


def get_metadata_from_filename(filename):
    """
    Get metadata from filename of this project's specific naming convention.
    Obtained parameters include method, setup, position and original dataset_name.
    
    Naming convention: 'DATASETNAME_METHOD_SETUP_METHOD-PARAM_POSITION_data.FILE-EXTENSION'
    Example: 'exp1_NFCHOA_L56_M006_pos01_data.csv'
    
    Parameters
    ----------
    filename : str
        Name of a file containing some metadata information.
        
    Returns
    -------
    method : str
        SFS method obtained from file name.
    setup : str
        Reproduction setup as obtained from filename.
    position : str
        Position identifier as obtained from filename.
    dataset_name : str
        Name of original data set as obtained from filename.
    """
    metadata = filename.split('_')
    
    dataset_name = metadata[0]
    method = metadata[1] + '_' + metadata[3]
    setup = metadata[2]
    position = metadata[4]
    return method, setup, position, dataset_name


def open_json(dir, filename):
    """Open json file and return its contents."""
    with open(dir + filename) as json_file:
        content = json.load(json_file)
    return content


def write_var_stdout(x):
    savetxt(sys.stdout, x)