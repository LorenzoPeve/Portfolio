
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

"""The functions in this module should all return a DF with at least three columns:
        ['Array of Interest', 'Latitude', 'Longitude'].
        Array of Interest can be any geotech paramater (i.e., Min undrained Strength, GWT Table,etc)"""



def minimumClayDesignStrength(df_CPT_SURVEY_ALL,df_CPT_SOIL_ALL,CRS):
    
    df = df_CPT_SURVEY_ALL.copy()
    df = df[['Northing (ft)','Easting (ft)']]
    
    def clayDesignValues(df_CPT_SOIL_ALL,df):
        
        def clayMINDesignValues(df):
            filt = df['Layer Name'].str.lower().str.strip().str.contains('clay')
            df = df.loc[filt,['Uni. Su Profile','Min. Su']].astype('float64')
            return df.min(axis=1).min()
    
        grpMIN = df_CPT_SOIL_ALL.groupby(level=0).apply(clayMINDesignValues)
        grpMIN.name = 'Min Su'
        df_geo = pd.concat([df , grpMIN] , axis=1)
        return df_geo
    
    
    df_geo = clayDesignValues(df_CPT_SOIL_ALL,df)
    
    #Feet to meters
    df_geo[['Northing (m)','Easting (m)']] = df_geo[['Northing (ft)','Easting (ft)']] * 0.3048
    df_geo.drop(labels=['Northing (ft)','Easting (ft)'], axis=1,inplace=True)
    df_geo = gpd.GeoDataFrame(df_geo,crs = CRS, geometry = gpd.points_from_xy(df_geo['Easting (m)'],df_geo['Northing (m)']))
    df_geo_LONG_LAT = df_geo.to_crs( crs = 4326)
    
    #  top left, top right, bottom right, bottom left
    df_geo_LONG_LAT['Latitude'] = df_geo_LONG_LAT['geometry'].y
    df_geo_LONG_LAT['Longitude'] = df_geo_LONG_LAT['geometry'].x
    df_geo_LONG_LAT = df_geo_LONG_LAT.loc[:,['Min Su','Latitude','Longitude']]
    
    return df_geo_LONG_LAT


def NE_to_Lat_long(df, CRS = 'EPSG:3466'):
    
    """
    df: DataFrame with at least 
        """
    
    df[['Northing (m)','Easting (m)']] = df[['Northing (ft)','Easting (ft)']] * 0.3048
    df = df[['Northing (m)','Easting (m)']]
    df = gpd.GeoDataFrame(df,crs = CRS, geometry = gpd.points_from_xy(df['Easting (m)'],df['Northing (m)']))
    df_geo = df.to_crs( crs = 4326)
     
    df_geo['Latitude'] = df_geo['geometry'].y
    df_geo['Longitude'] = df_geo['geometry'].x

    df_geo = df_geo.loc[:,['Latitude','Longitude']]
    return df_geo

def mapIdentifier(df, df_survey, layer, parameter, value, elevation, boundType, targetThickness):

    "This function  retruns a n x 3 DataFrame with [Boolean_array , Lat , Long] "
    
    def geoBoolean(df, layer, parameter, value, elevation, boundType, targetThickness):

        """Parameters
        df : pd.DataFrame CPT Output df for CPT
        layer : STR  ex. 'CCR,Sand 1'
        parameter : STR   MUST be a column of df
        value : float
        elevation : STR '[10,15]'
        boundType : STR    'Upper Bound' | 'Lower Bound'
        targetThickness : float
        """

        filt_1 = df['Layer IDX'] == layer
        elev_arr = [float(item) for item in elevation.strip('[]').split(',')]
        filt_2 = df['Elevation'].between(elev_arr[0],elev_arr[1])

        if boundType == 'Upper Bound':
            filt_3 = df[parameter] <= value
        else:
            filt_3 = df[parameter] >= value

        df = df[filt_1 & filt_2 & filt_3]

        return len(df) * 0.065 > 0.9 * targetThickness   
    
    boolSeries = df.groupby(level = 0).apply(geoBoolean, layer, parameter, value, elevation, boundType, targetThickness)
    boolSeries.name = parameter+'_bool'
    df_geo = NE_to_Lat_long(df_survey)  #DF with two columns (Latitude, Longitude) and CPT ID as the index
    df_bool = pd.concat([boolSeries, df_geo ], axis = 1, join = 'inner')
     
    return df_bool





def filterCPT(arr, filterMode, wSize = 11):

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
    if filterMode == 'Rolling Median':
        f = lambda x : pd.Series(arr).rolling(wSize,center=True,min_periods=1).median()
    elif filterMode == 'Rolling Average':
        f = lambda x : pd.Series(arr).rolling(wSize,center=True,min_periods=1).mean()
    else:
        raise ValueError('Provide filtering method')
    
    return f(arr).to_numpy()


def filterCPT_settle3d(tip_arr,depth_arr, elev, widthSize = 0.88, BS = 1, **kwargs):
    """
    Filters out the row with X values that do not satisfy the Bandwith thresholds.
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
    raw.columns = ['x','Depth','Category','Elevation']  
    
    df = raw.groupby('Category').agg({'x' : [np.mean,np.std]})    #Groupby based on depth interval
    df.columns = ['x_mean','x_std']                                   #Multindex to single index
    df.reset_index(inplace=True)            

    #Calculating Sigma_bi and Sigma_ai
    #Calculate Sigma_bi
    df_shifted_up = df.copy()
    df_shifted_up.index -= 1
    sigma_bi = (df['x_std']**2 +  df_shifted_up['x_std']**2)**0.5
    df['sigma_bi'] = sigma_bi

    #Calculate Sigma_ai
    df_shifted_down = df.copy()
    df_shifted_down.index += 1
    sigma_ai = (df['x_std']**2 +  df_shifted_down['x_std']**2)**0.5
    df['sigma_ai'] = sigma_ai
    df.head(10)

    #Uncomment to understand the INDEX SHIFT
    #pd.concat([df['Category'],df_shifted_up['Category'],df_shifted_down['Category']],axis=1,
    #     keys= ['Original','Next_interval','Previous Interval']).dropna(subset=['Original'])

    #FILTERING
    df['Bandwith'] = 'NA'                    #columns Category	qc_mean	qc_std	sigma_bi	sigma_ai	Bandwith
    filt = df['sigma_ai'] <= df['sigma_bi']
    df.loc[filt,'Bandwith'] = df['x_mean'] + BS * sigma_ai
    df.loc[~filt,'Bandwith'] = df['x_mean'] + BS * sigma_bi

    #Fix first and last row - First row to have
    df.loc[0,'Bandwith'] = df.loc[0,'x_mean'] + BS * df.loc[0,'sigma_bi']
    df.loc[df.index[-1],'Bandwith'] = df.loc[df.index[-1],'x_mean'] + BS * df.loc[df.index[-1],'sigma_ai']

    #MERGING
    raw_data_merged = pd.merge(raw,df,on='Category',validate = 'm:1')
    filtered_CPT_data = raw_data_merged.copy()
    filtered_CPT_data = filtered_CPT_data.query('x <= Bandwith')
    x = filtered_CPT_data['x'].to_numpy()
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
