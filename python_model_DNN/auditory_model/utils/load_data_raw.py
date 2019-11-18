"""
A python module that provides functions and classes to load data for training.
"""

import numpy as np
import pandas as pd
from keras.utils import Sequence


class DataGenerator_raw(Sequence):
    """
    A class for a data generator for Keras sequential models. Creates
    the training samples in batches on the fly from the non-reduntant
    (raw) database.    

    Attributes
    ----------
    list_IDs : numpy.ndarray
        A one-dimensional array containing global IDs or sample IDs.
    feature_data : numpy.ndarray
        Two-dimensional array of feature data from the non-redundant
        (raw) database.
    target_data : numpy.ndarray
        Two-dimensional array of target data from the non-redundant
        (raw) database.
    batch_size : int, optional
        Batch size.
    dim : int, optional
        Input dimension or number of features. Defaults to 96.
    shuffle : bool, optional
        Optionally shuffle the data for each epoch.
    n_frames : int, optional
        Number of frames/repititions in feature computation.
    n_angles : int, optional
        Number of angles. Defaults to 360.
    """
    def __init__(self, list_IDs, feature_data, target_data, batch_size=32,
                 dim=96, shuffle=True, n_frames=100, n_angles=360):
        """Initialization."""
        self.list_IDs = list_IDs
        self.feature_data = feature_data
        self.target_data = target_data
        self.batch_size = batch_size
        self.dim = dim
        self.shuffle = shuffle
        self.n_subjects = target_data.shape[1]
        self.n_frames = n_frames
        self.n_angles = n_angles
        self.on_epoch_end() #trigger once at beginning

    def __len__(self):
        """Denotes the number of batches per epoch."""
        return int(np.floor(len(self.list_IDs) / self.batch_size))

    def __getitem__(self, index):
        """Generate one batch of data."""
        # Generate indexes of the batch
        indexes = self.indexes[index*self.batch_size:(index+1)
                               *self.batch_size]

        # Find list of IDs
        list_IDs_temp = [self.list_IDs[k] for k in indexes]

        # Generate data
        X, y = self.__data_generation(list_IDs_temp)
        return X, y

    def on_epoch_end(self):
        """Updates indexes after each epoch."""
        self.indexes = np.arange(len(self.list_IDs))
        if self.shuffle == True:
            np.random.shuffle(self.indexes)

    def __data_generation(self, list_IDs_temp):
        """
        Generates data containing batch_size samples
        X : (n_samples, dim)
        """
        # Initialization
        X = np.empty((self.batch_size, self.dim))
        y = np.empty((self.batch_size))
        # Generate data
        for i, ID in enumerate(list_IDs_temp):
            # one feature row for all 20 subjects 0...19 -> f=0
            feature_idx = np.floor(ID/self.n_subjects)
            # one target row for 100 frames for each subject 0...1999 -> t=0
            target_idx = np.floor(ID/(self.n_subjects*self.n_frames))
            subject_idx = ID - feature_idx*self.n_subjects 
           
            # Store sample
            X[i,] = self.feature_data[int(feature_idx)]

            # Store targets
            y[i] = self.target_data[int(target_idx),int(subject_idx)]
        return X, y


def load_raw_ft_h5(filename, key_f='feature_data', key_t='target_data'):
    """
    Load raw feature and target data from single HDF5 file specified by
    filename and key. If no keys provided, use default keys.
    
    Parameters
    ----------
    filename : str
        Name of a HDF5 file containing the data.
    key_f : str, optional
        Key identifying the feature data in HDF5 file.
    key_t : str, optional
        Key identifying the target data in HDF5 file.
        
    Returns
    -------
    feature_df : pandas DataFrame object
        DataFrame containing all features.
    target_df : pandas DataFrame object
        DataFrame containing all targets.
    f_column_labels : list of strings
        Column labels of feature DataFrame.
    """
    feature_df = pd.read_hdf(filename, key=key_f)
    target_df = pd.read_hdf(filename, key=key_t)
    f_column_labels = feature_df.columns.tolist()
    return feature_df, target_df, f_column_labels


def load_raw_IDs_h5(filename, key_ID='ID_reference_table',
                    key_p='position_table', key_c='condition_table',
                    key_fp='feature_par'):
    """
    Load raw metadata from single HDF5 file specified by filename and
    key. If no keys provided, use default keys.
    
    Parameters
    ----------
    filename : str
        Name of a HDF5 file containing the data.
    key_ID : str, optional
        Key identifying the ID reference table in HDF5 file.
    key_p : str, optional
        Key identifying the position reference table in HDF5 file.
    key_c : str, optional
        Key identifying the condition reference table in HDF5 file.
    key_fp : str, optional
        Key identifying the feature parameter data in HDF5 file.
        
    Returns
    -------
    ID_ref_df : pandas DataFrame object
        DataFrame containing ID reference table.
    pos_table_df : pandas DataFrame object
        DataFrame containing position table.
    cond_table_df : pandas DataFrame object
        DataFrame containing condition table.
    par_df : pandas DataFrame object
        DataFrame containing feature parameter data.
    """

    ID_ref_df = pd.read_hdf(filename, key=key_ID)#.reset_index(drop=True)
    pos_table_df = pd.read_hdf(filename, key=key_p)
    cond_table_df = pd.read_hdf(filename, key=key_c)
    par_df = pd.read_hdf(filename, key=key_fp)
    return ID_ref_df, pos_table_df, cond_table_df, par_df


def load_raw_all_h5(filename, key_f=None, key_t=None, key_ID=None, key_p=None,
                    key_c=None, key_fp=None):
    """
    Load complete raw data from single HDF5 file specified by filename
    and key. If no keys provided, use default keys.
    
    Parameters
    ----------
    filename : str
        Name of a HDF5 file containing the data.
    key_f : str, optional
        Key identifying the feature data in HDF5 file.
    key_t : str, optional
        Key identifying the target data in HDF5 file.
    key_ID : str, optional
        Key identifying the ID reference table in HDF5 file.
    key_p : str, optional
        Key identifying the position reference table in HDF5 file.
    key_c : str, optional
        Key identifying the condition reference table in HDF5 file.
    key_fp : str, optional
        Key identifying the feature parameter data in HDF5 file.
        
    Returns
    -------
    feature_df : pandas DataFrame object
        DataFrame containing all features.
    target_df : pandas DataFrame object
        DataFrame containing all targets.
    ID_ref_df : pandas DataFrame object
        DataFrame containing ID reference table.
    pos_table_df : pandas DataFrame object
        DataFrame containing position table.
    cond_table_df : pandas DataFrame object
        DataFrame containing condition table.
    par_df : pandas DataFrame object
        DataFrame containing feature parameter data.
    """

    feature_df, target_df, _ = load_raw_ft_h5(filename)
    ID_ref_df, pos_table_df, cond_table_df, par_df = load_raw_IDs_h5(filename)
    return feature_df, target_df, ID_ref_df, pos_table_df, cond_table_df, par_df