import hcal_teststand.uhtr as uhtr
import hcal_teststand.hcal_teststand as hc
from hcal_teststand.utilities import time_string
from time import sleep
import sys
from optparse import OptionParser

def main(group, outfilename, n_orbits=1000000):
    t = time_string()[:-4]

    tsname = "HEfnal"
    if group == 2:
        tsname = "HEfnal2"
    ts = hc.teststand(tsname)

    out = "{0}/histo_{1}".format("data/long_histos", t)
    if outfilename:
        out = "{0}/{1}".format("data/long_histos", outfilename.replace(".root",""))

    histo_output = uhtr.get_histos(ts,
                                   n_orbits,
                                   sepCapID=0,
                                   file_out_base=out,
                                   script = False)                                           

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-n", "--norbits", dest="n_orbits",
                      type="int", default=1000000,
                      help="Number of orbits to take data."
                      )
    parser.add_option("-o", "--outfilename", dest="outfilename",
                      type="string", default=None,
                      help="Name of the output file."
                      )
    parser.add_option("-g", "--group", dest="group",
                      type="int", default=None,
                      help="Group (1 or 2)"
                      )
    (options, args) = parser.parse_args()

    try:

#        while True:
        print "Starting histo run at", time_string()[:-4]
        main(options.group, options.outfilename, options.n_orbits)
        print "Finished histo run at", time_string()[:-4]
#            sleep(60*5)

    except KeyboardInterrupt:
        print "Bye!"
        sys.exit()
