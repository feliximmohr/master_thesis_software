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