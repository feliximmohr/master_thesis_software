"""
Convert CSV files to HDF5 files containing pandas DataFrame objects.
"""

import numpy as np
import pandas as pd

from os.path import splitext
from utils.utils import get_metadata_from_filename

def csv2hdf_sep(data_dir, filelist, export_dir):
    """Write each csv file's data to seperate HDF5 file."""
    for name in filelist:
        # load csv
        df = pd.read_csv(data_dir+name)
        # save to HDF5
        name_new, _ = splitext(name)
        df.to_hdf(export_dir+name_new+'.h5', 'data', mode='w', format='table')

def hdf_sep2hdf_single(data_dir, filelist, export_dir, out_name='database.h5'):
    """Append to single large HDF5 file, each DF with individual key."""
    for name in filelist:
        m, _, p, _ = get_metadata_from_filename(name)
        key = m+'_'+p
        # load file
        df = pd.read_hdf(data_dir+name)
        # save to HDF5
        df.to_hdf(export_dir+out_name, key, mod='a', format='table')

def hdf_sep2hdf_single_append(data_dir, filelist, export_dir, out_name='database.h5'):
    """Append to single large HDF5 file, all DF appended with single key."""
    h5_file = pd.HDFStore(export_dir+out_name)#, complevel=5, complib='blosc')

    counter = 1
    for name in filelist:
        print('Appending Table {}'.format(counter))
        df = pd.read_hdf(data_dir+name)
        df2 = df.astype({'x':'float64', 'y':'float64'})
        h5_file.append('database', df2)#, complevel=5, complib='blosc')
        counter += 1
    
    h5_file.close()

def csv_raw2hdf_single(data_dir, export_dir, out_name='database_raw.h5'):
    """TODO"""
    # load data
    f_df, t_df, ID_ref_df, pos_df, cond_df, par_df = load_csv_raw(data_dir)

    # write data
    pos_df.to_hdf(export_dir+out_name, 'position_table', mode='a', format='table')
    cond_df.to_hdf(export_dir+out_name, 'condition_table', mode='a', format='table')
    par_df.to_hdf(export_dir+out_name, 'feature_par', mode='a', format='table')
    ID_ref_df.to_hdf(export_dir+out_name, 'ID_reference_table', mode='a', format='table')
    t_df.to_hdf(export_dir+out_name, 'target_data', mode='a', format='table')
    f_df.to_hdf(export_dir+out_name, 'feature_data', mode='a', format='table')

def load_csv_raw(data_dir, filelist=None):
    """TODO"""
    # load metadata
    pos_table = pd.read_csv(data_dir+'position_table.csv',dtype={'pos_id':np.uint8})
    pos_table.set_index('pos_id', drop=True, inplace=True)
    cond_table = pd.read_csv(data_dir+'condition_table.csv',dtype={'cond_id':np.uint8})
    cond_table.set_index('cond_id', drop=True, inplace=True)
    par = pd.read_csv(data_dir+'feature_par.csv',dtype={'cond_id':np.uint8})
    ID_ref_table = pd.read_csv(data_dir+'ID_reference_table.csv',dtype={'global_id': np.uint32, 'pos_id': np.uint8, 'cond_id': np.uint8, 'subject_id':np.uint8})
    ID_ref_table.set_index('global_id', drop=True, inplace=True)
    # load data
    target_data = pd.read_csv(data_dir+'target_data.csv')
    feature_data = pd.read_csv(data_dir+'feature_data.csv')
    return feature_data, target_data, ID_ref_table, pos_table, cond_table, par
