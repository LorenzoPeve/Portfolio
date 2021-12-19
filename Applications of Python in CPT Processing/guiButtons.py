# -*- coding: utf-8 -*-
"""
Created on Sun Dec  5 17:19:46 2021

@author: LPeve
"""

from plottingCPT import plotMapper
import ipywidgets as widgets

def dropdownParameter():

    button = widgets.Dropdown(options= list(plotMapper.keys()), value=list(plotMapper.keys())[0],
                                description='Select Parameter to Visualize:',
                                style = {'description_width': 'initial'},
                                layout={'width': 'max-content'},
                                disabled=False)
    return button

def dropdownCPTSelect_Surface(ids):
    
    cptBut = widgets.Dropdown(  options= ids, value = ids[0],
                                description='Select CPT Location to Visualize:',
                                style = {'description_width': 'initial'},
                                layout={'width': 'max-content'},
                                disabled=False)
    return cptBut



def plotMapper_to_CPT_column(key):
    
    """This function allows the mapping of a plotting parameter to the
        appropiate CPT output analysis column"""
    mapParameter2Column = dict(
        
                Tip_Resistance = 'Tip Res.',
                Corrected_Tip_Res =   'Corrected Tip Res.',
                Sleeve_Friction =  'Sleeve Friction',
                Pore_Pressure = 'Pore Pressure_cpt',
                Unit_Weight = 'Correlated Unit Weight',
                I_SBT = 'I_SBT',
                Norm_Tip_Res = 'Normalized Tip_Qt_n',
                Norm_Friction_Ratio = 'Normalized Fr',
                Pore_Press_Ratio_Bq = 'PP Ratio Bq',
                Ic_index = 'Ic_iter',
                Friction_Angle = 'Corr. Friction Angle',
                Su_Strength = 'Corr. Su',
                Precon_Pressure = 'Corr. PP'
                   )
    
    return mapParameter2Column[key]