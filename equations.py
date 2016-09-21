import numpy as np

G = 6.67384e-8
Msun = 1.988435e33
au = 1.495e11 * 100.0

def orbital_period(mass,a):
	mass = mass * Msun
	a = a * au
	numer = 4.0 * np.pi**2 * a**3
	denom = G * (Msun + mass) 
	p2 = numer / denom #Divide
	p = np.sqrt(p2) #square root
	p = p / 86400.0 #Convert seconds to days
	return p

def reverse_mutual_hill_radii(mass,nhr,a1,m1):
	numer = 2 * nhr
	a1 = a1 * au
	a = list()
#	a.append(a1)
	mass = np.asarray(mass)
	mass = mass * 3.002e-6 * Msun
	m1 = m1 * Msun
	
	d = ((mass[0] + m1) / (3. * Msun))**(1./3.)
	a_inter = a1 * (1. + nhr/2. * d) / (1. - nhr/2. * d)
	
	a.append(a_inter - a1)
	print [str(i) for i in a]
	print [str(i) for i in mass]
	
	print "Running loop"
	for i in xrange(len(mass)-1):
		denom = ((mass[i] + mass[i+1]) / (3. * Msun))**(1./3.)
#		print str(denom)
		a2 = a[i] * (1. + nhr/2. * denom) / (1. - nhr/2. * denom)
		print (a2 - a[i-1])/ au
		a.append(a2 - a[i])
		
	for i in xrange(len(a)):
		a[i] = a[i] / au
		
	return a
