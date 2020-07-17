import pandas as pd
from os import listdir
from os.path import isfile, join
import os

# Method to read in all dataframes in a single file and return 
# a dictionary containing all of them where the key is the parameter
# and the value is the dataframe
def get_data(file_dir, data_folder_name):
    path_to_files = os.path.join(file_dir, data_folder_name)      
    files = [f for f in listdir(path_to_files) if isfile(join(path_to_files, f))]
    data = {}
    for fil in files:
        parameter = fil[0:-5]
        dataframe = pd.read_csv(path_to_files+'/'+ fil, sep = ',', parse_dates=['Date'], index_col = False)
        data[parameter] = dataframe
    return data

# Method to form master dicionary that contains all data from the sub-groups.
# Outputs dictionary with key that is the name of the sub-group and value of
# the dataframes for that sub-group
def form_dataframe(file_dir,folder_names):
    final_df_dict = {}
    for file in folder_names:
        final_df_dict[file] = get_data(file_dir,file)
    return final_df_dict

#Get address to current directory (This will not work in Jupyter NB) 
file_dir = os.path.dirname(os.path.abspath(__file__))
file_names = ['AQ','GHG','WQ','ECON']
master_df = form_dataframe(file_dir,file_names)




