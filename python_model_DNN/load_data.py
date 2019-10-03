import numpy as np
import pandas as pd
from keras.utils import Sequence
from os.path import splitext

class DataGenerator_raw(Sequence):
    """
    Generates data for Keras. TODO
    TODO
    """
    def __init__(self, list_IDs, feature_data, target_data, batch_size=32, dim=96, shuffle=True, n_frames=100, n_angles=360):
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
            target_idx = np.floor(ID/(self.n_subjects*self.n_frames)) #one target row for 100 frames for each subject 0...1999 -> t=0
            subject_idx = ID - feature_idx*self.n_subjects 
           
            # Store sample
            X[i,] = self.feature_data[int(feature_idx)]

            # Store targets
            y[i] = self.target_data[int(target_idx),int(subject_idx)]
            
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

def get_subset_ids(subset_list, cond_lookup_df, pos_lookup_df=None, subject_lookup_df=None):
    """
    Get condition (cond_id), position (pos_id) and subject ids of a subset of the data specified by subset_list.
    Returns unique lists for cond_id, pos_id and subject_id, respectively.
    
    Parameters
    ----------
    subset_list : list
        List of strings containing position, condition or subject parameter substrings to select the subset, e.g. ['NFCHOA', 'pos1', 'subject_1']
    cond_lookup_df : pandas.DataFrame object
        DataFrame object containing all conditions and corresponding indexes.
    pos_lookup_df : pandas.DataFrame object
        Not yet supported.
    subject_lookup_df : pandas.DataFrame object
        Not yet supported.
        
    Returns
    -------
    cond_ids_subset : list
        List of condition ids of a subset as specified by subset_list.
    pos_ids_subset : list
        List of position ids of a subset as specified by subset_list.
    subject_ids_subset : list
        List of subject ids of a subset as specified by subset_list.
    """
    cond_ids_subset = []
    pos_ids_subset = []
    subject_ids_subset = []
    cond_id = []
    pos_id = []
    subject_id = []
    # do for each element in subset_list
    for elem in subset_list:
        # check if element related to positions, conditions or subjects
        if 'pos' in elem:
            pos_id = [int(elem[3:])-1]
        elif 'subject' in elem:
            subject_id = [int(elem[8:])]
        else:
            cond_id = cond_lookup_df.index[cond_lookup_df['sfs_method'].str.contains(elem)].tolist()
        # append to list
        pos_ids_subset.extend(pos_id)
        cond_ids_subset.extend(cond_id)
        subject_ids_subset.extend(subject_id)
    # return unique lists
    return list(set(cond_ids_subset)), list(set(pos_ids_subset)), list(set(subject_ids_subset))

def get_subset_sample_idx(ID_ref, cond_ids, pos_ids, subject_ids):
    """ 
    Get list of sample indices of a subset of the complete data set.
    The subset is selected by condition, position and subject ids.
    Returns a unique list of indices corresponding to exactly one samlpe in the complete data set.
    
    Parameters
    ----------
    ID_ref : pandas DataFrame object
        .
    cond_ids : list of int
        .
    pos_ids : list of int
        .
    subject_ids : list of int
        .
        
    Returns
    -------
    idx_list : ndarray of uint32
        .
    """
    # Initialization
    idx_list = np.array([],dtype=np.uint32)
    # irgendwas
    for pos in pos_ids:
        idx = ID_ref[(ID_ref.pos_id==pos)].index.values.astype(np.uint32)
        idx_list = np.concatenate((idx_list, idx))
    for cond in cond_ids:
        idx = ID_ref[(ID_ref.cond_id==cond)].index.values.astype(np.uint32)
        idx_list = np.concatenate((idx_list, idx))
    for sub in subject_ids:
        idx = ID_ref[(ID_ref.subject_id==sub)].index.values.astype(np.uint32)
        idx_list = np.concatenate((idx_list, idx))

    # Return unique idx list
    return np.unique(idx_list)