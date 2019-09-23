import numpy as np
import pandas as pd
from keras.utils import Sequence
from os.path import splitext

class DataGenerator_raw(Sequence):
    """
    Generates data for Keras. TODO
    TODO
    """
    def __init__(self, list_IDs, feature_data, target_data, batch_size=32, dim=96, shuffle=True):
        """Initialization."""
        self.list_IDs = list_IDs
        self.feature_data = feature_data
        self.target_data = target_data
        self.batch_size = batch_size
        self.dim = dim
        self.shuffle = shuffle
        
        self.n_subjects = target_data.shape[1]
        self.n_frames = 100 #TODO: get elsewhere
        self.n_angles = 360 #TODO: get elsewhere
        
        self.on_epoch_end() #trigger once at beginning

    def __len__(self):
        """Denotes the number of batches per epoch."""
        return int(np.floor(len(self.list_IDs) / self.batch_size))

    def __getitem__(self, index):
        """Generate one batch of data."""
        # Generate indexes of the batch
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]

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
        y = np.empty((self.batch_size), dtype=int)
        # Generate data
        for i, ID in enumerate(list_IDs_temp):
            feature_idx = np.floor(ID/self.n_subjects) #one feature row for all 20 subjects 0...19 -> f=0
            targets_idx = np.floor(ID/(self.n_subjects*self.n_frames)) #one target row for 100 frames for each subject 0...1999 -> t=0
            subject_idx = ID - feature_idx*self.n_subjects 
           
            # Store sample
            X[i,] = self.feature_data[int(feature_idx)]

            # Store targets
            y[i] = self.target_data[int(targets_idx),int(subject_idx)]
            
        return X, y
    
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

def get_ignore_ids(ignore_list, cond_lookup_df, pos_lookup_table=None):
    """
    Get condition (cond_id) and position ids (pos_id) to ignore as specified in list of strings ignore_list.
    Returns two unique lists for cond_id and pos_id, respectively.
    
    Parameters
    ----------
    ignore_list : list
        List of strings containing position or condition parameter substrings to ignore.
    cond_lookup_df : pandas.DataFrame object
        DataFrame object containing all conditions and corresponding indexes.
    pos_lookup_df : pandas.DataFrame object
        Not yet supported.
        
    Returns
    -------
    ignore_cond_ids : list
        List of condition ids to ignore as specified by ignore_list.
    ignore_pos_ids : list
        List of condition ids to ignore as specified by ignore_list.
    """
    ignore_cond_ids = []
    ignore_pos_ids = []
    cond_ign = []
    pos_ign = []
    # do for each element in ignore_list
    for ign in ignore_list:
        # check if element to ignore related to positions or conditions
        if 'pos' in ign:
            pos_ign = [int(ign[3:])-1]
        else:
            cond_ign = cond_lookup_df.index[cond_lookup_df['sfs_method'].str.contains(ign)].tolist()
        # append to list
        ignore_pos_ids.extend(pos_ign)
        ignore_cond_ids.extend(cond_ign)
    # return unique list
    return list(set(ignore_cond_ids)), list(set(ignore_pos_ids))
