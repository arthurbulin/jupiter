#mercury.make created 24th August, 2015 by Arthur A. Bulin
#last modified 8-24-15
all: mercury6 element6 close6

mercury6_gr:
	g77 -o mercury6_gr mercury6_2_gr.for

element6:
	g77 -o element6 element6.for

close6:
	g77 -o close6 close6.for

runclean:
	rm ./*.out ./*.tmp ./*.dmp

clean:
	rm ./mercury6 ./element6 ./close6
