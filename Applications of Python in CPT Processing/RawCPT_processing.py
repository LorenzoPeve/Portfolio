

import pandas as pd
import numpy as np


def filterCPT(arr, wSize = 11 , option = 'median'):

    """
    Filters an array using either median or rolling average.
    Parameters
        ----------
        array : numeric numpy array
        wSize : str
            Rolling window size
        option : 'median or average'
            Filtering option (default is 'median')
    """
    if option == 'median':
        f = lambda x : pd.Series(arr).rolling(wSize,center=True,min_periods=1).median()
    elif option == 'average':
        f = lambda x : pd.Series(arr).rolling(wSize,center=True,min_periods=1).mean()
    else:
        raise ValueError('Provide filtering method')

    return f(arr).to_numpy()

def filterCPT_settle3d(tip_arr,depth_arr, elev, widthSize,BS = 1):
    """
    Filters out the row with qc values that do not satisfy the Bandwith thresholds.
    Algorithm taken from Settle3D. Refer to README file for the reference.
    Parameters
        ----------
        CPT_file : str   (filename)
            Filename to be loaded
        widthSize : float
            Window size
    """

    #Read Raw Data & get Categorical column based on window size
    #= readCPT(CPT)    # #Depth, qc, qt, fs, u2,

    catArray = DepthCategory(depth_arr,widthSize)

    raw = pd.DataFrame([tip_arr, depth_arr,catArray, elev]).T
    raw.columns = ['qc','Depth','Category','Elevation']  
    
    df = raw.groupby('Category').agg({'qc' : [np.mean,np.std]})    #Groupby based on depth interval
    df.columns = ['qc_mean','qc_std']                                   #Multindex to single index
    df.reset_index(inplace=True)             # columns = Category ,  qc_mean  , qc_std

    #Calculating Sigma_bi and Sigma_ai
    #Calculate Sigma_bi
    df_shifted_up = df.copy()
    df_shifted_up.index -= 1
    sigma_bi = (df['qc_std']**2 +  df_shifted_up['qc_std']**2)**0.5
    df['sigma_bi'] = sigma_bi

    #Calculate Sigma_ai
    df_shifted_down = df.copy()
    df_shifted_down.index += 1
    sigma_ai = (df['qc_std']**2 +  df_shifted_down['qc_std']**2)**0.5
    df['sigma_ai'] = sigma_ai
    df.head(10)

    #Uncomment to understand the INDEX SHIFT
    #pd.concat([df['Category'],df_shifted_up['Category'],df_shifted_down['Category']],axis=1,
    #     keys= ['Original','Next_interval','Previous Interval']).dropna(subset=['Original'])

    #FILTERING
    df['Bandwith'] = 'NA'                    #columns Category	qc_mean	qc_std	sigma_bi	sigma_ai	Bandwith
    filt = df['sigma_ai'] <= df['sigma_bi']
    df.loc[filt,'Bandwith'] = df['qc_mean'] + BS * sigma_ai
    df.loc[~filt,'Bandwith'] = df['qc_mean'] + BS * sigma_bi

    #Fix first and last row - First row to have
    df.loc[0,'Bandwith'] = df.loc[0,'qc_mean'] + BS * df.loc[0,'sigma_bi']
    df.loc[df.index[-1],'Bandwith'] = df.loc[df.index[-1],'qc_mean'] + BS * df.loc[df.index[-1],'sigma_ai']

    #MERGING
    raw_data_merged = pd.merge(raw,df,on='Category',validate = 'm:1')
    filtered_CPT_data = raw_data_merged.copy()
    filtered_CPT_data = filtered_CPT_data.query('qc <= Bandwith')
    x = filtered_CPT_data['qc'].to_numpy()
    y = filtered_CPT_data['Elevation'].to_numpy()
    return (x,y)


def DepthCategory(depth_array,step=5,int_type='left'):

    '''This function returns a Categorical_index to be used for coloring or filtering purposes
       based on the detph

       Parameters
       ----------
       depth_array : Series or np.array
           Array with depth values
       step : int
           Depth increment for categorical index
       int_type : 'left or right'
           Choose which side of the interval is closed.
           'left' means that left side is closed and right is open. 'right' means otherwise.
           """'''

    #Categorical Interval
    max_val = depth_array.max()
    grouper_array = [0,max_val,step]  #start,end
    dz = list(np.arange(grouper_array[0],grouper_array[1],grouper_array[2]))
    if max_val not in dz:
        dz[-1] = round( max_val + 0.001 ,4)
    left = dz[:-1].copy()
    right = dz[1:].copy()
    profile_interval = pd.IntervalIndex.from_arrays(left,right,closed= int_type)

    return pd.cut(depth_array,bins = profile_interval)
