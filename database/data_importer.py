import pandas as pd
from os import listdir
from os.path import isfile, join
import os

'''
Method to read in all dataframes in a single file and return
a dictionary containing all of them where the key is the parameter
and the value is the dataframe

Input: 
    path_to_files: String representing path to data files
    data_folder_name: String representing name of file containing data within 
    
Returns:
    Dictionary containing all dataframes in the specified file with each key being the file name and the value
    being the respective dataframe for that data file
'''
def get_data(path_to_files,data_folder_name):
    #Filter out OS files used to keep track of contents of folder
    files = [f for f in listdir(path_to_files) if isfile(join(path_to_files, f)) and not f.startswith('.')]
    data = {}
    #Iterate through csv files in folder and read in the data
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
            dataframe = add_five_year_average(dataframe)

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

'''
Appends the five year average of data within the dataframe to that dataframe
with the unique year identifier 2000. 

Input:
    data: Dataframe containing five years worth of data
Return:
    data mutated to contain five year average designated by 
    year = 2000. 
'''
def add_five_year_average(data):
    dataframe = data[data['date'].dt.year.isin([2015, 2016, 2017, 2018, 2019])].copy()
    dataframe['date'] = dataframe['date'].apply(lambda x: x.replace(year=2000))
    dataframe = dataframe.groupby(['date', 'fips', 'county']).mean().reset_index()
    data = data.append(dataframe)
    return data

'''
Method to form master dictionary that contains all data from the sub-groups.

Input:
    file_dir: Path to directory containing files where each file contains data
        for an environmental group (Ex: GHG contains Greenhouse gas data files)
    folder_names: Names of files within the file_dir that will be explored for data
        and imported in the master dataframe
    
Returns:
    Dictionary with keys being each string within folder_names
    and values being a dictionary containing the dataframes within
    each folder respectively 
'''
def form_dataframe(file_dir,folder_names):
    final_df_dict = {}
    for file in folder_names:
        path_to_files = os.path.join(file_dir, file)
        final_df_dict[file] = get_data(path_to_files,file)
    return final_df_dict

#Get address to current directory (This will not work in Jupyter NB) 
file_dir = os.path.dirname(os.path.abspath(__file__))
file_names = ['AQ','GHG','WQ','ECON']
master_df = form_dataframe(file_dir,file_names)




