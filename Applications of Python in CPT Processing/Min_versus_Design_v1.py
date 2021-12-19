

import os
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default='browser'


#Internal
import mappingSchemas as mapSchema
from plottingCPT import *

#################################
path = r'C:\Users\LPeve\Desktop\GEAG Seminar Talk\P17'
CRS = 'EPSG:3466'   #ESPG CODE = 3466 ( NAD83 Alabama West)
#################################

os.chdir(path)
df_CPT = pd.read_csv('COMPILED_CPTs.csv', header=0,index_col = [0,1])    
df_CPT_SOIL_ALL = pd.read_csv('COMPILED_CPTs_SOILS.csv', header=0,index_col = [0,1])
df_CPT_SURVEY_ALL = pd.read_csv('COMPILED_CPTs_SURVEY.csv', header=0,index_col = 0)



###############################################################################
###############################################################################
# PLOT CPTS NOT MEETING DESIGN CRITERIA

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


def extractCord(x):
    l_coord = x.strip().split(',') #x is in the form of ['31.008881,-87.997851\n',
    long = float(l_coord[1])
    lat = float(l_coord[0])
    return (long,lat)

# CPT Locations basemap coordinates
with open('coordinates.txt') as f:   #Open txt file with coordinates
    lines = f.readlines()            



s = gpd.GeoSeries([Point(extractCord(item)) for item in lines] , crs = 4326) # WGS84 Latitude/Longitude: EPSG:4326

# Convert (Lon,Lat) to 2-D projection (Easting,Northing)
s_converted = s.to_crs( crs = CRS)

#Convert 2-D points from meters to feet
x_vals = s_converted.x * 3.281
y_vals = s_converted.y * 3.281

#Bounding Box X-Y
BBox = (min(x_vals), max(x_vals),
        min(y_vals), max(y_vals))


df_geo_LONG_LAT['Latitude'] = df_geo_LONG_LAT['geometry'].y
df_geo_LONG_LAT['Longitude'] = df_geo_LONG_LAT['geometry'].x

###############################################################################
###############################################################################

#For simplification make all functions return the same tuple:
    # (1) color string array: Why? this will eliminate the need to modify Legend
    # (2) discrete Map to have ordered legend
    # (3) Order
    
    
    #taking this approach to manage hover data
    

arrayInterest = df_geo_LONG_LAT['Min Su'].to_numpy()
latArray = df_geo_LONG_LAT['Latitude'] = df_geo_LONG_LAT['geometry'].y
lonArray = df_geo_LONG_LAT['Longitude'] = df_geo_LONG_LAT['geometry'].x
cptNames = df_geo_LONG_LAT.index


dfGEO = pd.DataFrame(np.stack([arrayInterest,latArray,lonArray], axis=1),
            index = cptNames,
            columns = ['Array of Interest','Latitude' , 'Longitude'])



# Equal_Interval
# Quantiles
# Maximum_Breaks
# Natural_Breaks
# StdMean
# Percentiles
# User_Defined
# BestFit : 'FisherJenks'

colorSTRArray , \
colorDiscreteSeq, \
colorDiscreteOrder, \
legendTitle = mapSchema.classiSchema(arrayInterest, mode = 'BestFit' )
dfGEO['colorArray'] = colorSTRArray
fig = plotScatterMap( dfGEO, 'Min Su' ,   colorDiscreteSeq, colorDiscreteOrder, legendTitle)
fig.show()






