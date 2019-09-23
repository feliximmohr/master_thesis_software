import numpy as np
import pandas as pd
from keras.utils import Sequence
from os.path import splitext

class DataGenerator(Sequence):
    """
    Generates data for Keras. Based on a global ID list load radomized single rows of data from file ID + local row ID pairs.
    VERY slow.
    """
    def __init__(self, list_IDs, data_dir, filelist, feature_label, target_label, n_rows=720000, batch_size=32, dim=96, shuffle=True):
        """Initialization."""
        self.list_IDs = list_IDs
        self.data_dir = data_dir
        self.filelist = filelist
        self.feature_label = feature_label
        self.target_label = target_label
        self.n_rows = n_rows
        self.batch_size = batch_size
        self.dim = dim
        self.shuffle = shuffle
        _, self.file_ext = splitext(self.filelist[0])
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
            # get name of file to read from
            file_idx = int(np.floor(ID/self.n_rows))
            filename = self.filelist[file_idx]
            # get local row index from ID (global index)
            local_idx = np.mod(ID,self.n_rows)
            
            if self.file_ext == '.h5':
                # load data from HDF5 file
                data = pd.read_hdf(self.data_dir+filename, where=[local_idx])
            else:
                # determine rows not to read
                local_rows = np.arange(self.n_rows,dtype='int32')
                skip_rows = np.delete(local_rows, local_idx)
                # load data from csv file
                data = pd.read_csv(self.data_dir+filename, skiprows=skip_rows)
            
            # Store sample
            X[i,] = data[self.feature_label].values

            # Store targets
            y[i] = data[self.target_label].values

        return X, y
    
class DataGenerator2(Sequence):
    """
    Based on a global ID list load radomized batches of consecutive rows of data from file ID + local row ID pairs.
    Slow.
    """
    def __init__(self, list_IDs, data_dir, filelist, feature_label, target_label, n_rows=720000, batch_size=32, dim=96, shuffle=True):
        """Initialization."""
        self.list_IDs = list_IDs
        self.data_dir = data_dir
        self.filelist = filelist
        self.feature_label = feature_label
        self.target_label = target_label
        self.n_rows = n_rows
        self.batch_size = batch_size
        self.dim = dim
        self.shuffle = shuffle
        _, self.file_ext = splitext(self.filelist[0])
        self.on_epoch_end() #trigger once at beginning

    def __len__(self):
        """Denotes the number of batches per epoch."""
        return int(np.floor(len(self.list_IDs) / self.batch_size))

    def __getitem__(self, index):
        """Generate one batch of data."""
        # Generate indexes of the batch
        list_IDs_temp = self.list_IDs[index*self.batch_size:(index+1)*self.batch_size]

        # Generate data
        X, y = self.__data_generation(list_IDs_temp)

        return X, y

    #def on_epoch_end(self):
    #    """Updates indexes after each epoch."""
    #    self.indexes = self.list_IDs
    #    if self.shuffle == True:
    #        np.random.shuffle(self.indexes)

    def __data_generation(self, list_IDs_temp):
        """
        Generates data containing batch_size samples
        X : (n_samples, dim)
        """
        # Initialization
        X = np.empty((self.batch_size, self.dim))
        y = np.empty((self.batch_size))
        
        # get name of file to read from
        file_idx = np.floor(np.divide(list_IDs_temp,self.n_rows))
        file_idx = file_idx.astype(int)
        multifile = np.argmax(file_idx>file_idx[0])
        # get local row index from ID (global index)
        local_idx = np.mod(list_IDs_temp,self.n_rows)
            
        if self.file_ext == '.h5':
            # load data from HDF5 file
            if not multifile:
                local_idx = local_idx.tolist()
                data = pd.read_hdf(self.data_dir+self.filelist[file_idx[0]], where=local_idx)
            else:
                local_idx1 = local_idx[:multifile].tolist()
                local_idx2 = local_idx[multifile:].tolist()
                df1 = pd.read_hdf(self.data_dir+self.filelist[file_idx[0]], where=local_idx1)
                df2 = pd.read_hdf(self.data_dir+self.filelist[file_idx[multifile]], where=local_idx2)
                data = pd.concat([df1, df2])
        else:
            # determine rows not to read
            local_rows = np.arange(self.n_rows,dtype='int32')
            skip_rows = np.delete(local_rows, local_idx)
            # load data from csv file
            data = pd.read_csv(self.data_dir+self.filelist[file_idx[0]], skiprows=skip_rows)
              
        # Store sample
        X = data[self.feature_label].values

        # Store targets
        y = data[self.target_label].values

        return X, y
    
class DataGenerator3(Sequence):
    """
    Based on a global ID list load radomized rows of data from single large table in single HDF5 file.
    Might be slow?
    """
    def __init__(self, list_IDs, data_dir, filelist, feature_label, target_label, n_rows=720000, batch_size=32, dim=96, shuffle=True):
        """Initialization."""
        self.list_IDs = list_IDs
        self.data_dir = data_dir
        self.filelist = filelist
        self.feature_label = feature_label
        self.target_label = target_label
        self.n_rows = n_rows
        self.batch_size = batch_size
        self.dim = dim
        self.shuffle = shuffle
        self.on_epoch_end() #trigger once at beginning

    def __len__(self):
        """Denotes the number of batches per epoch."""
        return int(np.floor(len(self.list_IDs) / self.batch_size))

    def __getitem__(self, index):
        """Generate one batch of data."""
        # Generate indexes of the batch
        list_IDs_temp = self.list_IDs[index*self.batch_size:(index+1)*self.batch_size]

        # Generate data
        X, y = self.__data_generation(list_IDs_temp)

        return X, y

    def on_epoch_end(self):
        """Updates indexes after each epoch."""
        self.indexes = self.list_IDs
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
            
        data = pd.read_hdf(self.data_dir+self.filelist[0], mode='r', where=list_IDs_temp)
              
        # Store sample
        X = data[self.feature_label].values

        # Store targets
        y = data[self.target_label].values

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

def get_ID_list(filelist, ignore_list, n_rows=[]):
    """
    Generate IDs each corresponding to exactly one row/sample of an entire data set.
    Returns list of numeric IDs. If specified, specific files and corresponding IDs can be ignored.
    
    Parameters
    ----------
    filelist : list
        List of strings containing the filenames.
    ignore_list : list
        List containing substrings of filenames to specify the files to be ignored.
        If an element in this list matches a substring in a filename, the corresponding file will be ignored.
    n_rows : list, optional
        Number of rows per file. If not specified, the number of rows will be
        determined by the first file in the sorted filelist.
    
        
    Returns
    -------
    ID_list : list
        List of numeric IDs, each corresponding to exactly one row of the complete data set.
        If specific files are ignored (corresponding to specific conditions/metadata),
        the corresponding row IDs are missing in this list.
    """
    
    # sort filelist
    filelist.sort()
    
    # get number of files and rows per file (optional)
    n_files = len(filelist)
    if not n_rows:
        with open(data_dir+filelist[0]) as file:
            n_rows = len(file.readlines())-1 #skip column label
    
    # initialize variables
    ID_list = np.array([], dtype='int32')
    
    # generate ID list for each file
    for file_idx,name in enumerate(filelist):
        m, s, p, _ = get_metadata_from_filename(name)
        
        ignore = any(any(elem in s for s in [m, s, p])  for elem in ignore_list)
        
        start_idx = file_idx * n_rows
        stop_idx = (file_idx+1) * n_rows
        
        # concatenate IDs for each file
        if not ignore:
            ID_list = np.concatenate((ID_list, np.arange(start=start_idx, stop=stop_idx, dtype='int32')))
              
    return ID_list, n_rows