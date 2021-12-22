import pandas as pd
import numpy as np
import os

def readCPTfile(path):
    """
    Arguments:
    path : str
        Location of CPT file to be analyzed. 
        
    Returns:
        df : Dataframe with 4 columns
    """    
    
    df = pd.read_csv(path,sep='\t',header=None,skiprows=7)
    df = df.iloc[:,[0,4,5,3]].copy()   # Depth, qc , fs, u2
    df.iloc[:,2:] = df.iloc[:,2:] / 1000   # Convert fs and u2 from kPa to MPa
    df.columns = ['Depth (m)','qc (MPa)','fs (MPa)','u2 (MPa)']
    return df

def readSoilProfile():
    
    """For now this function returns a simple soil profile with two layers. 
        Future version can read a .csv or text file or other user input """
       
    soil = pd.DataFrame( [['1',0,18,'gwt_1'],
                         ['2',10,18,'gwt_1'],
                         ['3',20,18,'gwt_1']],
                        columns= ['Layer Name','Top Depth','Total Unit Weight','GWT'])  
    return soil

def readGWT():
    
    """For now this function returns a single PWP profile 
        Future version can read a .csv or text file or other user input """
       
    pwpProfile = pd.DataFrame({'Depth To':0}, index = ['gwt_1'])
    pwpProfile.index.name = 'GWT_ID'
    return pwpProfile


