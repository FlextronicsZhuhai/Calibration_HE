import hcal_teststand.hcal_teststand as hc
import hcal_teststand.ngfec
import os, sys
from optparse import OptionParser



parser = OptionParser()
parser.add_option("-t", "--teststand", dest="tstype",
                  type="string", default="HEfnal",
                  help="Which teststand to set up?"
                  )
parser.add_option("-b", "--biasvoltage", dest="bv",
                  type="float", default=70,
                  help="SiPM bias voltage (70)"
                  )
parser.add_option("-s", "--shunt", dest="shunt",
                  type="int", default=0x00,
                  help="Shunt Setting (0x00)"
                  )
parser.add_option("--BVon", dest="bvon",
                  action="store_true",
                  default=False,
                  help="Execute settings needed to activate the bias contral")
parser.add_option("-g", "--group", dest="group",
                  type="int", default=None,
                  help="Group (1 or 2)"
                  )

(options, args) = parser.parse_args()

if not options.tstype:
    print "Please specify which teststand to use!"
    sys.exit()
tstype = options.tstype
if options.group == 2:
    tstype += "2"
ts = hc.teststand(tstype)

biasvoltage = float(options.bv)
if biasvoltage > 75.0:
    sys.exit("You cannot apply a bias voltage greater than 75! Exiting...")
shunt = options.shunt

cmds1 = []

# Set the DAC for the bias control if needed
if options.bvon:
    for i, crate in enumerate(ts.fe_crates):
        for slot in ts.qie_slots[i]:
            if len(cmds1) > 0:
                cmds1.append("wait")
            cmds1.extend([
                    "put HE%s-%s-dac1-daccontrol_RefSelect 0" % (crate, slot),
                    "put HE%s-%s-dac1-daccontrol_ChannelMonitorEnable 1" % (crate, slot),
                    "put HE%s-%s-dac1-daccontrol_InternalRefEnable 1" % (crate, slot),
                    "put HE%s-%s-dac2-daccontrol_RefSelect 0" % (crate, slot),
                    "put HE%s-%s-dac2-daccontrol_ChannelMonitorEnable 1" % (crate, slot),
                    "put HE%s-%s-dac2-daccontrol_InternalRefEnable 1" % (crate, slot)
                    ])


# loop over all occupied slots
for i, crate in enumerate(ts.fe_crates):
    for slot in ts.qie_slots[i]:
        if len(cmds1) > 0:
            cmds1.append("wait")
        cmds1.append("put HE%s-%s-biasvoltage[1-48]_f 48*%.1f" % (crate, slot, biasvoltage))

#print cmds1
print "sending commands"
output = hcal_teststand.ngfec.send_commands(ts=ts, cmds=cmds1, script=True)
print "done"
for l in output:
    print "%s    %s" % (l['cmd'], l['result'])

