import jawalib as jl
import os
	
def create_info(info, dir, sim_name):
	dump_num = 0
	done_success = False
	
	#get integration parameters
	for line in info:
		if "Algorithm" in line:
			a = line.split("Algorithm: ",1)[1].split("\n",1)[0]
		if "Integration start epoch:" in line:
			b = line.split()[3]
		if "Integration stop  epoch:" in line:
			c = line.split()[3]
		if "Output interval: " in line:
			d = line.split()[2]
		if "Output precision: " in line:
			e = line.split()[2]
		if "Initial timestep: " in line:
			f = line.split()[3]
		if "Accuracy parameter: "  in line:
			g = line.split()[2]
		if "Central mass: " in line:
			h = line.split()[2]
		if "J_2:" in line:
			i = line.split()[1]
		if "J_4:" in line:
			j = line.split()[1]
		if "J_6:" in line:
			k = line.split()[1]
		if "Ejection distance: " in line:
			l = line.split()[2]
		if "Radius of central body: " in line:
			m = line.split()[4]
		if "Includes collisions: " in line:
			n = line.split()[2]
		if "Includes fragmentation: " in line:
			o = line.split()[2]
		if "Includes relativity: " in line:
			p = line.split()[2]
		if "Includes user-defined" in line:
			q = line.split()[4]
		if "Number of Big bodies: " in line:
			r = line.split()[4]
		if "Number of Small bodies: " in line:
			s = line.split()[4]
		#Extract integration details after this point
		if "Initial energy:" in line:
			t = line.split()[2]
		if "Initial angular" in line:
			u = line.split()[3]
		if "Continuing " in line:
			dump_num = dump_num + 1
		if "Integration complete." in line:
			done_success = True
	collated_info = [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,dump_num,done_success]
	
	#	if "due to integrator:" in line:
	#		print line.split()[6]
	#	if "Fractional angular momentum change:" in line:
	#		print line.split()[4]
	#	if "Fractional energy c
	
	#Now I need to check on my big bodies
	big_data = jl.scribe('null', "/big.in", dir, 'ol')
	
	system_events,event_data,big_index,big_names = [],[],[],[]
	
	#Extract style, epoch, and name line
	for i in xrange(len(big_data)):
		line = big_data[i]
		if "style" in line:
		 	style = line.split("= ", 1)[1].split("\n",1)[0]
		if "epoch" in line:
			epoch = line.split("= ", 1)[1].split("\n",1)[0]
		if "m=" in line:
			big_index.append(i)
	#Extract the names of the big bodies
	for i in big_index:
		big_names.append(big_data[i].split()[0])
	
	#Extract mass, r, and hill radii
	for i in xrange(len(big_names)):
		line = big_data[big_index[i]]
		if "\n" in line:
			line = line.split("\n",1)[0]
			
		name = big_names[i]
		mass = line.split("m=",1)[1].split()[0]
		hill_radi = line.split("r=",1)[1].split()[0]
		density = line.split("d=",1)[1].split()[0]
	
		#Now to extract more info from the info.out, collisions and ejections.:
		for thing in info: 
			if name in thing:
				what_happened = thing.split(big_names[i],1)[1].split("at",1)[0].strip()
				when_happened = thing.split(big_names[i],1)[1].split("at",1)[1].strip()
				event_data = [name, what_happened, when_happened]
		if event_data:
			if event_data[0] != name:
				event_data = [name, "Stable", "Stable"]
		else:
			event_data = [name, "Stable", "Stable"]
		
		if os.path.isfile(dir + "/" + name+ ".aei"):
			event_data.append("Unpacked")
		else:
			event_data.append("Not unpacked")
			
		system_events.append(event_data)
	return [sim_name, collated_info, system_events]
