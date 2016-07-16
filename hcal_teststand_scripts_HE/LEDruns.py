import hcal_teststand.hcal_teststand as hc
import hcal_teststand.ngfec
import os, sys
from optparse import OptionParser



parser = OptionParser()
parser.add_option("-t", "--teststand", dest="tstype",
                  type="string", default="HEfnal",
                  help="Which teststand to set up?"
                  )
parser.add_option("-l", "--ledAmplitude", dest="ledAmp",
                  type="float", default=0.5,
                  help="LED amplitude (0.5)"
                  )
parser.add_option("-s", "--shunt", dest="shunt",
                  type="int", default=0x00,
                  help="Shunt Setting (0x00)"
                  )

(options, args) = parser.parse_args()

if not options.tstype:
    print "Please specify which teststand to use!"
    sys.exit()
tstype = options.tstype

ts = hc.teststand(tstype)

amplitude = options.ledAmp
shunt = options.shunt

# commands to run
cmds1 = ["put HE1-pulser-ledA-enable 1",
         "put HE1-pulser-ledA-amplitude_f %f"%amplitude,
         "put HE1-pulser-ledA-delay_f 0.0",
         "put HE1-pulser-ledA-bxdelay 9",
         "put HE1-pulser-ledA-width_f 10.",
         "put HE1-pulser-ledB-enable 1",
         "put HE1-pulser-ledB-amplitude_f %f"%amplitude,
         "put HE1-pulser-ledB-delay_f 0.0",
         "put HE1-pulser-ledB-bxdelay 9",
         "put HE1-pulser-ledB-width_f 10.0",
         "wait",
         "put HE1-1-QIE[1-48]_Gsel 48*%i"%shunt]
         
output = hcal_teststand.ngfec.send_commands(ts=ts, cmds=cmds1, script=True)
print output

