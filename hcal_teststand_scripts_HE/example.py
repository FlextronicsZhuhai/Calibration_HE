####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: This is a script skeleton.                          #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
import sys

# CLASSES:
# /CLASSES

# FUNCTIONS:
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	name = ""
	if len(sys.argv) == 1:
		name = "904"
	elif len(sys.argv) == 2:
		name = sys.argv[1]
	else:
		name = "904"
	
	print "\nYou've just run a script that's a skeleton for making your own script.\n"
	
	# Initialize a teststand object:
	ts = teststand(name)		# This object stores the teststand configuration and has a number of useful methods.
#	ts.update()		# Set version info in each component.
	
	# Print out some information about the teststand:
	ts.Print()
#	print ">> The teststand you're using is named {0}.".format(ts.name)
#	print ">> The BE crate and uHTR organization for the teststand is below:\n{0}".format(ts.be)
#	print ">> The FE crate and QIE card organization for the teststand is below:\n{0}".format(ts.fe)
# /MAIN
