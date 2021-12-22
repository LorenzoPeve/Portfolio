
import numpy as np
print('hola')
#OLSON & STARK 2002
def liqStrRatio_OS_2002(qt,sigma_E,pa_atm):
    
    #Equation [6] in Olson & Stark 2002
    Cq = 1.8 / (0.8 + (sigma_E/pa_atm))    
    qc1 = qt * Cq
    qc1 = qc1 / 1000 # kPa to MPa
    LSR_profile = 0.03 + 0.0143 * qc1
    LSR_profile = np.where(qc1 > 6.5 , 0.4 , LSR_profile )
       
    return LSR_profile


########################################################################
#Robertson 2010
def cleanSandQtn_Rob2010(Qt_n,Ic):
    f = lambda i : 5.581 * (i**3) - 0.403*(i**4) - 21.63*(i**2) + 33.75*i - 17.88  # Eqn [8] in Rob. 2010
    K_factor = np.where(Ic<= 1.64, 1.0,f(Ic))
    Qt_n_cs = K_factor * Qt_n                                                      # Eqn [6] in Rob. 2010
    return np.stack((K_factor , Qt_n_cs),axis=-1)

#Liquefied Strength Ratio LSR
def liqStrRatio_Rob2010(Qt_n_cs,phi):
    
    cond1 = Qt_n_cs <= 70  
    cond2 = Qt_n_cs > 70     
    condlist = [cond1, cond2]     
    
    f = lambda x : (0.02199 - 0.0003124*x) / (1 - 0.02676*x + 0.0001783* (x**2) )   # Eqn [10] in Rob. 2010
    choicelist = [f(Qt_n_cs),0.4]
            
    LSR_profile = np.select(condlist , choicelist)
    
    #Set minimum to 0.05  
    LSR_profile = np.where(LSR_profile<0.05,0.05, LSR_profile)
    #Set max to tan(phi)
    LSR_profile = np.where(cond1, np.minimum(LSR_profile,np.tan(np.radians(phi))), LSR_profile)
    
    return LSR_profile



########################################################################
def liqStrRatio_IB_2015(Ic,qt,sigma_E,pa_atm,phi, C_FC=0):  #uSE TAN(PHI) COLUMN
    
    FC = 80*(Ic+C_FC)-137
    FC = np.clip(FC , 0 , 100)
                        
    # Function for iteration to (m) exponent
    def iterate_m_factor(arr, pa_atm):
        """This function gets a 3 column array in the form of qt, sigma_E, and FC"""
        #Array unpacking
        qt,sigma_E,FC = arr
       
        #Initialize Iteration Variables
        m_calc = 0.52
        m = 0.5
        count=0
        while abs(m_calc-m)>0.001:
            m = m_calc
            Cn = min( (pa_atm/sigma_E)**m , 1.7)
            qc1N = Cn * qt/pa_atm
            delta_qc1N = (11.9 + qc1N/14.6) * np.exp(1.63 - (9.7 / (FC+2)) - (15.7 / (FC+2))**2)
            qc1N_cs = qc1N + delta_qc1N
            qc1N_cs = np.clip(qc1N_cs , 21 , 254)
            m_calc = 1.338 - 0.249 * (qc1N_cs ) ** 0.264
            
            if count > 25:
                print('Reached Max Iteration') 
                m_calc = 0.5  #Could be set to np.nan
                break
            count+=1
            return m_calc
        
    #Create Array for function application
    arr_temp = np.stack((qt, sigma_E, FC),axis=-1)
    
    #Iteration Function loop
    m_iter = np.apply_along_axis(func1d = iterate_m_factor, axis = 1, arr = arr_temp , pa_atm = pa_atm)
    m_iter = np.clip(m_iter ,  0.264 , 0.782)
    Cn = (pa_atm/sigma_E)**m_iter 
    Cn = np.clip(Cn,None,1.7)
    qc1N = Cn * qt/pa_atm
    delta_qc1N_Sr = -0.007*(FC**2) + 1.2904*FC - 2.4319
            
            
    qc1N_cs = qc1N + delta_qc1N_Sr   
    
    LSR = np.exp( (qc1N_cs / 24.5) - (qc1N_cs / 61.7)**2 + (qc1N_cs / 106)**3 - 4.42) 
    LSR_profile_voids = np.clip(LSR, 0.05,np.tan(np.radians(phi)))
    LSR_profile_no_voids = np.clip( LSR * (1 + np.exp( (qc1N_cs/11.1) - 9.82)), 
                                0.05,
                                np.tan(np.radians(phi)))
    
    LSR_profile_no_voids = np.where(LSR_profile_no_voids > 0.4, 0.4,  LSR_profile_no_voids )
    LSR_profile_voids = np.where(LSR_profile_voids > 0.4, 0.4,  LSR_profile_voids )
    print('hola')
    print(LSR_profile_no_voids.max())
    print(LSR_profile_voids.max())
    return np.stack((m_iter , qc1N_cs , LSR_profile_no_voids, LSR_profile_voids),axis=-1)


