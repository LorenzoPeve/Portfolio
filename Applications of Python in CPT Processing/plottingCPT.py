import plotly
import ast
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
import processingCPT

"""This module has (3) functions and (1) global variable

plotScatterMap:
batchPlotParameter:
plotCPT: Plots X and Y array using CPT template and paramters given in dictionary (i.e., CPT Parameter-specific styling)
plotMapper: DICT with parameter-specific graph properties
"""
#HELPER FUNCTIONS

def typicalAxis():
    ax_style = dict(linecolor = 'black',
                        mirror=True,
                        ticks = 'outside',
                        tickmode = 'auto',
                        tickangle = 0,
                        showgrid=True,
                        gridcolor = '#D3D3D3',
                        zeroline = False,
                        title_font_size = 14)
    return ax_style
    
def tickGenerator(plotParams):
    """Arguments:
        plotParams : DICT with plotting parameters"""
    
    if 'majorTicksStart' in plotParams:
        start = 0
    else:
        start = plotParams['xlimits'][0]

    end   =     plotParams['xlimits'][1]
    step  =     plotParams['minorTicks']
    step_major =plotParams['majorTicks']

    if plotParams.get('floatingTicks'):
        xtickvals    = np.linspace(start, end, int((end-start)/step) +1 , endpoint=True) 
        mticks_array = np.arange(start,end+0.1,step_major)
        xticktext    = np.array([' ' if item not in mticks_array else item for item in xtickvals])
    else:
        xtickvals = np.linspace(start, end, int((end-start)/step) +1 , endpoint=True) 
        xticktext = np.array([' ' if item not in list(range(start,end+1,step_major)) else int(item) for item in xtickvals])
    
    if 'majorTicksStart' in plotParams:
    
        left_end = plotParams['xlimits'][0]
        arr_left_vals =  np.linspace(left_end, 0, abs(int(left_end/step)) , endpoint=False)
        arr_left_txt = np.array([' ' for item in arr_left_vals])
        xtickvals = np.append(arr_left_vals, xtickvals)
        xticktext = np.append(arr_left_txt, xticktext)
     
    return (xtickvals,xticktext)

plotMapper = dict(
                Tip_Resistance = dict(     xlimits      = [0,250] , 
                                           minorTicks   = 50 ,
                                           majorTicks   = 100 ,
                                           graphTitle   = '<b><i>Tip Resistance</i></b>',
                                           xTitle       = 'Tip Res., q<sub>c</sub> (tsf)',
                                           graphMode    = 'lines',
                                           graphSymbol  = None, 
                                           graphSymbolS = None,
                                           dataColor    = '#990033',  #Dark Red 
                                        ),  

                Corrected_Tip_Res = dict(  xlimits      = [0,250] , 
                                           minorTicks   = 50 ,
                                           majorTicks   = 100 ,
                                           graphTitle   = '<b><i>Corrected Tip Resistance</i></b>',
                                           xTitle       = 'Corrected Tip Res., q<sub>t</sub> (tsf)',
                                           graphMode    = 'lines',
                                           graphSymbol  = None, 
                                           graphSymbolS = None,
                                           dataColor    = '#990033',  #Dark Red 
                                        ),  
    
                Sleeve_Friction = dict(    xlimits      = [0,10] , 
                                           minorTicks   = 0.5 ,
                                           majorTicks   = 2 ,
                                           graphTitle   = '<b><i>Sleeve Friction</i></b>',
                                           xTitle       = 'Sleeve Friction, f<sub>s</sub> (tsf)',
                                           graphMode    = 'lines',
                                           graphSymbol  = None, 
                                           graphSymbolS = None,
                                           dataColor    = '#3366FF',  #Blueish 
                                        ),  
    
                Pore_Pressure = dict(      xlimits      = [-2000,12000] , 
                                           minorTicks   = 1000 ,
                                           majorTicks   = 5000 ,
                                           majorTicksStart = 0,    #When axis extends longer but you need ticks starting at another position
                                           graphTitle   = '<b><i>Pore Pressure</i></b>',
                                           xTitle       = 'Pore Pressure, u<sub>2</sub> (psf)',
                                           graphMode    = 'lines',
                                           graphSymbol  = None, 
                                           graphSymbolS = None,
                                           dataColor    = '#0066FF', #Blue-Green
                                           zeroLine     = True,  
                                        ),  
    
                Unit_Weight = dict(        xlimits      = [70,130] , 
                                           minorTicks   = 5 ,
                                           majorTicks   = 10 ,
                                           graphTitle   = '<b><i>Total Unit Weight</i></b>',
                                           xTitle       = "Total Unit Weight, \u03B3<sub>T</sub> (pcf)",
                                           graphMode    = 'lines',
                                           graphSymbol  = None, 
                                           graphSymbolS = None,
                                           dataColor    = '#934BC9',   #Purple
                                   ),
                I_SBT = dict(              xlimits      = [1,4] , 
                                           minorTicks   = 0.2 ,
                                           majorTicks   = 1 ,
                                           graphTitle   = '<b><i>SBT Index</i></b>',
                                           xTitle       = 'I<sub>SBT</sub>',
                                           graphMode    = 'lines',
                                           graphSymbol  = None, 
                                           graphSymbolS = None,
                                           dataColor    = '#002060',   #Dark Blue
                                   ),
                Norm_Tip_Res = dict(       xlimits      = [0,250] , 
                                           minorTicks   = 25 ,
                                           majorTicks   = 50 ,
                                           graphTitle   = '<b><i>Normalized Tip Resistance</i></b>',
                                           xTitle       = 'Norm. Tip Res., Q<sub>tn</sub>',                                           
                                           graphMode    = 'lines',
                                           graphSymbol  = None, 
                                           graphSymbolS = None,
                                           dataColor    = '#990033',  #Dark Red 
                                        ), 
                Norm_Friction_Ratio = dict(xlimits      = [0,10] , 
                                           minorTicks   = 0.5 ,
                                           majorTicks   = 2 ,
                                           graphTitle   = '<b><i>Normalized Friction Ratio</i></b>',
                                           xTitle       = 'Norm F<sub>R</sub> (%)',
                                           graphMode    = 'lines',
                                           graphSymbol  = None, 
                                           graphSymbolS = None,
                                           dataColor    = '#3366FF',  #Blueish 
                                        ),
                Pore_Press_Ratio_Bq = dict(xlimits      = [-0.5,1] , 
                                           minorTicks   = 0.25 ,
                                           majorTicks   = 0.5 ,
                                           graphTitle   = '<b><i>Pore Pressure Ratio</i></b>',
                                           xTitle       = 'B<sub>q</sub>',
                                           graphMode    = 'lines',
                                           graphSymbol  = None, 
                                           graphSymbolS = None,
                                           dataColor    = '#19999F',  #Blueish
                                           zeroLine     = True, 
                                           floatingTicks = True,
                                        ), 
    
                 Ic_index = dict(          xlimits      = [1,4] , 
                                           minorTicks   = 0.2 ,
                                           majorTicks   = 1 ,
                                           graphTitle   = '<b><i>I<sub>C</sub> Index</i></b>',
                                           xTitle       = 'I<sub>C</sub>',
                                           graphMode    = 'lines',
                                           graphSymbol  = None, 
                                           graphSymbolS = None,
                                           dataColor    = '#002060',   #Dark Blue
                                   ),
    
                 Friction_Angle = dict(    xlimits      = [25,50] , 
                                           minorTicks   = 2.5 ,
                                           majorTicks   = 5 ,
                                           graphTitle   = '<b><i>Effective Friction Angle</i></b>',
                                           xTitle       = "Friction Angle, \u03A6<sup>'</sup> (deg)",
                                           graphMode    = 'markers',
                                           graphSymbol  = 'circle-open', 
                                           graphSymbolS = 6,
                                           dataColor    = '#CC5500',   #Burnt Orange
                   ),
    
                 Su_Strength = dict(       xlimits      = [0,1500] , 
                                           minorTicks   = 250,
                                           majorTicks   = 500,
                                           graphTitle   = '<b><i>Undrained Shear Strength</i></b>',
                                           xTitle       = 'S<sub>u</sub> (psf)',
                                           graphMode    = 'lines',
                                           graphSymbol  = None,
                                           graphSymbolS = None,
                                           dataColor    = '#369A55',   #Dark Green
                   ),
                
                Precon_Pressure = dict(    xlimits      = [0,6000] , 
                                           minorTicks   = 1000,
                                           majorTicks   = 2000,
                                           graphTitle   = '<b><i>Pre-Consolidation & Eff. Stress</i></b>',
                                           xTitle       = "P<sup>'</sup><sub>P</sub> and \u03C3<sup>'</sup><sub>v</sub> (psf)",
                                           graphMode    = 'lines',
                                           graphSymbol  = None,
                                           graphSymbolS = None,
                                           dataColor    = '#D72FFF',   #Dark Pink/Purple
                   ),                  
                 )

def plotSoilLayersBATCH(fig, df_CPT_ALL, df_CPT_SOIL_ALL, df_CPT_SURVEY_ALL, soilLines, soilLabels, soilPatches, zText ):
    
    for jj in range(len(fig.data)):
        name = fig.data[jj].name
        elev = df_CPT_SURVEY_ALL.at[name,'Survey Elevation (ft)']
        topArr = df_CPT_SOIL_ALL.loc[name,'Top Depth'].to_numpy()
        topArr = elev - topArr
        botArr = np.append(topArr[1:], df_CPT_ALL.loc[name,'Elevation'].min())     #Append Graph y-lim
        depthArr_mx2 = np.array([topArr, botArr]).T
        colorArray = df_CPT_SOIL_ALL.loc[name,'RGB_val']
        clist = [ast.literal_eval(item) for item in colorArray]                             # '(r,g,b)' to (r,g,b) 
        clist = [(round(item[0],4) , round(item[1],4), round(item[2],4)) for item in clist] #  (r,g,b) with 4 significant figures
        clist = ['rgba' + str(item)[:-1] + ',0.7)' for item in clist]
        nameArr = df_CPT_SOIL_ALL.loc[name,'Layer Name'].to_numpy()
        
        if soilPatches:
            for ii in range(depthArr_mx2.shape[0]):         #Iterate through each row
                top, bot = depthArr_mx2[ii]
                color = colorArray[ii]
                fig.add_hrect(y0 = top, y1 = bot, fillcolor = 'rgb' + color, 
                              layer = 'below', 
                              line_width = 0,
                              row = 1, col = jj+1)
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=False)
            fig.update_traces(line_color = 'black')
            
                
        if zText:
            for ii in range(len(topArr)):          #Iterate through each row
        
                fig.add_annotation( x = 0.99,
                                    xanchor = "right",
                                    xref = 'x domain' if ii == 0 else 'x' + str(ii + 1) +' domain', 
                                    y = topArr[ii],
                                    yanchor = 'bottom',
                                    text= '{:.1f} ft'.format(round(topArr[ii],1)), 
                                    showarrow=False,
                                    font_family = 'Arial',
                                    font_color =  'black',
                                    row = 1, col = jj+1)
            
        if soilLabels:
            for ii in range(len(topArr)):          #Iterate through each row
                y_ave = np.average(depthArr_mx2[ii])
                fig.add_annotation( x = 0.5,
                                    xanchor = "center",
                                    xref = 'x domain' if ii == 0 else 'x' + str(ii + 1) +' domain', 
                                    y = y_ave,
                                    yanchor = 'middle',
                                    text= '<b><i>' + nameArr[ii] + '</i></b>', 
                                    showarrow = False,
                                    font_family = 'Arial',
                                    font_color =  'black',
                                    bgcolor = clist[ii],
                                    borderpad = 0, 
                                    borderwidth = 0,    
                                    row = 1, col = jj+1)
                
        if soilLines:
            for ii in range(len(topArr)):         #Iterate through each row
                fig.add_hline(y = topArr[ii], 
                                layer = 'below', 
                                line_color = 'black',
                                line_dash  = 'dashdot',
                                line_width = 1,
                                row = 1, col = jj+1)
                
            
    
    
    return fig  


#MAIN FUNCTIONS

def plotScatterMap( dfGEO,
                   colorDiscreteSeq, colorDiscreteOrder, legendTitle,
                   zoomUser = 16, mSize = 12):
    
        
    """This function...
    
    Arguments:
        df  :   pd.DataFrame with ['Array', 'Latitude', 'Longitude', 'colorArray'] 
                columns and CPT ID as index
        
                Array of interest should have an specific name ex. ('Min Su')
        """
    
    fig = px.scatter_mapbox(            dfGEO,
                                        lat = 'Latitude' , 
                                        lon = 'Longitude',
                                        hover_name  = dfGEO.index,
                                        hover_data = { dfGEO.columns[0]: ':.2f',
                                                      'Latitude'   : False,    #':.5f' ,
                                                      'Longitude'  : False,    #':.5f',    
                                                      'colorArray' : False},
                                        color = 'colorArray',
                                        color_discrete_sequence = colorDiscreteSeq,
                                        category_orders = { 'colorArray' : colorDiscreteOrder}
                                        )
    
    
    
    fig.update_layout(mapbox_style =    "white-bg",
                      mapbox_layers = [{
                                        "below": 'traces',
                                        "sourcetype": "raster",
                                        "sourceattribution": "United States Geological Survey",
                                        "source":  ["https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"]
                                        }],
    
                      mapbox     = dict(zoom = zoomUser))
    
    fig.update_traces(marker     = dict(size=mSize),
                      hoverlabel = dict (bgcolor = '#FFFFFF'))
        
    fig.update_layout(legend = dict(    title_text = legendTitle,
                                        bgcolor = '#FFFFFF',
                                        bordercolor = '#FFFFFF',
                                        xanchor = 'right',
                                        yanchor = 'top',
                                        x = 0.99,
                                        y = 0.95),
                      font   = dict(    family = 'Arial', 
                                        color = 'black'))
    
    return fig

def plotScatterMap_SimpleScatter( dfGEO, zoomUser = 16, mSize = 12):
    
        
    """This function...
    
    Arguments:
        df  :   pd.DataFrame with ['Array', 'Latitude', 'Longitude'] 
                columns and CPT ID as index
        
                Array of interest should have an specific name ex. ('Min Su').
                That name is used for the legend.
                Continuous colorscale with median as midpoint
        """
    dfGEO = dfGEO.copy()
    dfGEO['colorArray'] = dfGEO.iloc[:,0]
    fig = px.scatter_mapbox(            dfGEO,
                                        lat = 'Latitude' , 
                                        lon = 'Longitude',
                                        hover_name  = dfGEO.index,
                                        hover_data = { dfGEO.columns[0]: ':.2f',
                                                      'Latitude'   : False,    #':.5f' ,
                                                      'Longitude'  : False,    #':.5f',    
                                                      'colorArray' : False},
                                        color = 'colorArray',
                                        color_continuous_scale  = plotly.colors.diverging.Picnic,
                                        color_continuous_midpoint  = round(dfGEO.iloc[:,0].median(),1)
                                        )
    
    
    
    fig.update_layout(mapbox_style =    "white-bg",
                      mapbox_layers = [{
                                        "below": 'traces',
                                        "sourcetype": "raster",
                                        "sourceattribution": "United States Geological Survey",
                                        "source":  ["https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"]
                                        }],
    
                      mapbox     = dict(zoom = zoomUser))
    
    fig.update_traces(marker     = dict(size=mSize),
                      hoverlabel = dict (bgcolor = '#FFFFFF'))
        
    fig.update_layout(font   = dict(    family = 'Arial', color = 'black'))
    fig.update_coloraxes(colorbar_title_text = dfGEO.columns[0],
                         colorbar_ticks = 'outside',
                         colorbar_dtick = 2,
                         colorbar_tick0 = -15)
    
    return fig


def batchPlotParameter(df_CPT_ALL,cpt_list,parameter,**kwargs):
    
    # Dictionary with attributes for each Parameter
    plotMapper = {  'Sleeve Friction' :  [ 0, 10, 0.5, 2, 'Sleeve Friction (tsf)','lines'],
                'Tip Res.' : [ 0, 250, 25, 50, 'Tip. Res. (tsf)','lines'],
                'Corrected Tip Res.' : [ 0, 250, 25, 50, 'Corrected Tip. Res. (tsf)','lines'],
                'Pore Pressure_cpt': [0, 12000, 1000, 5000,'Pore Pressure<br>u<sub>2</sub> (psf)','lines'],
                'Normalized Fr' : [0, 10, 0.5, 2,'Norm. Friction Ratio<br>F<sub>R</sub> (%)','lines'],
                #'PP Ratio Bq',  
                #'Exp_n_iter', 
                'Normalized Tip_Qt_n_iter':  [0, 250, 25, 50, 'Normalized Tip Res.<br>Q<sub>tn</sub>','lines'],
                'Ic_iter' : [1, 4, 0.2, 1 ,'I<sub>c</sub>','lines'],
                'Corr. Friction Angle' : [25, 50, 2.5, 5,"Friction Angle<br>\u03A6<sup>'</sup> (deg)",'markers'],
                'Corr. Su' : [0, 1500, 100, 500 ,"Undrained Shear Strength<br>S<sub>u</sub> (psf)",'lines']
             }
    
    #Dictionary for General Axis Properties
    def typicalAxis():
    
        ax_style = dict(linecolor = 'black',
                    mirror=True,
                    ticks = 'inside',
                    tickmode = 'auto',
                    tickangle = 0,
                    showgrid=True,
                    gridcolor = '#D3D3D3',
                    zeroline = False,)
        return ax_style  

    layout = go.Layout(
                        font = dict(family = 'Arial', color = 'black'), #Sets the global font
                        width = 500,
                        height = 800,
                        plot_bgcolor='#FFF',  # Sets background color to white
                        xaxis= typicalAxis(),
                        yaxis= typicalAxis() )
    
    fig = go.Figure(layout = layout)
    
    #PLOT EACH TRACE
    for item, lineColor in zip(cpt_list,plotly.colors.qualitative.G10):
        
        yArr = df_CPT_ALL.loc[item,'Elevation']
        depth_arr = df_CPT_ALL.loc[item,'Depth']
        
        if kwargs['filterData']:
            
            if kwargs['filterMode'] == 'Settle3D':
                xArr,yArr = processingCPT.filterCPT_settle3d(df_CPT_ALL.loc[item,parameter].to_numpy(),
                                                             depth_arr, yArr, 
                                                             kwargs['wSizeSettle'], BS = 1)
                print(len(xArr),len(df_CPT_ALL.loc[item]) )
            else:
                xArr = processingCPT.filterCPT(df_CPT_ALL.loc[item,parameter],**kwargs)
        else:
            print('ACA')
            xArr = df_CPT_ALL.loc[item,parameter]
            
        fig.add_trace(go.Scatter(
                                    x = xArr,
                                    y = yArr,
                                    name = item,
                                    line_color=  lineColor,
                                    mode = plotMapper[parameter][-1],
                                    marker_symbol = "circle",
                                    marker_size = 6,
                                    line_width = 2))
    
    #STYLING
    start = plotMapper[parameter][0]
    end = plotMapper[parameter][1]
    step = plotMapper[parameter][2]
    step_major = plotMapper[parameter][3]
    xtickvals = np.linspace(start, end, int((end-start)/step) +1 , endpoint=True) 
    xticktext = np.array([' ' if item not in list(range(start,end+1,step_major)) else int(item) for item in xtickvals])
               
    fig.update_layout(xaxis=dict(   range = plotMapper[parameter][:2],
                                    tickmode = 'array',
                                    tickvals = xtickvals,
                                    ticktext = xticktext,
                                    title = plotMapper[parameter][4]),
                      yaxis=dict(   range = [-40,45],
                                    tickmode = 'linear',
                                    tick0 = -40,
                                    dtick = 5,
                                    title = 'Elevation (ft)'))                 
        
    return fig


def plotCPT(xArr, yArr, depthArr, plotParams, ylimits = [-40,45], graphWidth = 500, graphHeight = 800, lWidth = 2):
    
    """This function plots an X and Y array using a template for CPT graphs. 
        It takes a dictionary "plotParams" with the plotting parameters 
        (i.e., x_limits, axis labels, markers/lines type and color, etc.)
        
        xArr, yArr : ARRAYS or LISTLIKE
        depthArr : ARRAYS or LISTLIKE for hoverdata
        plotParams : DICT with plotting info
        ylimits =: LIST ex. [-40,45]
        graphWidth = 500
        graphHeight = 800
        lWidth = 2
        """
    #SETTING FIGURE LAYOUT
    layout = go.Layout(
                                font = dict(family = 'Arial', color = 'black'), #Sets the global font
                                title_font_size = 14,
                                width = graphWidth,
                                height = graphHeight,
                                plot_bgcolor='#FFF',  # Sets background color to white
                                xaxis= typicalAxis(),
                                yaxis= typicalAxis() )
    
    fig = go.Figure(layout = layout)
    
    #ADDING DATA
    fig.add_trace(go.Scatter(   x = xArr,
                                y = yArr,
                                marker_color=    plotParams['dataColor'],
                                mode =           plotParams['graphMode'],
                                marker_symbol =  plotParams['graphSymbol'],
                                marker_size =    plotParams['graphSymbolS'],
                                marker_line_width = 1.5,
                                line_width = lWidth,
                                hoverlabel_bgcolor = '#FFFFFF',
                                hoverlabel_bordercolor = '#000000',
                                xhoverformat = ".1f",
                                yhoverformat = ".1f",
                                text = depthArr,
                                hoverinfo = 'x+y+text',
                                showlegend = False))
                         
    #STYLING
    # (1) Setting Ticks
        #This is needed to simulate a major/minor grid structure with text labels ONLY at major grid ticks.
    xtickvals,xticktext = tickGenerator(plotParams)
    
    # (2) Updating Layout
    fig.update_layout(
                title = dict(   text     =       plotParams['graphTitle'],
                                xanchor  =       'center',
                                x        =        0.5, 
                                xref     =        'paper',
                                yanchor  =       'bottom',
                                yref     =       'paper',
                                y        =        1,
                                pad_b    =        10),
                   
                xaxis = dict(   range    =       plotParams['xlimits'],
                                tickmode =       'array',
                                tickvals =       xtickvals,
                                ticktext =       xticktext,
                                title    =       plotParams['xTitle'],
                                ),
                yaxis = dict(   range    =       ylimits,
                                tickmode =       'linear',
                                tick0    =       ylimits[0],
                                dtick    =       5,
                                title    =       'Elevation (ft)'))   
    
    if plotParams.get('zeroLine'):
        fig.update_xaxes(zeroline = True , zerolinecolor = '#9D9D9D'  ) 
    
    return fig



def plotSoilLayers(fig, depthArr_mx2, colorArray):
    """This function takes a:
        fig: plotly.graph_objs._figure.Figure;
        depthArr_mx2: [(top_elev, bottom_elev),....] for each soil layer;
        colorArray: for each soil layer"""
    
    for ii in range(depthArr_mx2.shape[0]):         #Iterate through each row
        top, bot = depthArr_mx2[ii]
        color = colorArray[ii]
        fig.add_hrect(y0 = top, y1 = bot, fillcolor = 'rgb' + color, 
                      layer = 'below', 
                      line_width = 0,)
    
    return fig

def plotSoilLayersELEVText(fig, depthArr,
                        xPos = 0.99, yshift = 0, fSize =12):
    """This function takes a:
        fig: plotly.graph_objs._figure.Figure;
        depthArr : Top elevation for each soil layer
        """
    #IF integer provided - Create array of repeated value to work with for loop
    if type(xPos) == int or type(xPos) == float:
        xPos = np.full(depthArr.shape, xPos)
        
    if type(yshift) == int or type(yshift) == float:
        yshift = np.full(depthArr.shape[0], yshift)   
        
    for ii in range(len(depthArr)):          #Iterate through each row
        
        fig.add_annotation( x = xPos[ii],
                            xanchor = "right",
                            xref = 'paper',
                            y = depthArr[ii],
                            yanchor = 'bottom',
                            text= '{:.1f}'.format(round(depthArr[ii],1)), #'<b><i>' + nameArr[ii] + '</i></b>',
                            showarrow=False,
                            yshift= yshift[ii],
                            font_family = 'Arial',
                            font_color =  'black')       
    return fig

def plotSoilLayersLines(fig, depthArr):

    """This function takes a:
        fig: plotly.graph_objs._figure.Figure;
        depthArr : Top elevation for each soil layer
        """
            
    for ii in range(len(depthArr)):         #Iterate through each row
        
        fig.add_hline(y = depthArr[ii], 
                        layer = 'below', 
                        line_color = 'black',
                        line_dash  = 'dashdot',
                        line_width = 1.5)
    
    return fig

def plotSoilLabels(fig, depthArr_mx2, nameArr, 
                   xPos = 0.2, yshift = 0 , colorArray ='rgba(255,255,255,0.7)',
                   fColor = '#000000', fSize =12):
    
    """This function takes a:
        fig: plotly.graph_objs._figure.Figure;
        depthArr_mx2: [(top_elev, bottom_elev),....] for each soil layer;
        nameArr : Layer Name
        xpos : int (0 to 1) or array of floats (0 to 1) to give the x_pos relative to the x-axis.
               Allows same position for all labels, or label-specific positioning.
        yshift : int or array of int (default = 0). 
                 Specify global yshift or label specific shift (+ or -) from the calculated y_position
        colorArray: Specify textbox background color. If one, color given, then, propagated for all labels.
                    'rgba(255,255,255,0.7)'
        """
    #IF integer provided - Create array of repeated value to work with for loop
    if type(xPos) == int or type(xPos) == float:
        xPos = np.full(depthArr_mx2.shape[0], xPos)
        
    if type(yshift) == int or type(yshift) == float:
        yshift = np.full(depthArr_mx2.shape[0], yshift)   
        
    if type(colorArray) == str:
        colorArray = np.full(depthArr_mx2.shape[0], colorArray)
    
    for ii in range(depthArr_mx2.shape[0]):         #Iterate through each row
        
        y_ave = np.average(depthArr_mx2[ii])
        fig.add_annotation( x = xPos[ii],
                            xanchor = "left",
                            xref = 'paper',
                            y = y_ave,
                            yanchor = 'middle',
                            text= '<b><i>' + nameArr[ii] + '</i></b>', 
                            showarrow=False,
                            yshift= yshift[ii],
                            opacity = 1,
                            font_family = 'Arial' ,
                            font_color =  fColor,
                            font_size  = fSize,
                            bgcolor = colorArray[ii],
                            borderpad = 0, 
                            borderwidth = 0)       
        
    return fig

def plotDPTLines(fig, depthArr, xlims):

    """This function takes a:
        fig: plotly.graph_objs._figure.Figure;
        depthArr : Top elevation for each soil layer
        """
         
    for ii in range(len(depthArr)):         #Iterate through each row
        if ii == 0: #Add Legend to only the first
            fig.add_trace(go.Scatter( x = xlims , y = [depthArr[ii],depthArr[ii] ], showlegend = True,
                                      mode = 'lines', line_color = '#12F2E2', line_dash = 'dash', line_width = 3,
                                      name = 'DPT Interfaces'))
        else:
            fig.add_trace(go.Scatter( x = xlims , y = [depthArr[ii],depthArr[ii] ], showlegend = False,
                                      mode = 'lines', line_color = '#12F2E2', line_dash = 'dash', line_width = 3))

    return fig

def plotSurface(xArr_CPT, yArr_CPT, zArr_CPT,
                simplices, cpt_ids,
                xArr_DPT, yArr_DPT, zArr_DPT,dpt_ids, df):

    
    min_z = np.floor(min(zArr_DPT.min(),zArr_CPT.min()))
    max_z = np.ceil(max(zArr_DPT.max(),zArr_CPT.max()))
    
    fig = plotly.figure_factory.create_trisurf(x=xArr_CPT, y=yArr_CPT, z=zArr_CPT,
                                 simplices=simplices,
                                 plot_edges = False,
                                 colormap = plotly.colors.diverging.Geyser,
                                 backgroundcolor = '#655F5F'  ,          #'rgb(150, 150, 150)',
                                 aspectratio=dict(x=1.3, y=1.3, z=0.3),
                                 height = 800,
                                 width = 1000)

    fig.update_traces(hoverinfo = 'skip', selector=dict(type='mesh3d'))
    
    fig.update_traces(marker_cmin = min_z, marker_cmax = max_z,
                      marker_colorbar = dict(   x = -0.2 , 
                                                len = 0.6,
                                                title  ='Interface Elevation (ft)',
                                                ticks = "outside",
                                                tick0 = 0 ,
                                                dtick = 1), selector=dict(type='scatter3d'))
        
    fig2 = px.scatter_3d(df, x = 'Longitude', y='Latitude', z='Elevation_TC',
                          color= 'delta_DPT_color', 
                          color_discrete_map = {'CPT Locations' : 'blue',
                                                'CPT > T' : '#D83434', 
                                                'CPT <= T' : '#00FA71'},
                         hover_name  = df.index, 
                         hover_data = { 'Latitude'   : False ,
                                        'Longitude'  : False,
                                        'delta_DPT_color'  : False},)
    #Add CPT Locacions
    fig.add_trace(fig2.data[0])
    
    #ADD DPT CO-locations
    fig.add_trace(go.Scatter3d( z = zArr_DPT, 
                                x = xArr_DPT, 
                                y = yArr_DPT,
                                marker_symbol = "square" ,
                                marker_color = '#FF00FF',
                                marker_size = 6,
                                mode='markers',
                                name = 'DPT Locations',
                                surfacecolor = '#FF99CC' ,
                                surfaceaxis = 2,
                                text = dpt_ids ))
    
    #Add Colored  CPT locations
    fig.add_trace(fig2.data[1])
    fig.add_trace(fig2.data[2])
    
    #Update Layout
    fig.update_layout(  title = dict( text = 'CCR-Clay Interface Elevation',
                                      xanchor = 'center',
                                      yanchor = 'top',
                                      x = 0.5,
                                      y = 0.95),
                        font = dict(  family = 'Arial', 
                                      color = 'black'),
                        legend=dict( x=0.85,  y=1.0, xanchor = 'right', yanchor = 'top'))
    
    fig.update_scenes( zaxis_range = [min_z -1.5 ,max_z + 1.5 ])
      
    return fig



def batchPlotParameter_STACKED(df_CPT_ALL, cpt_list, parameter, 
                               checkFilterData,
                               dropdownFilterMode,
                               wSize,
                               wSizeSettle3D,
                               plotParams, 
                               xlimitsSTR,
                               ylimits = [-40,45],
                               graphWidth = 1000, graphHeight = 600, lWidth = 2):
   
    fig = make_subplots(rows=1, cols=len(cpt_list)+1,shared_yaxes=True,
                        subplot_titles= cpt_list)
    for item, lineColor, jj in zip(cpt_list,plotly.colors.qualitative.G10,range(1,len(cpt_list)+1)):
        
        if parameter ==  'Pore Pressure_cpt':
            xArr = (df_CPT_ALL.loc[item,parameter] * 2000).to_numpy()
        else:
            xArr = df_CPT_ALL.loc[item,parameter].to_numpy()
        yArr = df_CPT_ALL.loc[item,'Elevation']
        
        
        #Filtering Step
        if checkFilterData.value:
            
            if dropdownFilterMode.value == 'Settle3D':
                depth_arr = df_CPT_ALL.loc[item,'Depth']
                xArr,yArr = processingCPT.filterCPT_settle3d(xArr,depth_arr, yArr, 
                                                             widthSize = wSizeSettle3D, BS = 1)
            else:
                xArr = processingCPT.filterCPT(xArr, filterMode = dropdownFilterMode.value, wSize = wSize)
       
        #ADD TRACE
        fig.add_trace(go.Scatter(x          = xArr,
                                 y          = df_CPT_ALL.loc[item,'Elevation'],
                                 name       = item,
                                 line_color = lineColor,
                                 line_width = lWidth), 
                                 row        = 1,
                                 col        = jj)
        
    #STYLING
        # (1) Setting Ticks        
    xtickvals,xticktext = tickGenerator(plotParams)

    # (2) Updating Layout

    fig.update_xaxes(**typicalAxis())
    fig.update_yaxes(**typicalAxis())

    fig.update_layout(plot_bgcolor = '#FFFFFF', showlegend = False, font = dict(family = 'Arial', color = 'black'),
                     width = graphWidth , height = graphHeight,
                     yaxis = dict(title = 'Elevation (ft)'))

    fig.update_xaxes(range   =       plotParams['xlimits'],
                    tickmode =       'array',
                    tickvals =       xtickvals,
                    ticktext =       xticktext,
                    title    =       plotParams['xTitle'])
    
    if plotParams.get('zeroLine'):
        fig.update_xaxes(zeroline = True , zerolinecolor = '#9D9D9D'  )
        
    if len(xlimitsSTR) > 0:
        xRange = [float(item) for item in xlimitsSTR.strip('[]').split(',')]
        fig.update_xaxes(range = xRange, tickmode ='auto')
    
    if len(ylimits) > 0 and type(ylimits) == str:
        yRange = [float(item) for item in ylimits.strip('[]').split(',')]
        fig.update_yaxes(range = yRange, tickmode = 'linear', dtick = 1)
    else:
        ylimits = [-40,45]
        fig.update_yaxes(range = ylimits, tickmode = 'linear', tick0 = ylimits[0],  dtick = 5)
                      
    return fig