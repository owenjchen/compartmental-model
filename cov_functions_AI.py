from parameters_cov_AI import params
from math import exp, ceil, log, floor, sqrt
import numpy as np
from scipy.integrate import ode
from scipy.stats import norm, gamma
import pandas as pd
##
# -----------------------------------------------------------------------------------
##
class simulator:
    def __init__(self):
        pass
    ##
#-----------------------------------------------------------------
        
    ##
    def ode_system(self,t,y,population_frame,control_time,beta_factor):
        ##
        dydt = np.zeros(y.shape)

        I_vec = [ y[params.I_ind+i*params.number_compartments] for i in range(params.age_categories)]

        if t > control_time[0] and t < control_time[1]: # control in place
            control_factor = beta_factor
        else:
            control_factor = 1
            


        for i in range(params.age_categories):
            # S
            dydt[params.S_ind + i*params.number_compartments] = - y[params.S_ind + i*params.number_compartments] * control_factor * (np.dot(params.infection_matrix[i,:],I_vec)) 
            # E
            dydt[params.E_ind + i*params.number_compartments] = ( y[params.S_ind + i*params.number_compartments] * control_factor * (np.dot(params.infection_matrix[i,:],I_vec))
                                                                - params.infectious_rate * y[params.E_ind + i*params.number_compartments])
            # I
            dydt[params.I_ind + i*params.number_compartments] = (params.infectious_rate * y[params.E_ind + i*params.number_compartments] - 
                                                                  params.non_infectious_rate * y[params.I_ind + i*params.number_compartments])
            # R
            dydt[params.R_ind + i*params.number_compartments] = (params.non_infectious_rate * (1 - population_frame.p_hospitalised[i]) * y[params.I_ind + i*params.number_compartments] +
                                                                  params.hosp_rate * (1 - population_frame.p_critical[i]) * y[params.H_ind + i*params.number_compartments] + 
                                                                  params.death_rate * (1 - params.death_prob) * y[params.C_ind + i*params.number_compartments])
            # H
            dydt[params.H_ind + i*params.number_compartments] = (params.non_infectious_rate * (population_frame.p_hospitalised[i]) * y[params.I_ind + i*params.number_compartments] -
                                                                  params.hosp_rate * y[params.H_ind + i*params.number_compartments])
            # C
            dydt[params.C_ind + i*params.number_compartments] = (params.hosp_rate  * (population_frame.p_critical[i]) * y[params.H_ind + i*params.number_compartments] -
                                                                  params.death_rate * y[params.C_ind + i*params.number_compartments])
            # D
            dydt[params.D_ind + i*params.number_compartments] = params.death_rate * (params.death_prob) * y[params.C_ind + i*params.number_compartments]

        return dydt
    ##
    #--------------------------------------------------------------------
    ##
    def run_model(self,T_stop,population,population_frame,control_time,beta_factor): # ,beta_L_factor,beta_H_factor,t_control,T_stop,vaccine_time,ICU_grow,let_HR_out):
        
        E0 = 0
        I0 = 1/population
        R0 = 0
        H0 = 0
        C0 = 0
        D0 = 0
        S0 = 1 - I0 - R0 - C0 - H0 - D0

        y0 = np.zeros(params.number_compartments*params.age_categories)

        for i in range(params.age_categories):
            y0[params.S_ind + i*params.number_compartments] = (population_frame.Population[i]/100)*S0
            y0[params.E_ind + i*params.number_compartments] = (population_frame.Population[i]/100)*E0
            y0[params.I_ind + i*params.number_compartments] = (population_frame.Population[i]/100)*I0
            y0[params.R_ind + i*params.number_compartments] = (population_frame.Population[i]/100)*R0
            y0[params.H_ind + i*params.number_compartments] = (population_frame.Population[i]/100)*H0
            y0[params.C_ind + i*params.number_compartments] = (population_frame.Population[i]/100)*C0
            y0[params.D_ind + i*params.number_compartments] = (population_frame.Population[i]/100)*D0

        sol = ode(self.ode_system,jac=None).set_integrator('dopri5').set_f_params(population_frame,control_time,beta_factor)
        
        tim = np.linspace(0,T_stop, 301) # use 141 time values
        
        sol.set_initial_value(y0,tim[0])

        y_out = np.zeros((len(y0),len(tim)))
        
        i2 = 0
        y_out[:,0] = sol.y
        for t in tim[1:]:
                if sol.successful():
                    sol.integrate(t)
                    i2=i2+1
                    y_out[:,i2] = sol.y
                else:
                    raise RuntimeError('ode solver unsuccessful')
        
        return {'y': y_out,'t': tim}

#--------------------------------------------------------------------


# print(simulator().run_model(200))