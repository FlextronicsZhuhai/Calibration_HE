# uses uHTRs for QIE testing

import os
import sys        
from subprocess import Popen, PIPE

##### simplifying functions from other files 

def send_commands(crate=None, slot=None, cmds=''):
    # Sends commands to "uHTRtool.exe" and returns the raw output and a log. The input is the crate number, slot number, and a list of commands.
    # Arguments and variables:
    raw = ""
    results = {}                # Results will be indexed by uHTR IP unless a "ts" has been specified, in which case they'll be indexed by (crate, slot).

    ## Parse cmds:
    if isinstance(cmds, str):
        print 'WARNING (uhtr.send_commands): You probably didn\'t intend to run "uHTRtool.exe" with only one command: {0}'.format(cmds)
        cmds = [cmds]

    # Prepare ip address:
    uhtr_ip = "192.168.%i.%i"%(crate, slot*4)

    # Prepare the uHTRtool arguments:
    uhtr_cmd = "uHTRtool.exe {0}".format(uhtr_ip)   

    # Send commands and organize results:
    # This puts the output of the command into a list called "raw_output" the first element of the list is stdout, the second is stderr.
    raw_output = Popen(['printf "{0}" | {1}'.format(' '.join(cmds), uhtr_cmd)], shell = True, stdout = PIPE, stderr = PIPE).communicate()
    raw += raw_output[0] + raw_output[1]
    results[uhtr_ip] = raw
    return results

def get_histo(crate, slot, n_orbits=5000, sepCapID=0, file_out=""):
        # Set up some variables:
        log = ""
        if not file_out:
                file_out = "histo_uhtr{0}.root".format(slot)

        # Histogram:
        cmds = [
                '0',
                'link',
                'histo',
                'integrate',
                '{0}'.format(n_orbits),                # number of orbits to integrate over
                '{0}'.format(sepCapID),
                '{0}'.format(file_out),
                '0',
                'quit',
                'quit',
                'exit',
                '-1'
        ]
        result = send_commands(crate=crate, slot=slot, cmds=cmds)
        return result
	
def histo_test(crate, slots, n_orbits=5000, sepCapID=0, file_out_base="", new_dir="uHTR_histotests_root_files"):
	if isinstance(slots, int):
		slots=[slots] 
	if not file_out_base:
		file_out_base="something"

	for slot in slots:
		file_out=file_out_base+"_{0}".format(slot)
		get_histo(crate, slot, n_orbits, sepCapID, file_out)
	return new_dir

###make sure this all works 
#crate=41
#slot=5
#result=get_histo(crate, slot, 5000, 0, "test1.root")
#print(result["192.168.%i.%i"%(crate, slot*4)])


















