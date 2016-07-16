import sys
import subprocess

from hcal_teststand.uhtr import *
from hcal_teststand import *
from hcal_teststand.hcal_teststand import *
from hcal_teststand.qie import *
from checkLinks_Old import *

from read_histo import *

ts = teststand("HEfnal")

# uhtr.get_histos(ts=ts, n_orbits=1000, sepCapID=1, file_out_base="histotest")

# vals = read_histo("histotest.root",True,0)

# for i in vals:
#     print i, vals[i]

print_links(ts)
getGoodLinks(ts,22)
print_links(ts)
