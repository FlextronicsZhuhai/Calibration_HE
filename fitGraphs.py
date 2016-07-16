from ROOT import *
from linearADC import *
from array import array
import sys
import os
import csv

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d", "--dir", dest="dirName", default="",
		 help="selecting the directory")
parser.add_option("-c", "--chnl", dest="channel",default="25" ,
                  help="choose which channels to run the script over")
parser.add_option("-m", "--hist", dest="hist", default="96",
                  help="choose the histogram number")
(options, args) = parser.parse_args()
gROOT.SetBatch(kTRUE)
gStyle.SetFuncWidth(1)
mean =[array('d') for i in range(12)]
rms=[array('d') for i in range(12)]
charge1=array('d')
charge2=array('d')
y_lin = [array('d') for i in range(12)]
rms_lin = [array('d') for i in range(12)]
y_mean=[array('d') for i in range(12)]
y_rms=[array('d') for i in range(12)]
dac=[array('d') for i in range(12)]
output = [array('d') for i in range(12)]
x_rms=[array('d') for i in range(12)]


gr =[] 
mg=TMultiGraph()
can = TCanvas("can","can",500,500)
low_val = [ i for i in range(40,500,20)] + [ i for i in range(700,1501,150)]#+[i for i in range(2000, 10000, 400)]+[i for i in range(10000, 48000,3000)]
high_val = [i for i in range(40,500,20)] + [ i for i in range(700, 1501,50)] #+[i for i in range(2000, 10000, 200)] +[i for i in range(10000,48000,2000)]
#print len(low_val)
for i in low_val:
	charge1.append((i-40)*1.3*5.6)
	
for i in high_val:
	charge2.append((i-40)*1.3)
histo=[i for i in range(120,132)]
l=[]	
for j in histo:
	for i in low_val:
		f = TFile("{0}/Scan_channel_-1_dac_{1}_highCurrent.root".format(options.dirName,i),"READ")
		
		h = f.Get("h{0}".format(j))
	
		mean[j-120].append(h.GetMean())
		rms[j-120].append(h.GetRMS())
		dac[j-120].append(i)

	for i in range(len(mean[j-120])):	
		meanlin,rmslin = ((linADC(mean[j-120][i],rms[j-120][i])))
		
		y_mean[j-120].append(meanlin)
		y_rms[j-120].append(rmslin)
		x_rms[j-120].append(0)
	l = [y_mean[j-120], y_rms[j-120], mean[j-120], rms[j-120]]
	print len(y_mean[j-120])
	print len(x_rms[j-120])
	print len(y_rms[j-120])
	print len(charge1)

	output = zip(*l)
	
	with open('Mean_RMS_lowResistor_hist{0}.csv'.format(j),'wb') as csvfile:
		writer= csv.writer(csvfile, delimiter =',')
		header =[ 'lin mean', 'lin rms', 'actual mean', 'rms']
		writer.writerow(header)
		for i in range(len(output)):
			writer.writerow(output[i])
		
	
	gr.append(TGraphErrors(len(charge1),charge1,y_mean[j-120],x_rms[j-120],y_rms[j-120]))
	gr[j-120].SetMarkerColor(4);
	gr[j-120].SetMarkerStyle(8);
	gr[j-120].SetMarkerSize(.5);
	gr[j-120].Fit("1++x")
	l.append(gr[j-120].GetFunction("1++x"))
	can.Clear()
        gr[j-120].Draw('AP') 

	
	gr[j-120].SetTitle("Linearized ADC vs Charge")
	gr[j-120].GetYaxis().CenterTitle(1)
	gr[j-120].GetXaxis().CenterTitle()
	gr[j-120].GetXaxis().SetTitle("Charge fC")
	gr[j-120].GetYaxis().SetTitle("Linearized ADC")


	can.SaveAs("lowResistor_hist{0}.pdf".format(j))
