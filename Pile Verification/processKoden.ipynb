##############################################################################

# This script takes the raw Koden survey data and applies a filtering procedure to match
# the VEGA software output.
# INPUT is required for:
#        - outlier threshold value in milimeters
#        - casing thickness in milimeters
#        - casing bottom depth in meters
#        - Filtering option. Either: 'median' or 'internal_profile'

##############################################################################


# This script takes the raw Koden survey data and applies a filtering procedure to match
# the VEGA software output.
# INPUT is required for:
#        - outlier threshold value in milimeters
#        - casing thickness in milimeters
#        - casing bottom depth in meters
#        - Filtering option. Either: 'median' or 'internal_profile'

##############################################################################


## LIBRARIES
import pandas as pd 
import numpy as np
from matplotlib import pyplot as plt
import plotly.graph_objects as go

##USER INPUT - To be Read from receiving spreadsheet

filt_option = 'median' 
#filt_option = 'internal_profile'   
outlier_threshold = 400       # milimeters
casing_bottom_depth = 10.60   # meters
casing_thick = 40             # milimeters

df_koden = pd.read_csv('S116944S-RCDD-KODE-DATA-100620-0249-UP1.TXT',
                     delimiter=',',
                     skiprows=1,
                     names= ['Depth (cm)','X',"X'",'Y',"Y'"],
                     usecols=range(1,6))

## RAW DATAFRAME MANIPULATION 
#casing_array = np.zeros(df_koden.shape)
#casing_array[:] = np.nan
#df_casing = pd.DataFrame(casing_array)
#df_casing.columns = ['Depth (cm)','X',"X'",'Y',"Y'"]

df_koden['Depth (m)'] = df_koden['Depth (cm)']/100
filt = df_koden['Depth (m)'] >= 0.25  
df_koden = df_koden.loc[filt]

filt = df_koden > outlier_threshold
df_koden.iloc[:,1:5] = df_koden.iloc[:,1:5].where(filt) # Where the value is smaller than threshold replace by NaN
df_koden.dropna(inplace=True)                           # Where the value is NaN DROP entire row

#ACCOUNTING FOR CASINS THICKNESS
df_casing = df_koden.copy()
cond = df_koden['Depth (m)'] < casing_bottom_depth
df_casing.loc[cond,'X':"Y'"] += casing_thick
df_casing.loc[~cond,'X':"Y'"] =np.nan

## DEPTH INTERVALS FOR REPORTING: 0.5, 1, 1.5...

depth_vals = pd.Series(np.arange(0.5,df_koden['Depth (m)'].max(),0.5))
if df_koden['Depth (m)'].max() not in depth_vals:
    depth_vals = depth_vals.append( pd.Series(df_koden['Depth (m)'].max()), ignore_index=True)
depth_vals = np.flip(depth_vals)  #Array from bottom to ground surface
depth_vals.name = 'Depth (m)'

## CREATING A SERIES WITH dz BOUNDS FOR FILTERING PURPOSES
        #NOTE: + 0.01 to solve a numerical issue and include final depth in interval

step = 0.5
dz = np.arange(0.25,df_koden['Depth (m)'].max(),step)       #   array([ 0.25,0.75,1.25,...
if df_koden['Depth (m)'].max() not in dz:
    dz = np.append(dz, df_koden['Depth (m)'].max()+0.01)    # Include maximum depth

## CREATE IntervalIndex FOR Groupby OPERATION

ll = dz[:-1].copy()
rr = dz[1:].copy()    
t1 = pd.IntervalIndex.from_arrays(ll,rr,
                                  closed='neither',       
                                  dtype='interval[float64]')  # VEGA software uses (-) type of interval 

## OBTAIN CATEGORICAL INTERVALS

depth_interval = pd.cut(df_koden['Depth (m)'], t1)  #returns a Series object with the respective bin for each depth


## Groupby BASED ON CATEGORICAL INTERVALS

df_koden_grp = df_koden.iloc[:,1:5].groupby(depth_interval, as_index=False) #group based on the bin interval


## CONCAT REPORTING DEPTHS (depth_vals) with FILTERED DF
        #NOTE: Groubpy sorts the group keys from small to large. That is why .iloc[::-1] is used below.

if filt_option == 'median':
    df_filt = pd.concat( [depth_vals ,df_koden_grp.median().iloc[::-1]],
                    axis=1,ignore_index=True)
elif filt_option == 'internal_profile':
    df_filt = pd.concat( [depth_vals ,df_koden_grp.min().iloc[::-1]],
                    axis=1,ignore_index=True)
else:
    raise ValueError('Specify Filtering Option')
    
df_filt.columns = ['Depth (m)','X',"X'",'Y',"Y'"]                # Rename because indexes are ignored in previous step
df_filt.sort_values('Depth (m)',ascending=False,inplace=True)    # Match VEGA Software output


## FINAL CLEANING AND EXPORTING
df_filt.dropna(inplace=True)
df_filt.to_csv('Filtered_Koden_output.csv')


#PLOTTING

layout = go.Layout(
                    font = dict(family = 'Arial', color = 'black'), #Sets the global font
                    width = 600,
                    height = 800,
                    title = dict(text = 'Pile Verticality Criteria',
                                 x = 0.5 , 
                                 xanchor = 'center'),
                    plot_bgcolor='#FFF',  # Sets background color to white
                    xaxis=dict(
                        title = 'Measurements (mm)', 
                        linecolor = 'black',  
                        range = [-1200,1200],
                        mirror=True,
                        showgrid=True,
                        gridcolor = '#E8E7E4',
                        gridwidth = 0.5,
                        ticks = 'inside',
                        ticklen = 10,
                        tickmode = 'linear',
                        tickangle = 0,
                        tick0 = -1200,
                        dtick = 200
                       ),
                    yaxis=dict(
                        title = 'Depth (m)',  
                        linecolor = 'black',  
                        mirror=True,
                        tickmode = 'linear',
                        showgrid=True,
                        gridcolor = '#E8E7E4',
                        ticks = 'inside',
                        ticklen = 10,
                        tick0 = 0,
                        dtick = 2,
                        autorange= 'reversed',
                        range = [0, 54],
                    )
                    )

data=go.Scatter(x=df_koden['Y'], y=df_koden['Depth (m)'], mode = 'markers',showlegend=False,
                marker = dict(color = 'black',
                              size = 3,
                              symbol = "diamond",
                              opacity = 0.5))

fig = go.Figure(data=data, layout=layout)
                              
fig.add_trace(go.Scatter
              (x=df_koden["Y'"]*-1, y=df_koden['Depth (m)'], mode = 'markers',showlegend=False,
                marker = dict(color = 'black',
                              size = 3,
                              symbol = "diamond",
                              opacity = 0.5)))

#ADD CASING Traces
fig.add_trace(go.Scatter
              (x=df_casing["Y'"]*-1, y=df_casing['Depth (m)'], mode = 'lines',name="Y'|Y casing",
               line_color = '#0D4C85'))

fig.add_trace(go.Scatter
              (x=df_casing["Y"], y=df_casing['Depth (m)'], mode = 'lines',
               line_color = '#0D4C85',showlegend=False))

#ADD TOLERANCE Traces

y = [0.25,43.71]
fig.add_trace(go.Scatter (x=[660,850], y=y, mode = 'lines',name='Tolerance',
                         line= dict(color = 'red',
                                     width = 2)))

fig.add_trace(go.Scatter (x=[-660,-850], y=y, mode = 'lines',showlegend=False,
                         line= dict(color = 'red',
                                     width = 2)))

#ADD FITLERED DATA
fig.add_trace(go.Scatter (x=df_filt['Y'], y=df_filt['Depth (m)'], mode = 'lines',showlegend=False,
                         line= dict(color = 'limegreen',
                                     width = 1.5)))
fig.add_trace(go.Scatter (x=df_filt["Y'"]*-1, y=df_filt['Depth (m)'], mode = 'lines',name= 'Processed Data',
                         line= dict(color = 'limegreen',
                                     width = 1.5)))


#ANNOTATIONS
fig.add_annotation( x=-710, y=-1, text="Y' Upstream",xanchor ='center',bordercolor='black', showarrow=False)
fig.add_annotation( x=710, y=-1, text="Y Downstream",xanchor ='center',bordercolor='black', showarrow=False)
fig.show()
