class data_generator(Sequence):
    """
    Generator class to process large datasets.
    """

    def __init__(self, filenames, feat_col_labels, target_col_labels, batch_size):
        self.filenames = filenames
        self.feat_col_labels = feat_col_labels
        self.target_col_labels = target_col_labels
        self.batch_size = batch_size

    def __len__(self):
        return int(np.ceil(len(self.filenames) / float(self.batch_size)))

    def __getitem__(self, idx):
        data = pd.read_csv(self.filenames[idx])# * self.batch_size:(idx + 1) * self.batch_size])
        batch_x = data[self.feat_col_labels].values
        batch_y = data[self.target_col_labels].values

        return np.array(batch_x), np.array(batch_y)
    
    
def generate_metadata_dict(filelist):
    """
    Parse metadata from all filenames and generate dictionary to link 
    
    Parameters
    ----------
    filelist : list
        TODO.
        
    Returns
    -------
    method : dict
        TODO.
    setup : dict
        TODO.
    position : dict
        TODO.
    """
    # initialize variables
    methods = []
    setups = []
    positions = []
    
    # get metatdata from all filenames and append to lists if unexisting
    for name in filelist:
        m, s, p, _ = get_metadata_from_filename(name)
        if m not in methods:
            methods.append(m)
        if s not in setups:
            setups.append(s)
        if p not in positions:
            positions.append(p)
            
    # sort lists
    methods.sort()
    setups.sort()
    positions.sort()
    
    # create dictionaries
    methods = dict(zip(methods,np.arange(len(methods))))
    setups = dict(zip(setups,np.arange(len(setups))))
    positions = dict(zip(positions,np.arange(len(positions))))
    
    return methods, setups, positions

# deprecated
#filename = 'test.h5'

#df = pd.read_csv(data_dir+filelist[1])

# Save to HDF5
#df.to_hdf(filename, 'data', mode='w', format='table')
#del df    # allow df to be garbage collected

# Append more data
#df2 = pd.read_csv(data_dir+filelist[2])
#df2.to_hdf(filename, 'data', append=True)

def mse_wrap_angle_old(y_true, y_pred):
    """Custom loss function based on MSE but with angles wrapped to 360 degree. Not working."""
    diff = y_pred - y_true
    if K.greater(diff,180) is not None:
        diff = diff - 360
    elif K.less(diff,-180) is not None:
        diff = diff + 360
    return K.mean(K.square(diff), axis=-1)

def mae_wrap_angle_old(y_true, y_pred):
    """Custom loss function based on MAE but with angles wrapped to 360 degree. Not working."""
    diff = y_pred - y_true
    if K.greater(diff,180) is not None:
        diff = diff - 360
    elif K.less(diff,-180) is not None:
        diff = diff + 360
    return K.mean(K.abs(diff), axis=-1)






class DataGenerator_raw1(Sequence):
    """
    Generates data for Keras. TODO
    TODO
    """
    def __init__(self, list_IDs, filename, keys, feature_label, target_label, batch_size=32, dim=96, shuffle=True):
        """Initialization."""
        self.filename = filename
        self.list_IDs = list_IDs
        self.keys = keys
        self.feature_label = feature_label
        self.target_label = target_label
        self.batch_size = batch_size
        self.dim = dim
        self.shuffle = shuffle
        _, self.file_ext = splitext(self.filename)
        
        self.feature_data = pd.read_hdf(self.filename, self.keys[0])
        self.target_data = pd.read_hdf(self.filename, self.keys[1])
        
        self.n_subjects = 20 #TODO: get from target df
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
            
            target = self.target_data.iloc[targets_idx].values
            
            # Store sample
            X[i,] = self.feature_data.iloc[feature_idx].values

            # Store targets
            y[i] = target[subject_idx]

        return X, y