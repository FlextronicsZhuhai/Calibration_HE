#Script to inject charge into the QIEs with the DAC and make histograms using the uHTR tool corresponding to each of the charge values 


from ROOT import *
from array import array
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--dir", dest="dirName", default="" ,
                  help="output directory" )
parser.add_option("-t", "--tag", dest="tagName", default="test" ,
                  help="output filename prefix" )
parser.add_option("-s", "--scan", dest="scan", default="custom" ,
                  help="choose which scan you would like to perform: range0, range1, range2, range3, custom" )
parser.add_option("-c", "--chnl", dest="channel",default="25" ,
                  help="choose which channels to run the script over")
parser.add_option("-m", "--hist", dest="hist", default="96",
		  help="choose the histogram number")
parser.add_option("-q", "--quick", dest="quick",default=False ,action="store_true",
                  help="enabling this skips the drawing and saving of each histogram")

(options, args) = parser.parse_args()

gROOT.SetBatch(kTRUE)
can = TCanvas("can","can",500,500)
can.SetLogy()
mean = [array("d") for i in range(12)]
rms = [array("d") for i in range(12)]
dac = [array("d") for i in range(12)]

first = True
color = 1
low_val = [ i for i in range(40,500,20)] #+ [ i for i in range(700,1501,150)]+[i for i in range(2000, 10000, 400)]+[i for i in range(10000, 48000,3000)]
high_val = [i for i in range(40,500,20)] #+ [ i for i in range(700, 1501,50)] +[i for i in range(2000, 10000, 200)] +[i for i in range(10000,48000,2000)]


histo = [ i for i in range(120,132)]#+[i for i in range(102,114)]
canMeanVdac = TCanvas("canMeanVdac","canMeanVdac",500,500)
canMeanVdac.SetLogx()
canRMSVdac = TCanvas("canRMSVdac","canRMSVdac",500,500)
canRMSVdac.SetLogx()
canRMSVmean = TCanvas("canRMSVmean","canRMSVmean",500,500)
canRMSVmean.SetLogy()
for j in histo:
	for i in high_val:
		f = TFile("{0}/Scan_channel_-1_dac_{1}_lowCurrent.root".format(options.dirName,i),"READ")
	
		h = f.Get("h{0}".format(j))
		#h.SetBinContent(1,0)
		print "RMS:",h.GetRMS()
		# if(h.GetRMS() <= 0.5 and h.GetMean() >= 100.):
		#h.GetXaxis().SetRangeUser(h.GetMean() - 6 , h.GetMean() + 6)
		#else :
		#h.GetXaxis().SetRangeUser(h.GetMean() - 15*h.GetRMS() , h.GetMean() + 15*h.GetRMS())
		mean[j-120].append(h.GetMean())
		rms[j-120].append(h.GetRMS())
		dac[j-120].append(i)
		h.SetLineWidth(1)
		h.SetLineColor(2)
    
		h.Draw()
		h.GetYaxis().SetTitle("ADCdist")
		h.GetYaxis().SetTitleSize(0.045)
		h.GetYaxis().SetTitleOffset(1.8)
		can.Clear()
		can.SaveAs("{0}/ADC_lowCurr_DAC{1}_channel{2}.png".format(options.dirName,i,j))
		can.SaveAs("{0}/ADC_lowCurr_DAC{1}_channel{2}.pdf".format(options.dirName,i,j))

	print len(mean[j-120])
	print len(dac[j-120])
	print len(rms[j-120])

	canMeanVdac.Clear()
	canRMSVmean.Clear()
	canRMSVdac.Clear()

	meanVdac = TGraph(len(dac[j-120]),dac[j-120],mean[j-120])
	meanVdac.GetXaxis().SetTitle("DAC Voltage")
	meanVdac.GetYaxis().SetTitle("Mean of ADC")
	meanVdac.SetMarkerStyle(8)
	meanVdac.Draw("Ap")
	canRMSVdac.SaveAs("{0}/MeanVdac_lowCurr_hist{1}.png".format(options.dirName,  j))
	canRMSVdac.SaveAs("{0}/MeanVdac_lowCurr_hist{1}.pdf".format(options.dirName,  j))
	canRMSVdac.Clear()
	rmsVdac = TGraph(len(dac[j-120]),dac[j-120],rms[j-120])
	rmsVdac.SetMarkerStyle(8)
	rmsVdac.GetXaxis().SetTitle("DAC LSB")
	rmsVdac.GetYaxis().SetTitle("RMS of ADC")
	rmsVdac.Draw("Ap")
	canRMSVdac.SaveAs("{0}/RMSVdac_lowCurr_hist{1}.png".format(options.dirName,  j))
	canRMSVdac.SaveAs("{0}/RMSVdac_lowCurr_hist{1}.pdf".format(options.dirName,  j))	
	canRMSVdac.Clear()
	rmsVmean = TGraph(len(dac[j-120]),mean[j-120],rms[j-120])
	rmsVmean.SetMarkerStyle(8)
	rmsVmean.GetXaxis().SetTitle("Mean ADC")
	rmsVmean.GetYaxis().SetTitle("RMS")
	rmsVmean.Draw("Ap")
	canRMSVdac.SaveAs("{0}/RMSVmean_lowCurr_hist{1}.png".format(options.dirName, j))
	canRMSVdac.SaveAs("{0}/RMSVmean_lowCurr_hist{1}.pdf".format(options.dirName, j))                                                                                                                                                              
