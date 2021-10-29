# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 17:34:47 2021

@author: LPeve
"""


import plotly.graph_objects as go
import numpy as np
import pandas as pd
import plotly.express as px








def Roberston2010(x, y, color, width, height, g_title='', rob2010_points = None):
     
    x_ticks_vals = np.append(np.arange(0.1,0.99,0.1), np.arange(1,11,1))
    x_ticks_text = np.array([' ' if item not in [0.1,1,10] else item for item in x_ticks_vals])
    y_ticks_vals = np.concatenate([ np.arange(1,10,1), np.arange(10,100,10),  np.arange(100,1001,100) ])
    y_ticks_text = np.array([' ' if item not in [1,10,100,1000] else item for item in y_ticks_vals])
    
    layout = go.Layout(
                        font = dict(family = 'Arial', color = 'black'), #Sets the global font
                        width = width,
                        height = height,
                        title = dict(text = g_title,x = 0.5,xref = 'paper',xanchor = 'center'),
                        plot_bgcolor='#FFF',  # Sets background color to white
                        xaxis=dict(
                            title = 'Friction Ratio, R<sub>f</sub> (%)', 
                            linecolor = 'black',  
                            mirror=True,
                            type = 'log',
                            range = [-1,1],
                            ticks = 'inside',
                            ticklen = 10,
                            tickmode = 'array',
                            tickvals = x_ticks_vals ,
                            ticktext = x_ticks_text,
                            tickangle = 0
                            
                        ),
                        yaxis=dict(
                            title = 'Norm. Cone Resistance (q<sub>c</sub>/P<sub>a</sub>)',  
                            linecolor = 'black',  
                            mirror=True,
                            type = 'log',
                            range = [0,3],
                            ticks = 'inside',
                            ticklen = 10,
                            tickmode = 'array',
                            tickvals = y_ticks_vals ,
                            ticktext = y_ticks_text
                            
                        ),
                        legend = dict(title='Depth Ranges (ft)')
                        )
    if len(np.unique(color)) <= 1:
         fig = px.scatter(x = x, y = y, color=color)
    else:
        fig = px.scatter(x = x, y = y, color=color, color_discrete_sequence = px.colors.qualitative.Dark24)  
    
    #Add CPT Zoning
    if rob2010_points:
        
        aa = 0.8
        fig.add_trace(go.Scatter(x=rob2010_points['zone1']['x'], y=rob2010_points['zone1']['y'], mode = 'lines',
                                 marker_color = '#808080', marker_opacity = aa, showlegend=False))
        
        fig.add_trace(go.Scatter(x=rob2010_points['zone3']['x'], y=rob2010_points['zone3']['y'], mode = 'lines',
                                 marker_color = '#808080', marker_opacity = aa, showlegend=False)) 
        
        fig.add_trace(go.Scatter(x=rob2010_points['zone4']['x'], y=rob2010_points['zone4']['y'], mode = 'lines',
                                 marker_color = '#808080',marker_opacity = aa, showlegend=False)) 
        
        fig.add_trace(go.Scatter(x=rob2010_points['zone5']['x'], y=rob2010_points['zone5']['y'], mode = 'lines',
                                 marker_color = '#808080',marker_opacity = aa, showlegend=False)) 
        
        fig.add_trace(go.Scatter(x=rob2010_points['zone6']['x'], y=rob2010_points['zone6']['y'], mode = 'lines',
                                 marker_color = '#808080',marker_opacity = aa, showlegend=False)) 
        
        fig.add_trace(go.Scatter(x=rob2010_points['zone7']['x'], y=rob2010_points['zone7']['y'], mode = 'lines',
                                 marker_color = '#808080',marker_opacity = aa, showlegend=False)) 
        
        fig.add_trace(go.Scatter(x=rob2010_points['zone8']['x'], y=rob2010_points['zone8']['y'], mode = 'lines',
                                 marker_color = '#808080',marker_opacity = aa, showlegend=False)) 
        
        fig.add_trace(go.Scatter(x=rob2010_points['zone9']['x'], y=rob2010_points['zone9']['y'], mode = 'lines',
                                 marker_color = '#808080',marker_opacity = aa, showlegend=False)) 
        
        
        #Add CPT Zoning Labels
        fig.add_annotation(x=np.log10(0.3), y=np.log10(3), text='<b>1</b>',showarrow = False)
        fig.add_annotation(x=np.log10(6.5), y=np.log10(2), text='<b>2</b>',showarrow = False)
        fig.add_annotation(x=np.log10(2), y=np.log10(3), text='<b>3</b>',showarrow = False)
        fig.add_annotation(x=np.log10(0.9), y=np.log10(8), text='<b>4</b>',showarrow = False)
        fig.add_annotation(x=np.log10(0.5), y=np.log10(20), text='<b>5</b>',showarrow = False)
        fig.add_annotation(x=np.log10(0.3), y=np.log10(90), text='<b>6</b>',showarrow = False)
        fig.add_annotation(x=np.log10(0.2), y=np.log10(550), text='<b>7</b>',showarrow = False)
        fig.add_annotation(x=np.log10(3), y=np.log10(550), text='<b>8</b>',showarrow = False)
        fig.add_annotation(x=np.log10(6.5), y=np.log10(450), text='<b>9</b>',showarrow = False)
    
    fig.update_layout(layout)
    return fig

def Roberston2010_points():
    
    df = pd.read_csv('RobPoints.csv')
    rob2010_points = {}
    rob2010_points['zone1'] = df.iloc[:,[0,1]].dropna(how='any')
    
    zone3 = df.iloc[:,[2,3]].dropna(how='any')
    zone3.columns = ['x','y']
    rob2010_points['zone3'] = zone3
    
    zone4 = df.iloc[:,[4,5]].dropna(how='any')
    zone4.columns = ['x','y']
    rob2010_points['zone4'] = zone4
    
    zone5 = df.iloc[:,[6,7]].dropna(how='any')
    zone5.columns = ['x','y']
    rob2010_points['zone5'] = zone5
        
    zone6 = df.iloc[:,[8,9]].dropna(how='any')
    zone6.columns = ['x','y']
    rob2010_points['zone6'] = zone6
    
    zone7 = df.iloc[:,[10,11]].dropna(how='any')
    zone7.columns = ['x','y']
    rob2010_points['zone7'] = zone7
    
                    
    zone8 = df.iloc[:,[12,13]].dropna(how='any')
    zone8.columns = ['x','y']     
    rob2010_points['zone8'] = zone8
                    
    zone9 = df.iloc[:,[14,15]].dropna(how='any')
    zone9.columns = ['x','y']  
    rob2010_points['zone9'] = zone9
                    
    nc_1 = df.iloc[:,[16,17]].dropna(how='any')
    nc_1.columns = ['x','y']  
    rob2010_points['nc_1'] = nc_1
                   
    nc_2 = df.iloc[:,[18,19]].dropna(how='any')
    nc_2.columns = ['x','y']   
    rob2010_points['nc_2'] = nc_2
    
    return (rob2010_points)



def cptBasicChart(x, y, color, width, height, g_title=''):
    
    layout = go.Layout(
                        font = dict(family = 'Arial', color = 'black'), #Sets the global font
                        width = width,
                        height = height,
                        title_text = g_title,
                        plot_bgcolor='#FFF',  # Sets background color to white
                        xaxis=dict(
                            title = 'Friction Ratio, Rf', 
                            linecolor = 'black',  
                            mirror=True,
                            ticks = 'inside',
                            ticklen = 10,
                            tickmode = 'linear',
                            tickangle = 0
                            
                        ),
                        yaxis=dict(
                            title = 'Cone Resistance (q<sub>c</sub>/P<sub>a</sub>)',  
                            linecolor = 'black',  
                            mirror=True,
                            type = 'log',
                            range = [0,3],
                            ticks = 'inside',
                            ticklen = 10,
                            tickmode = 'array',
                            dtick = 1                            
                        )
                        )
    fig = px.scatter(x=rf,y = qc_pa,color=raw_data['Category'])
    #data = go.Scatter(x=x, y=y, mode = 'markers' , marker = dict(color = color) )
    #fig = go.Figure(data=data, layout=layout)
    fig.update_layout(layout)
    
    return fig

def Rob_1990_NORM():
    fig.add_trace(go.Scatter(x=nc_1['x'], y=nc_1['y'], mode = 'lines',marker_color = '#808080',
                             marker_opacity = aa , line_dash = 'dash', showlegend=False)) 
    fig.add_trace(go.Scatter(x=nc_2['x'], y=nc_2['y'], mode = 'lines',marker_color = '#808080',
                             marker_opacity = aa , line_dash = 'dash', showlegend=False)) 