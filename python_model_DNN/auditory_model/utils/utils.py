"""
Various utility functions.
"""

import numpy as np
import pandas as pd
from os import walk

def get_filelist(data_dir):
    """Load filelist."""
    filelist = []
    for (_, _, filenames) in walk(data_dir):
        filelist.extend(filenames)
    return filelist.sort()

def get_metadata_from_filename(filename):
    """
    Get metadata from filename of this project's specific naming convention.
    Obtained parameters include method, setup, position and original dataset_name.
    
    Naming convention: 'DATASETNAME_METHOD_SETUP_METHOD-PARAM_POSITION_data.FILE-EXTENSION'
    Example: 'exp1_NFCHOA_L56_M006_pos01_data.csv'
    
    Parameters
    ----------
    filename : string
        Name of a file containing some metadata information.
        
    Returns
    -------
    method : string
        SFS method obtained from file name.
    setup : string
        Reproduction setup as obtained from filename.
    position : string
        Position identifier as obtained from filename.
    dataset_name : string
        Name of original data set as obtained from filename.
    """
    metadata = filename.split('_')
    
    dataset_name = metadata[0]
    method = metadata[1] + '_' + metadata[3]
    setup = metadata[2]
    position = metadata[4]
    
    return method, setup, position, dataset_name