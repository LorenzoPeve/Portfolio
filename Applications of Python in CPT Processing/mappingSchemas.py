

import numpy as np
import pandas as pd
import mapclassify as mc
import plotly

       
def classiSchema(arr, mode = 'Equal_Interval', **kwargs):
    
    """This function takes an array and returns.
    
    Keyword arguments:
        array      :  np.array (DATA)
        mode       : STR - Data Classification mode. One of
                     ['Threshold','Equal_Interval', 'Quantiles', 'Maximum_Breaks',
                      'Natural_Breaks','Percentiles','StdMean','User_Defined',
                      'BestFit']
                     
                     
        colorScale : plotly.colorscale
        AutoSearch : bool       allows for algorithm autosearch in Maximum breaks/Natural Breaks
        k          : int        Number of Intervals. Default is 4
        pct
        bins
        desValue : for mode = 'Threshold'
        parameter : When using Boolean Criterion which
        
    
    1) 'Threshold'
    2) User Defined
    3) 'Boolean_Criterion'
    
    
    4) Map Schema
    Depending on the mode, the function first returns a mapclassify.classifiers (mcOut) with the following attributes:
        mcOut.bins = the upper bounds of each class
        mcOut.yb   = bin ids for observations (0 to k-1)
        mcOut.k    = the number of classes
        
    This mcOUT is passed to either:
        
        colorProps_from_intervals() : 
                   1) uses the STR representation of the intervals and 
                   mapping of the y codes. Array of Strings ("colorSTRArray") for px.Express.
                   2) colorDiscreteSeq
                   3) colorDiscreteOrder 
                
                   Equal_Interval ; Quantiles ; Maximum_Breaks ; Natural_Breaks ; BestFit
    
    Returns
        colorSTRArray : Array of Strings ("colorSTRArray") for px.Express. 
                        Intervals '(0, 500]' ; Membership String ex. 'Passing'
        colorDiscreteSeq : List of RGB colors ['rgb(255, 241, 169)', 'rgb(254, 171, 73)',...]
        colorDiscreteOrder : List of ORDERED (low to high) bins/intervals to have an intensity-increasing legend
        legendTitle : String with data classifier characteristics (k, etc)
        """
        
    
    
    if 'colorScale' not in kwargs:
            kwargs['colorScale'] = plotly.colors.sequential.YlOrRd
            
    if 'AutoSearch' not in kwargs:
            kwargs['AutoSearch'] = False
     
    # (1) Threshold
    if mode == 'Threshold':
        
        if 'desValue' not in kwargs:
            kwargs['desValue'] = 500
        
        colorSTRArray = np.where(arr >= kwargs['desValue'] , 'Passing' , 'Not Passing'   )
        colorDiscreteSeq = ['#00FA71', '#D83434']
        colorDiscreteOrder = ['Passing','Not Passing']
        legendTitle = 'S<sub>u</sub> Criteria >= ' +  str(kwargs['desValue']) + ' psf'
        return (colorSTRArray,colorDiscreteSeq,colorDiscreteOrder,legendTitle)
    
    # (2) User-Defined
    if mode == 'User_Defined':
        
        #Default Value
        if 'bins' not in kwargs:
            kwargs['bins'] = [0,500,1000,1500]
            
        #Get Categorical Array & Get INT Codes
        catArray = pd.cut(arr,kwargs['bins'],right=True , precision= 1)
        s1 = pd.Series(catArray.codes)
        
        #Create DICT in form of {0:interval_one, 1:interval_2} and Map
        mapDict = { x : str(catArray.categories[x])  for x in range(len(catArray.categories))}
        colorSTRArray = s1.map(mapDict).to_numpy()
        
        #Color Sequence and Order
        colorDiscreteSeq = plotly.colors.sample_colorscale( kwargs['colorScale'] , len(catArray.categories) , low = 0.1 )        
        colorDiscreteOrder =  sorted(list(mapDict.values()),key = lambda x : float(x.split(',')[0][1:]))
        
        legendTitle = 'User_Defined Intervals'
        
        return (colorSTRArray,colorDiscreteSeq,colorDiscreteOrder,legendTitle)
    
    # (3) Layer Boolean Criterion
    if mode == 'Boolean_Criterion':
        
        colorSTRArray = np.where(arr == True, 'Zone Present' , 'Zone NOT Present'   )
        colorDiscreteSeq = ['#00FA71', '#D93BA8']
        colorDiscreteOrder = ['Zone NOT Present', 'Zone Present']
                       
        legendTitle = 'Boolean_Criterion'
        return (colorSTRArray,colorDiscreteSeq,colorDiscreteOrder,legendTitle)
    
    
    if mode == 'Equal_Interval':
        if 'k' not in kwargs:
            kwargs['k'] = 4
        
        mcOut = mc.EqualInterval(arr, kwargs['k'])
        colorSTRArray, colorDiscreteSeq ,colorDiscreteOrder = colorProps_from_intervals(mcOut, kwargs['colorScale'] )
        legendTitle = 'Equal_Interval Schema (k=' + str(kwargs['k']) +')'
        return (colorSTRArray, colorDiscreteSeq ,colorDiscreteOrder ,legendTitle)
    
    
    if mode == 'Quantiles':
        if kwargs['AutoSearch']:
            mcOut = mc.gadf(arr, method='Quantiles', maxk=12, pct=0.8)[1]
            kwargs['k'] = len(mcOut.bins)
        else:
            if 'k' not in kwargs:
                kwargs['k'] = 4
            mcOut = mc.Quantiles(arr, kwargs['k'])
       
        colorSTRArray, colorDiscreteSeq ,colorDiscreteOrder = colorProps_from_intervals(mcOut, kwargs['colorScale'] )
        legendTitle = 'Quantiles Schema (k=' + str(len(mcOut.bins)) +')'
        return (colorSTRArray,colorDiscreteSeq,colorDiscreteOrder,legendTitle)
    
    if mode == 'Maximum_Breaks':
        if kwargs['AutoSearch']:
            mcOut = mc.gadf(arr, method='MaximumBreaks', maxk=12, pct=0.8)[1]
            kwargs['k'] = len(mcOut.bins)
        else:
            if 'k' not in kwargs:
                kwargs['k'] = 4
            mcOut = mc.MaximumBreaks(arr, kwargs['k'])
        
        colorSTRArray, colorDiscreteSeq ,colorDiscreteOrder = colorProps_from_intervals(mcOut, kwargs['colorScale'] )
        legendTitle = 'Maximum_Breaks Schema (k=' + str(len(mcOut.bins)) +')'
        return (colorSTRArray,colorDiscreteSeq,colorDiscreteOrder,legendTitle)

    if mode == 'Natural_Breaks':
        if kwargs['AutoSearch']:
            mcOut = mc.gadf(arr, method='NaturalBreaks', maxk=12, pct=0.8)[1]
            kwargs['k'] = len(mcOut.bins)
        else:
            if 'k' not in kwargs:
                kwargs['k'] = 4
            mcOut = mc.NaturalBreaks(arr, kwargs['k'])
        
        colorSTRArray, colorDiscreteSeq ,colorDiscreteOrder = colorProps_from_intervals(mcOut, kwargs['colorScale'] )
        legendTitle = 'Natural_Breaks Schema (k=' + str(len(mcOut.bins)) +')'
        return (colorSTRArray,colorDiscreteSeq,colorDiscreteOrder,legendTitle)
    
    if mode == 'StdMean':
        if 'multiples' not in kwargs:
            kwargs['multiples'] = [-2, -1, 0, 1, 2]
        
        kwargs['colorScale'] = plotly.colors.sequential.RdBu_r  
        mcOut = mc.StdMean(arr, kwargs['multiples'])
        colorSTRArray, \
        colorDiscreteSeq,\
        colorDiscreteOrder = colorProps_from_bins(mcOut, inputArr = kwargs['multiples'],
                                                  suffix = '-STD', colorScale = kwargs['colorScale'] )
        legendTitle = 'StdMean Schema (k=' + str(kwargs['k']) +')'
        return (colorSTRArray,colorDiscreteSeq,colorDiscreteOrder,legendTitle)
                        
    if mode == 'Percentiles':
        
        #Default Value
        if 'pct' not in kwargs:
            kwargs['pct'] = [1, 10, 50, 90,100]
        kwargs['colorScale'] = plotly.colors.sequential.RdBu_r   
        mcOut = mc.Percentiles(arr, kwargs['pct'])
        colorSTRArray, \
        colorDiscreteSeq,\
        colorDiscreteOrder = colorProps_from_bins(mcOut, inputArr = kwargs['pct'],
                                                  suffix = '%', colorScale = kwargs['colorScale'] )
        legendTitle = 'Percentiles Schema'
        return (colorSTRArray,colorDiscreteSeq,colorDiscreteOrder,legendTitle)
    
    if mode == 'BestFit':
        
       mcOut = mc.KClassifiers(arr).best
       colorSTRArray, colorDiscreteSeq ,colorDiscreteOrder = colorProps_from_intervals(mcOut, kwargs['colorScale'] )
       legendTitle = mcOut.name +  ' (k=' + str(len(mcOut.bins)) +')'
       return (colorSTRArray,colorDiscreteSeq,colorDiscreteOrder,legendTitle)
    
    
    
    
    


    
def colorProps_from_intervals(mcOut, colorScale):
    
    """This function returns a 3-item tuple resulting from:
            mcout : bin ids (0 to n-1) for observations
            
        Returns:
            colorSTRArray : np.array of type "Object" same size as input array
            colorDiscreteSeq : list of RGB colors from sampling a continuous colorscale
            colorDiscreteOrder : list of categories (intervals) as strings """
    
    IntsOut = mcOut.get_legend_classes(fmt = "{:.1f}")   # List of strings  ['[0.01, 0.25]', '(0.25, 0.50]',..]
             
    s1 = pd.Series(mcOut.yb) #bin ids for observations
    mapDict = { x : IntsOut[x]  for x in range(len(IntsOut))} # DICT in form of {0:interval_one, 1:interval_2}
    colorSTRArray = s1.map(mapDict).to_numpy() # Map Series with dictionary to get array of strings
    
    #Color Sequence Sampling and Order
    colorDiscreteSeq = plotly.colors.sample_colorscale(colorScale, len(IntsOut) , low = 0.1 )        
    colorDiscreteOrder =  list(mapDict.values())  
    return (colorSTRArray,colorDiscreteSeq,colorDiscreteOrder)


def colorProps_from_bins(mcOut, inputArr, suffix,colorScale):
    
    """This function returns a 3-item tuple resulting from:
            mcout : bin ids (0 to n-1) for observations
            inputArr : In the case of mode == 'Percentiles' it is the array of percentiles
                       In the case of mode == 'StdMean' it is the array of STD to add/subtract:
            
        Returns:
            colorSTRArray : np.array of type "Object" same size as input array
            colorDiscreteSeq : list of RGB colors from sampling a continuous colorscale
            colorDiscreteOrder : list of categories (intervals) as strings """
    
    binsOut = mcOut.bins
             
    s1 = pd.Series(mcOut.yb) #bin ids for observations
    mapDict = { x : str(inputArr[x]) + suffix + ' ' + '({:.1f})'.format(binsOut[x]) for x in range(len(binsOut))}
    colorSTRArray = s1.map(mapDict).to_numpy()
    
    #Color Sequence and Order
    colorDiscreteSeq = plotly.colors.sample_colorscale( colorScale , len(binsOut) , low = 0.1 )        
    colorDiscreteOrder =  list(mapDict.values())   
           
    return (colorSTRArray,colorDiscreteSeq,colorDiscreteOrder)

