

import pandas as pd
import numpy as np
import os
import plotly.io as pio
import glob

pio.renderers.default='browser'
import plotly.graph_objects as go

#Interal Modules
os.chdir(r'\\ARO-01\Data\Gis\Prj1\L\Landsvirkjun SAU Dam\Phase 02 - Updated Ground Model\CPT Data Analysis\Python Code')

import loading_CPT_and_profiles_rev2 as loadCPT
import cptGeotech_rev3 as cptGeotech
import residualStrength_rev2 as RS


#CONSTANTS
a_n = 0.8
gamma_w = 9.81 #kN/m3
pa_atm = 101.325 #kPa


#Read Data
os.chdir(r'\\ARO-01\Data\Gis\Prj1\L\Landsvirkjun SAU Dam\CPT Data\Results for Python Script')
files = glob.glob('*.txt')

for item in files:

    cpt_data = loadCPT.readCPTfile(item)
    
    #Load Soil & GWT Profiles
    soilProfile = loadCPT.readSoilProfile()
    gwt_levels = loadCPT.readGWT()
    
    #Mappping Soil Profile Properties
    cpt_data[['Layer IDX','Total Unit Weight','GWT_ID']] = cptGeotech.cptMapper(cpt_data['Depth (m)'].array,soilProfile)
    cpt_data['GWT Depth'] = gwt_levels.loc[cpt_data['GWT_ID'],'Depth To'].values
    
    #Soil Stresses Calculations
    new_cols = ['Total Stress (kPa)','Pore Pressure (kPa)', 'Effective Stress (kPa)']
    cpt_data[new_cols] = cptGeotech.soilStresses(cpt_data['Depth (m)'].to_numpy(dtype=np.float32),
                                      cpt_data['Total Unit Weight'].to_numpy(dtype=np.float32),
                                      cpt_data['GWT Depth'].to_numpy(dtype=np.float32),
                                      gamma_w
                                     )
    
    
    #All columns in kPa
    cpt_data.loc[:,['qc (MPa)','fs (MPa)','u2 (MPa)']] = cpt_data.loc[:,['qc (MPa)','fs (MPa)','u2 (MPa)']] * 1000   # Convert from MPa to kPA
    cpt_data.rename(columns = {'qc (MPa)':'qc (kPa)' ,
                               'fs (MPa)': 'fs (kPa)',
                               'u2 (MPa)':'u2 (kPa)' },inplace=True)
    
    cpt_data['qt (kPa)']= cpt_data['qc (kPa)'] + (1 - a_n) * cpt_data['u2 (kPa)']
    
    
    # Variables for geotech calculations
    fs = cpt_data['fs (kPa)'].to_numpy(dtype=np.float32)
    fs = np.where( fs <= 0 , 0.001 , fs)  
    
    qt = cpt_data['qt (kPa)'].to_numpy(dtype=np.float32)
    sigma_T = cpt_data['Total Stress (kPa)'].to_numpy(dtype=np.float32)
    sigma_E = cpt_data['Effective Stress (kPa)'].to_numpy(dtype=np.float32)
    depth_arr = cpt_data['Depth (m)'].to_numpy(dtype=np.float32)
    
    cpt_data[['Fr','Qt_1' , 'Ic_o', 'n_iter','Qt_n','Ic_n','Friction Angle']]  = cptGeotech.geoComputations(qt,fs,sigma_T,sigma_E,depth_arr,pa_atm)
    
    
    #RESIDUALS STRENGTH CALCULATIONS
    
    #Robertson 2010
    cpt_data[['R10_K_factor','R10_Qt_n_cs']] = RS.cleanSandQtn_Rob2010( cpt_data['Qt_n'].to_numpy(), cpt_data['Ic_n'].to_numpy() )
    f_angle = cpt_data['Friction Angle'].to_numpy()
    LSR_profile_Rob_2010 = RS.liqStrRatio_Rob2010( cpt_data['R10_Qt_n_cs'].to_numpy(),f_angle )
    liq_strength_Rob_2010 = LSR_profile_Rob_2010 * sigma_E
    
    
    cpt_data['LSR_Rob_2010'] = LSR_profile_Rob_2010
    cpt_data['Sr_Rob_2010'] = liq_strength_Rob_2010
    
    
    
    #Olson & Stark 2002
    LSR_profile_OS_2002 = RS.liqStrRatio_OS_2002(qt, sigma_E, pa_atm)
    liq_strength_OS_2002 = LSR_profile_OS_2002 * sigma_E
    
    
    cpt_data['LSR_OS_2002'] = LSR_profile_OS_2002
    cpt_data['Sr_OS_2002'] = liq_strength_OS_2002
    
    #I&B 2015
    Ic = cpt_data['Ic_n'].to_numpy()
    cpt_data[['IB15_m_iter','IB15_qc1N_cs','IB15_LSR','IB15_LSR_void']]  =     RS.liqStrRatio_IB_2015(  Ic    ,qt,sigma_E,pa_atm,f_angle)
    cpt_data['IB15_Sr']  =    cpt_data['IB15_LSR'] * sigma_E
    cpt_data['IB15_Sr_void']  =    cpt_data['IB15_LSR_void'] * sigma_E
    
    directory = r'\\ARO-01\Data\Gis\Prj1\L\Landsvirkjun SAU Dam\Phase 02 - Updated Ground Model\CPT Data Analysis\Python Code'
    cpt_data.to_csv(directory + '\Output\CPT_' + item.split('-')[1] + '.csv')




#############################
#PLOTTING

def axisDict():
    axDICT = dict(  linecolor = 'black',  
                    mirror=True,
                    ticks = 'inside',
                    ticklen = 10,
                    tickmode = 'linear',
                    tickangle = 0,
                    showgrid=True,
                    gridcolor = '#E8E7E4',
                    zeroline = False,
                    exponentformat ='none')
    return axDICT 

layout = go.Layout( font = dict(family = 'Arial', color = 'black'), #Sets the global font
                    width = 400,
                    height = 1000,
                    plot_bgcolor='#FFF',  
                    xaxis= axisDict(),
                    yaxis=axisDict())

#PLOT RESIDUAL STRENGTHS
fig = go.Figure(layout=layout)
fig.add_trace(go.Scatter(x= cpt_data['Sr_Rob_2010'], y = depth_arr, mode = "lines",   
                         line_color = '#0066FF',line_width=2 , name='Rob. 2010'))

fig.add_trace(go.Scatter(x= cpt_data['Sr_OS_2002'], y = depth_arr, mode = "lines",   
                         line_color = '#428265',line_width=2 , name='OS 2002'))

fig.add_trace(go.Scatter(x= cpt_data['IB15_Sr'], y = depth_arr, mode = "lines",   
                         line_color = '#B63CB0',line_width=2 , name='IB 2015"'))
                
fig.update_yaxes(dict(title = 'Depth (m)',  autorange= 'reversed', dtick = 0.5))
fig.update_xaxes(dict(title = 'Residual Shear Strength (psf)', range = [0,200], dtick = 50))
fig.update_layout(showlegend=True)                
fig.show()

#PLOT RESIDUAL STRENGTH RATIOS
fig = go.Figure(layout=layout)

fig.add_trace(go.Scatter(x= cpt_data['R10_Qt_n_cs'], y = cpt_data['LSR_Rob_2010'], mode = "markers",
                         marker_symbol="circle",marker_size=3,  marker_color = '#0066FF', name='Rob. 2010"'))

fig.add_trace(go.Scatter(x= cpt_data['IB15_qc1N_cs'], y = cpt_data['IB15_LSR'], mode = "markers",
                         marker_symbol="circle",marker_size=3,  marker_color = '#B63CB0', name='IB 2015"'))
                
fig.update_yaxes(dict(title = 'Residual Shear Strength Ratio',  range = [0,0.4], dtick = 0.05))
fig.update_xaxes(dict(title = 'Equivalent Clean Sand CPT Norm. Corr. Tip Res.', range = [0,200], dtick = 25))
fig.update_layout(showlegend=True,width = 500, height = 400,)                
fig.show()