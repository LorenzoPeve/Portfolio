

## CPT GEOTECH COMPUTATION MODULE


import pandas as pd
import numpy as np

def cptMapper(depth_array,soilProfile):
    """
    Arguments:
    depth : np.array
            CPT depth Array
    soilProfile : pd.DataFrame
            Soil profile to be used for mapping soil properties to corresponding depth.
    
    Returns:
        2D np.array with 1 column per mapped property
    """   
    #Create soil profile intervals for later mapping properties    
    soilProfile_mapper = np.array([soilProfile['Top Depth'],soilProfile['Top Depth'][1:].append(pd.Series([100000]),ignore_index=True)])
    soilProfile_mapper= np.transpose(soilProfile_mapper)
    profile_interval = pd.IntervalIndex.from_arrays(soilProfile_mapper[:,0],
                                                        soilProfile_mapper[:,1],closed= 'left')  
                        # IntervalIndex([[0, 10), [10, 100000)],  closed='left', dtype='interval[int64]')
    
    #Mapping
    layer_indx = profile_interval.get_indexer(depth_array)
    layerIDX = soilProfile.loc[layer_indx,'Layer Name'].values
    total_unit_weight = soilProfile.loc[layer_indx,'Total Unit Weight'].values
    gwt_id = soilProfile.loc[layer_indx,'GWT'].values
    
    return np.stack((layerIDX,total_unit_weight,gwt_id),axis=-1) #Stack arrays as individual columns

def soilStresses(depth,unit_weight,PP_profile,gamma_w):
    """
    Arguments:
    depth       : np.array
                  CPT depth Array
    unit_weight : np.array
                      
    Returns:
        2D np.array with 3 columns: Total, Pore Pressure, Effective Stresses
    """     
    ### Total Stress Calculations
    a1 = depth[0]
    a2 = depth[1:] - depth[:-1] 
    delta_z = np.append(a1,a2)               # Calculate layer delta_z
    layer_weight = delta_z * unit_weight     # Calculate delta_gamma
    sigma_t = np.cumsum(layer_weight)   # Calculate Total Stress
    
    ### Pore Pressure Calculation
    pore_pressure = (depth - PP_profile) * gamma_w
    pore_pressure = np.where( pore_pressure < 0 , 0 , pore_pressure)
        
    ### Effective Stress Calculations
    sigma_e = sigma_t - pore_pressure
  
    return np.stack((sigma_t , pore_pressure , sigma_e),axis=-1)


def geoComputations(qt,fs,sigma_T,sigma_E,depth_arr,pa_atm):
    
    #Normalized Friction Ratio
    Fr = (fs/(qt-sigma_T) ) * 100
    Fr = np.where( Fr <= 0 , 0.001 , Fr)
        
    #Normalized Tip resistance n=1
    Qt_1 = (qt - sigma_T)/pa_atm * (pa_atm/sigma_E) ** 1
    Qt_1 = np.where( Qt_1 < 0 , 0.01 , Qt_1)
    
    #Ic Calculations
    Ic_o = ((3.47-np.log10(Qt_1))**2+(1.22+np.log10(Fr))**2)**0.5
    n_o = np.minimum(0.381*Ic_o + 0.05*(sigma_E/pa_atm)-0.15,1)
    n_o = np.maximum(n_o,0.35) #CHECK
    Qt_n_o = np.array((qt - sigma_T)/pa_atm * (pa_atm/sigma_E)**n_o)
    
    #Iteration for exponent n
    arr_temp = np.stack((qt , sigma_T , sigma_E,Fr,depth_arr),axis=-1)
    n_iter = np.apply_along_axis(func1d = Ic_iteration, axis = 1, arr = arr_temp , pa_atm = pa_atm)
    
    #Qt_n and Ic calculations
    Cn = np.minimum( (pa_atm/sigma_E)**n_iter, 1.7)     #
    Qt_n = np.array((qt - sigma_T)/pa_atm * Cn)
    Qt_n = np.where( Qt_n < 0 , 0.01 , Qt_n)
    Ic_n = ((3.47-np.log10(Qt_n))**2+(1.22+np.log10(Fr))**2)**0.5
    
    #Friction Angle Correlations
    Qt_05 =   ((qt-sigma_T) / pa_atm) * (pa_atm/sigma_E)**0.5            # Explicitly using exponent factor of 0.5 for sands
    Qt_05 = np.where( Qt_05 < 0 , 0.01 , Qt_05)
    f_angle_KW_1990 = 17.6 + 11*np.log10(Qt_05) # Kulhawy & Mayne (1990)
    f_angle_RB_1983 = np.degrees(np.arctan( (1 / 2.68) * (np.log10(qt/sigma_E) + 0.29)))
    
    #Stack Arrays and get maximum
    f_angle = np.amax( np.stack( (f_angle_KW_1990,f_angle_RB_1983),axis = -1) , axis =1)
    
    return np.stack((Fr , Qt_1 , Ic_o, n_iter,Qt_n,Ic_n, f_angle),axis=-1)

def Ic_iteration(cpt_array,pa_atm):
           
    n_calc = 1 
    n_start = 0.9
    count = 0
    while abs(n_calc-n_start)>0.01: 
        n_start = n_calc
        Cn =  np.minimum((pa_atm/cpt_array[2])**n_start , 1.7) 
        Qt_n = max( ((cpt_array[0] - cpt_array[1])/pa_atm)*Cn ,0.01)  #25
        #Qt_n = max( ((cpt_array[0] - cpt_array[1])/pa_atm)*(pa_atm/cpt_array[2])**n_start ,0.01)
        
            # cpt_array[0] = qt_i
            # cpt_array[1] = sigma_T_i
            # cpt_array[2] = sigma_E_i
            # cpt_array[3] = Fr_i
        Ic_n = ( (3.47 - np.log10( Qt_n ) )**2 + (1.22 + np.log10( cpt_array[3] )) **2) **0.5
        n_calc = 0.381*Ic_n + 0.05*(cpt_array[2]/pa_atm)-0.15
        n_calc = np.clip(n_calc,0.35,1)
        if count > 25:
            print('Reached Max Iteration Step at',cpt_array[-1])  #Print Depth value
            n_calc = np.nan
            break
        count+=1
    
    n_iter = n_calc
    return n_iter     

