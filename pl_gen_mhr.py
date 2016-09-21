import numpy as np
import math

def anomcalc(meananom,ecc):
    """calculates eccentric anomaly from the mean anomaly"""
    #based on Murray and Dermot
    meananom=np.asarray(meananom)
    ecc=np.asarray(ecc)
    k=0.85
    sign=np.sin(meananom)/np.fabs(np.sin(meananom))

    E0=meananom+sign*k*ecc
    E=E0

    sel=np.arange(0,len(E0))
    fracdiff=sel*0.+1.
    sel2=np.where(ecc >= 1)
    fracdiff[sel2]=0.

    while np.amax(fracdiff) > 0.001:
        f0=E[sel]-ecc[sel]*np.sin(E[sel])-meananom[sel]
        f1=1.-ecc[sel]*np.cos(E[sel])
        f2=ecc[sel]*np.sin(E[sel])
        f3=ecc[sel]*np.cos(E[sel])
        
        del1=-f0/f1
        del2=-f0/(f1+.5*del1*f2)
        del3=-f0/(f1+.5*del2*f2+1./6.*del2**2*f3)

        nextone=E[sel]+del3
        diff=E[sel]-nextone
        fracdiff[sel]=np.fabs(diff/E[sel])
        
        E[sel]=nextone
        sel=np.where((fracdiff > 0.001))

        sel2=np.where(ecc >= 1)
        fracdiff[sel2]=0.

    sel2=np.where(ecc >= 1)
    E[sel2]=2.*math.pi*1.0001

    return(E)



def angcalc(E,ecc):
    """calculates the true anomaly from the eccentric anomaly"""
    E=np.asarray(E)
    ecc=np.asarray(ecc)

    cosang=(np.cos(E)-ecc)/(1-ecc*np.cos(E))
    angpos=np.arccos(cosang)

    #sometimes E is just under 0...this is wrong    
    E=np.fabs(E)

    #output of arccos goes from 0 to pi, but real angles go up to 2*pi
    #we need to correct for this
    acoscorrec=np.floor(E/math.pi)*2*math.pi

    #however sometime E is just over 2*pi.  these don't need corrected
    Enoisecorrec=np.floor(E/(2*math.pi))*4.*math.pi
    acoscorrec=acoscorrec-Enoisecorrec

    #correcting angpos
    angpos=acoscorrec-angpos
    angpos=(angpos*angpos)**.5

    return(angpos)


def rcalc(E,a,ecc):
    """calculates distance from Sun for a given orbit and ecc. anomaly"""
    r=a*(1.-ecc*np.cos(E))

    return(r)



def pl_gen(ainner,npl,mpl,nhill):
    """generates a tp initial conditions file for SCATR"""

    #note: masses should be inputted into this function in jupiter masses
    #ainner is the innermost semimajor axis (in AU)
    #npl is the desired number of planets in the system
    #mpl is the mass of each planet in earth masses
    #nhill is the number of mutual hill radii that should separate each planet
    massivenum = npl + 1 #includes sun
    
    #build name array
    names = []
    for i in range(1,massivenum):
	names.append('PL'+str(i))

    denlist = np.ones(npl)
    mass=np.empty(massivenum)
    Msun=2.959139768995959e-04
    Mearth = Msun * 3e-6
    mass[0]=Msun*1.0

    a=np.empty(npl)
    ecc=np.empty(npl)
    inc=np.empty(npl)
    longper=np.empty(npl)
    longasc=np.empty(npl)
    meanlong=np.empty(npl)

    mass[1:] = mpl*Mearth
    
    #set up planet orbits
    for i in range(npl):
	if i==0:
	    a[i]=ainner
	else:
	    mfactor = ((mass[i+1] + mass[i]) / (3. * mass[0]))**(1./3.)
	    a[i] = a[i-1] * (1. + nhill/2. * mfactor) / (1. - nhill/2. * mfactor)

	ecc[i]=1e-2 * np.random.random_sample(1)
	inc[i]=1. * np.random.random_sample(1)
	longper[i]=360. * np.random.random_sample(1)
	longasc[i]=360. * np.random.random_sample(1)
	meanlong[i]=360. * np.random.random_sample(1)
    
    inc=inc*math.pi/180.
    longper=longper*math.pi/180.
    longasc=longasc*math.pi/180.
    meanlong=meanlong*math.pi/180.
    meananom=meanlong-longper #see p. 34 of Murray and Dermott

    #transforming random mean anomalies into actual orbital positions
    eccanom=anomcalc(meananom,ecc)
    angpos=angcalc(eccanom,ecc)
    rpos=rcalc(eccanom,a,ecc)

    argper=longper-longasc #see p. 49 of Murray and Dermott

    #transform into actual positions and velocities
    transformx = (np.cos(longasc) * np.cos(argper + angpos) - np.sin(longasc)
                 * np.sin(argper + angpos) * np.cos(inc))
    transformy = (np.sin(longasc) * np.cos(argper + angpos) + np.cos(longasc)
                 * np.sin(argper + angpos) * np.cos(inc))
    transformz = np.sin(argper + angpos) * np.sin(inc)

    #transforming coords
    gencoordx = np.empty(massivenum)*0.0
    gencoordy = np.empty(massivenum)*0.0
    gencoordz = np.empty(massivenum)*0.0
    gencoordx[1:massivenum] = rpos * transformx
    gencoordy[1:massivenum] = rpos * transformy 
    gencoordz[1:massivenum] = rpos * transformz

    #calculating velocities in specific orbit coordinate
    signinc = inc / np.fabs(inc)
    period = np.sqrt(4 * math.pi**2 * a**3 / mass[0])
    angvel = 2 * math.pi / period

    #doing velocity transformations...see p. 31 and 51 of Murray and Dermott
    xdot = -angvel * a * np.sin(angpos) / np.sqrt(1 - ecc**2)
    ydot = angvel * a * (ecc + np.cos(angpos)) / np.sqrt(1 - ecc**2)
    zdot = 0 * angpos
        
    genvelx = np.empty(massivenum)*0.0
    genvely = np.empty(massivenum)*0.0
    genvelz = np.empty(massivenum)*0.0
    genvelx[1:massivenum] = ((np.cos(argper) * np.cos(longasc) - np.sin(argper) *
            np.sin(longasc) * np.cos(inc)) * xdot - (np.sin(argper) *
            np.cos(longasc) + np.cos(argper) * np.sin(longasc) *
            np.cos(inc)) * ydot)
    genvely[1:massivenum] = ((np.cos(argper) * np.sin(longasc) + np.sin(argper) *
            np.cos(longasc) * np.cos(inc)) * xdot + (np.cos(argper) *
            np.cos(longasc) * np.cos(inc) - np.sin(argper) *
            np.sin(longasc)) * ydot)
    genvelz[1:massivenum] = ((np.sin(argper) * np.sin(inc)) * xdot +
            (np.cos(argper) * np.sin(inc)) * ydot)


    Lx = np.sum((gencoordy*genvelz - gencoordz*genvely) * mass)
    Ly = np.sum((gencoordz*genvelx - gencoordx*genvelz) * mass)
    Lz = np.sum((gencoordx*genvely - gencoordy*genvelx) * mass)
    Ltot = np.sqrt(Lx*Lx + Ly*Ly + Lz*Lz)
    Lxhat = Lx/Ltot
    Lyhat = Ly/Ltot
    Lzhat = Lz/Ltot

    thet = np.arctan2(Lyhat,Lxhat)
    phi = np.arcsin(Lzhat)

    #rotate around z-axis so all ang. momentum is in x-z plane
    thet = -thet
    for i in range(massivenum):
        rotz=[[np.cos(thet),-np.sin(thet),0],[np.sin(thet),np.cos(thet),0],[0,0,1]]
        pos = [[gencoordx[i]],[gencoordy[i]],[gencoordz[i]]]
        vel = [[genvelx[i]],[genvely[i]],[genvelz[i]]]

        pos = np.dot(rotz, pos)
        vel = np.dot(rotz, vel)

        gencoordx[i] = pos[0]
        gencoordy[i] = pos[1]
        gencoordz[i] = pos[2]
        genvelx[i] = vel[0]
        genvely[i] = vel[1]
        genvelz[i] = vel[2]

    #rotating around y-axis to align all ang. momentum with z-axis
    phi = -(math.pi/2. - phi)
    for i in range(massivenum):
        roty=[[np.cos(phi),0,np.sin(phi)],[0,1,0],[-np.sin(phi),0,np.cos(phi)]]
        pos = [[gencoordx[i]],[gencoordy[i]],[gencoordz[i]]]
        vel = [[genvelx[i]],[genvely[i]],[genvelz[i]]]

        pos = np.dot(roty, pos)
        vel = np.dot(roty, vel)

        gencoordx[i] = pos[0]
        gencoordy[i] = pos[1]
        gencoordz[i] = pos[2]
        genvelx[i] = vel[0]
        genvely[i] = vel[1]
        genvelz[i] = vel[2]

    #create tp.in file
    filename= 'big.in'
    f = open(filename, 'w')
    f.write(')O+_06 Big-body initial data  (WARNING: Do not delete this line!!)\n')
    f.write(') Lines beginning with ) are ignored.\n')
    f.write(')---------------------------------------------------------------------\n')
    f.write(' style (Cartesian, Asteroidal, Cometary) = Cartesian\n')
    f.write(' epoch (in days) = 0.0\n')
    f.write(')---------------------------------------------------------------------\n')


    #select masses and radii
    for j in range(1,massivenum):
        mass[j] = mass[j]/Msun
        massing = mass[j]*1.98855e33
        density = denlist[j-1]
        f.write(names[j-1] + ' m='+str(mass[j])+' r=1.D0 d='+str(density)+'\n')
        
        randthet = np.random.random_sample(1)*math.pi*2.
        randcosphi = np.random.random_sample(1)*2.-1.
        randphi = math.acos(randcosphi)
        randx = 1e-9*math.cos(randthet)*math.cos(randphi)
        randy = 1e-9*math.sin(randthet)*math.cos(randphi)
        randz = 1e-9*math.sin(randphi)

        newx,newy,newz = gencoordx[j]+randx, gencoordy[j]+randy, gencoordz[j]+randz
        f.write('  '+'%.15e' % newx +' '+'%.15e' % newy +' '+'%.15e' % newz +'\n')
        f.write(str(genvelx[j]) + ' ' + str(genvely[j]) + ' ' + str(genvelz[j])+'\n')
        f.write('0. 0. 0.\n')

    f.close()

