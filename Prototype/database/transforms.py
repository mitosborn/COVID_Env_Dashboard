import pandas as pd
from os import listdir
from os.path import isfile, join
import os
from urllib.request import urlopen
import json
# Method to read in all dataframes in a single file and return 
# a dictionary containing all of them where the key is the parameter
# and the value is the dataframe
def get_data(file_dir, data_folder_name):
    path_to_files = os.path.join(file_dir, data_folder_name)      
    files = [f for f in listdir(path_to_files) if isfile(join(path_to_files, f)) and not f.startswith('.')]
    data = {}
    for fil in files:
        parameter = fil[0:-4]
        dataframe = pd.read_csv(path_to_files+'/'+ fil, sep = ',', index_col = False)
        try:
            dataframe.columns = dataframe.columns.str.lower()
            if(parameter.lower() in dataframe.columns.values):
                dataframe = dataframe.rename(columns = {parameter.lower():'value'})
            print(dataframe.columns)
            dataframe['date'] = pd.to_datetime(dataframe['date'])
            dataframe['fips'] = dataframe['fips'].astype(int).astype(str)
        except:
            print("Has no date col")
        data[parameter] = dataframe
    if(data_folder_name == 'ECON'):
        print("Got here")
        #Read in Econ county point level data
        data['county_centers']['name'] = data['county_centers']['name'].str.replace(' County', '')
        data['county_centers'].drop(['usps', 'ansicode'], axis=1, inplace=True)
        data['econ_data'] = data['econ_data'].merge(data['county_centers'],how = 'left',left_on = 'county',right_on = 'name')

        data['econ_data'].columns = [col.strip() for col in data['econ_data'].columns]
    return data

# Method to form master dictionary that contains all data from the sub-groups.
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




