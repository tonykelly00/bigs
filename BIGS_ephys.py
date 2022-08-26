# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 13:37:35 2019

@author: Tony Kelly
"""

from neuron import h, gui
import matplotlib.pyplot as plt
import numpy as np

#import the dll from neuron
#neuron.load_mechanisms(D:/Bonn/other/BIGS_Summer_School/2019/model/mod)
#h.nrn_load_dll("F:\\Bonn\\other\\Teaching\\BIGS_Summer_School\\2021\\model\\mod\\nrnmech.dll")   # this way of loading dll from daniel works

#dir(h) #to view what is hoc variables are accessable from python

#h.allsec() # try instead of forall


def mk_soma(length, diam, leak_conductance=1/5000, v_init=-80): # makes soma; soma = mk_soma(20,20)
    soma = h.Section()
    soma.L = length
    soma.diam = diam
    soma.Ra = 181
    soma.cm = 1
    
    soma.insert('pas')
    soma(0.5).pas.g = leak_conductance # 0.0002  5000 ohms.cm2
    soma(0.5).e_pas = v_init
    
    
    # soma.insert('hh')
    # soma(0.5).hh.el = v_init #in mod file set to -54.3
    # soma.ki = 150 #mM #as default ki is 54 mM for squid axon
    # dir(soma(0.5).hh) # view the variables
    
    return soma
    

def attach_dend(soma, dend_length, dend_diameter, leak_conductance=1/5000, v_init=-80): # attaches dendrites to soma; dend = attach_dend(soma, dend_length, dend_diameter)
    dend = h.Section()
    dend.L = dend_length
    dend.diam = dend_diameter
    
    dend.Ra = 181
    dend.cm = 1
    
    dend.insert('pas')
    dend(0.5).pas.g = leak_conductance # 0.0002  5000 ohms.cm2
    dend(0.5).e_pas = v_init
    dend.nseg = 20
    
    soma.connect(dend(0.0), 1.0)
    
    dendV_vec = h.Vector()      # Membrane potential vector
    dendV_vec.record(dend(0.8)._ref_v)
    #plt.plot(t_vec, dend[1]) #plots dendritic voltage
    return dend, dendV_vec

def attach_synapse(loc): # attaches excitatory synapse to compartment eg dend; sy1 = attach_synapse(dend[0])
    sy = h.AlphaSynapse(loc(0.2))
    sy.onset = 150
    sy.tau = 0.1
    sy.gmax = 0.01	#uS  #Mitchell and Williams, Nature Neuroscience, 2008 used <25nS
    sy.e = 0
    
    syI_vec = h.Vector()      # Membrane current vector (nA)
    syI_vec.record(sy._ref_i)
    #plt.plot(t_vec, sy1[1]) #plots synaptic current  (nA)
    return sy, syI_vec
    
def attach_VC(loc, rs=1):  # attaches voltage-clamp electrode to compartment eg soma; vc = attach_VC(soma)
  vc = h.SEClamp(loc(0.5))
  vc.rs = rs
  vc.dur1 = 10 #ms
  vc.amp1 = -80 # mV
  vc.dur2 = 100 #ms
  vc.amp2 = 0 # mV
  vc.dur3 = 10 #ms
  vc.amp3 = -80 # mV
  
  somaI_vec = h.Vector()      # Membrane current vector
  somaI_vec.record(vc._ref_i)
  #plt.plot(t_vec, vc[1]) #plots mesured current (nA)
  
  return vc, somaI_vec

def attach_IC(loc):  # attaches current injecting electrode to compartment eg soma; ic = attach_IC(soma)
  ic = h.IClamp(loc(0.5))
  ic.delay = 10 #ms
  ic.dur = 100 # ms
  ic.amp = -0.01 #nA
  
  #soma.insert('hh')
  
  return ic


def record(syN):
    gmax_list = []
    for i in range(100):
       gmax_list.append(i*.01)

       syN = gmax_list[i]
       print(syN)
    
    return syN
            
def run(soma, stepT=0.01, v_init=-80, end=250): # Runs simulation stepT determines the time resolution default 0.01 = 1/0.01 =>100pt/ms
    #print(soma.L) 
    # Record
    v_vec = h.Vector()             # Membrane potential vector (mV)
    t_vec = h.Vector()             # Time stamp vector (ms)
    v_vec.record(soma(0.5)._ref_v)
    t_vec.record(h._ref_t)
     
    # Simulation hyperparameters
    h.cvode.active(0)
    h.finitialize(v_init)
    #new block to reach SS see neuron book 8.4.2
    h.t = -1e6
    h.dt = 1e3
    while h.t<-h.dt:
        h.fadvance()
    h.t = 0
       
    dt = stepT
    h.steps_per_ms = 1.0/dt
   
    h.secondorder = 0
    h.dt = dt
    
    h.frecord_init()  # Necessary after changing t to restart the vectors
    while h.t < end:
        h.fadvance()
    print("Done Running")
    
    #plt.figure(figsize=(8,4)) # Default figsize is (8,6)
    #plt.plot(t_vec, v_vec)
    #plt.xlabel('time (ms)')
    #plt.ylabel('mV')
    #plt.show()
    

    return t_vec, v_vec

def run_conductances(stepT=0.01, v_init=-80, conductance=0.05):
    soma = mk_soma(20,20)
    dend = attach_dend(soma, dend_length, dend_diameter)
    sy1 = attach_synapse(dend[0])
    vc = attach_VC(soma)
    
    sy1[0].gmax = conductance
    
    
     # Record
    v_vec = h.Vector()             # Membrane potential vector (mV)
    t_vec = h.Vector()             # Time stamp vector (ms)
    v_vec.record(soma(0.5)._ref_v)
    t_vec.record(h._ref_t)
     
    # Simulation hyperparameters
    h.cvode.active(0)
    dt = stepT
    h.steps_per_ms = 1.0/dt
    h.finitialize(v_init)
    h.secondorder = 0
    h.dt = dt
    
    h.frecord_init()  # Necessary after changing t to restart the vectors
    while h.t < 250:
        h.fadvance()
    print("Done Running")
    
    #plt.figure(figsize=(8,4)) # Default figsize is (8,6)
    plt.plot(t_vec, v_vec)
    plt.xlabel('time (ms)')
    plt.ylabel('mV')
    plt.show()
    

    return t_vec, v_vec, vc[1]


if __name__ == "__main__":
    soma_length = 20  # um
    soma_diameter = 20  # um
    dend_length = 200
    dend_diameter = 3
    conductances = np.arange(0,0.1,0.001)
    result_collection = []
#    for x in conductances:
#        curr_results = run_conductances(stepT=0.01, v_init=-80, conductance=x)
#        result_collection.append(curr_results)
    #leak_conductance = 1/5000   # 0.0002 S.cm2 5000 ohms.cm2
    # t_vec, v_vec = run()
    """
    Rin
        for discuassion of converting specific membrane resitance (Rm)) to Rin see https://www.neuron.yale.edu/phpBB/viewtopic.php?f=8&t=2822
        Rm = Rin [*106 (scaling for  mega)] * surface area [*10-8 (scaling for um2 to cm2)] 
         = Rm / surface area [4*pie*R^2] [*10-8 (scaling for um2 to cm2)]
         (1/soma(0.5).pas.g)/(4*3.14*10**2) * (1e2) [check 1e2 scaling]
    
    Membrane time constant 
		cell area [h.area(0.5)=1256um^2} time 1uF/cm^2	=> 1256 (1e-8) * 1 (1e-6) = 12.56pF
		400mOhms * .012 nF = 4.8ms
		and rise of voltage change at 66% around that 
		bit fast compared to real cell?
    
    """
    """
    current_soma = mk_soma(soma_length, soma_diameter)
    current_dendrite = attach_dendrite(current_soma, dend_length, dend_diameter)
    """
