

import pandas as pd
import numpy as np

def readCPT(CPT_file):

    """This function reads CPT Raw Data and returns a DF with:
        [Depth,qc,qt,fs,u2]

        INPUTS:
                CPT_file : str   (filename)
                step : int       depth increment for categorical index
                cpt_elev : float
    Parameters
    ----------
    CPT_file : str   (filename)
        Filename to be loaded
    step : int
        Depth increment for categorical index
    int_type : 'left or right'
        Choose which side of the interval is closed.
        'left' means that left side is closed and right is open. 'right' means otherwise.
    """

    df = pd.read_excel(CPT_file,header=None)

    #Extract Raw Data and Convert u2 (ft) to tsf
    raw_data = df.iloc[39:,[2,3,4,5,6]].copy()
    raw_data[6] = raw_data[6] * 62.4 / 2000
    raw_data.columns = ['Depth','qc','qt','fs','u2']
    raw_data.replace(to_replace = 0 , value = np.nan , inplace=True )

    #Drop last five Rows with NA in fs
    raw_data = raw_data.dropna(axis=0, subset=['fs'])
    raw_data.reset_index(drop=True,inplace=True)

    return raw_data


def filterCPT(raw, wSize = 11 , option = 'median', alpha = 0.8):

    """
    Filters qc and f using either median or rolling average.
    Calculates qt using a = 0.8 by default.
    Parameters
        ----------
        raw : pd.DataFrame
            CPT raw Data
        wSize : str
            Rolling window size
        option : 'median or average'
            Filtering option (default is 'median')
        alpha : float
            Alpha value to calculate qt using qc and u2
    """
    filtered_data = raw.copy()

    if option == 'median':
        f = lambda x : x.rolling(wSize,center=True,min_periods=1).median()
    elif option == 'average':
        f = lambda x : x.rolling(wSize,center=True,min_periods=1).mean()
    else:
        raise ValueError('Provide filtering method')

    filtered_data[['qc','fs']] =  filtered_data[['qc','fs']].apply(axis=0, func = f )
    filtered_data['qt'] = filtered_data['qc'] + filtered_data['u2'] * (1- alpha)

    return filtered_data

def filterCPT_settle3d(CPT,widthSize,BS = 1):
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
    raw_data = readCPT(CPT)    # #Depth, qc, qt, fs, u2,

    raw_data['Category'] = DepthCategory(raw_data['Depth'],widthSize)

    #Grouping and calculating qc_mean and STD
    df = raw_data.groupby('Category').agg({'qc' : [np.mean,np.std]})    #Groupby based on depth interval
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
    raw_data_merged = pd.merge(raw_data,df,on='Category',validate = 'm:1')
    filtered_CPT_data = raw_data_merged.copy()
    filtered_CPT_data = filtered_CPT_data.query('qc <= Bandwith')
    outliers = raw_data_merged.query('qc > Bandwith').index
    return (filtered_CPT_data,outliers,raw_data_merged)


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
