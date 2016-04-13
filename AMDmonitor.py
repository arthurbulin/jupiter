import glob
import numpy as np
import matplotlib
import math
import os


def aeireader(filename):
    """this function reads a mercury .aei file"""
    t, el1, el2, el3, el4, el5, el6, m = np.genfromtxt(filename, unpack = True, skip_header = 4)

    return(t, el1, el2, el3, el4, el5, el6, m)


juplist = glob.glob('*/JUPITER.aei')


def AMDmonitor(simname):
    AMDnum = 0
    AMDden = 0

    #call the function to store the variables
    t1, a1, e1, inc1, capom1, omega1, capm1, m1 = aeireader(simname+'/JUPITER.aei')
    t1 = np.asarray(t1).flatten()
    tmax = max(t1)

    #call the function to store the variables
    tr1, ar1, er1, incr1, capomr1, omegar1, capmr1, mr1 = aeireader(simname+'/MERCURY.aei')
    tr1 = np.asarray(tr1).flatten()

    #call the function to store the variables
    tr2, ar2, er2, incr2, capomr2, omegar2, capmr2, mr2 = aeireader(simname+'/VENUS.aei')
    tr2 = np.asarray(tr2).flatten()

    #call the function to store the variables
    tr3, ar3, er3, incr3, capomr3, omegar3, capmr3, mr3 = aeireader(simname+'/EARTH.aei')
    tr3 = np.asarray(tr3).flatten()

    #call the function to store the variables
    tr4, ar4, er4, incr4, capomr4, omegar4, capmr4, mr4 = aeireader(simname+'/MARS.aei')
    tr4 = np.asarray(tr4).flatten()

    #calculate numerator and denominator separately to avoid singularity
    AMDnum = np.zeros(len(t1))
    AMDden = np.zeros(len(t1))
    AMDnum[:len(tr1)] = AMDnum[:len(tr1)] + mr1 * np.sqrt(ar1) * (1. - np.sqrt(1. - er1**2.) * np.cos(incr1 * math.pi / 180.))
    AMDden[:len(tr1)] = AMDden[:len(tr1)] + mr1 * np.sqrt(ar1)
    AMDnum[:len(tr2)] = AMDnum[:len(tr2)] + mr2 * np.sqrt(ar2) * (1. - np.sqrt(1. - er2**2.) * np.cos(incr2 * math.pi / 180.))
    AMDden[:len(tr2)] = AMDden[:len(tr2)] + mr2 * np.sqrt(ar2)
    AMDnum[:len(tr3)] = AMDnum[:len(tr3)] + mr3 * np.sqrt(ar3) * (1. - np.sqrt(1. - er3**2.) * np.cos(incr3 * math.pi / 180.))
    AMDden[:len(tr3)] = AMDden[:len(tr3)] + mr3 * np.sqrt(ar3)
    AMDnum[:len(tr4)] = AMDnum[:len(tr4)] + mr4 * np.sqrt(ar4) * (1. - np.sqrt(1. - er4**2.) * np.cos(incr4 * math.pi / 180.))
    AMDden[:len(tr4)] = AMDden[:len(tr4)] + mr4 * np.sqrt(ar4)

    #only do AMD while there are 4 rocky planets
    ntp4ind = min([len(tr1),len(tr2),len(tr3),len(tr4)])
    AMD = AMDnum[:ntp4ind] / AMDden[:ntp4ind]

    #normalize AMD to modern value
    normAMD = AMD/.0018
    tarr = t1[:ntp4ind]

    return(tarr,normAMD)

