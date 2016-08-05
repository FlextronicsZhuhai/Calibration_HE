from datetime import date, datetime
from time import sleep
import os
from optparse import OptionParser
import subprocess
import sys

from numpy import std
from ROOT import *

#script to control DAC
from DAC import *

#from scans import *

# from adcTofC import *
# from fitGraphs import *
from adcTofC_linearized_2d import *
from fitGraphs_linearized_2d import *
from GraphParamDist import *

from FitUncertaintyPlots import *

slotDict = {1:[18,19,20,21,23,24,25,26],
            }

shunt_Val ={1:0,
            1.5:1,
            2:2,
            3:4,
            4:8,
            5:16,
            6:18,
            7:20,
            8:24,
            9:26,
            10:28,
            11:30,
            11.5:31}        
shuntMultList = shunt_Val.keys()
shuntMultList.sort()

# sys.path.insert(0, '/home/hep/ChargeInjector/hcal_teststand_scripts_HE')

# from hcal_teststand.uhtr import *
# #from hcal_teststand import *
# from hcal_teststand.hcal_teststand import *
# #from hcal_teststand.qie import *

# from ngccmEmulatorCommands import *
# from simpleLinkMap import getSimpleLinkMap

import sqlite3 as lite

#from TDC_scan import *

from read_histo_2d import read_histo_2d

#from checkLinks_Old import *
#from checkLinks import *
#from SerialNumberMap import *

gROOT.SetBatch(kTRUE)

orbitDelay = 30
GTXreset = 1
CDRreset = 0

### Which slot number contains which injection card {slot:card}
### slots are numbered 1 to 8 (slot 10 contains the DAC, slot 9 has an extra injection card)
### The purpose of this dictionary is to allow for swapping out a nonfunctional card
injectionCardSlotMapping = {1:1,
                            2:2,
                            3:3,
                            4:4,
                            5:5,
                            6:6,
                            7:7,
                            8:8,
                            }

fakesimpleCardMap = {1  : 1 , 2  : 2 , 3  : 3 , 4  : 4 , 5  : 5 , 6  : 6 , 7  : 7 , 8  : 8 , 9  : 9 , 10 : 10, 11 : 11, 12 : 12, 13 : 13, 14 : 14, 15 : 15, 16 : 16, 17 : 17, 18 : 18, 19 : 19, 20 : 20, 21 : 21, 22 : 22, 23 : 23, 24 : 24, 25 : 25, 26 : 26, 27 : 27, 28 : 28, 29 : 29, 30 : 30, 31 : 31, 32 : 32,
                             }


#outputDir = 'Data_CalibrationScans/2016-07-14/Run_01'
#outputDirectory= 'Data_CalibrationScans/2016-07-14/Run_01'
def getValuesFromFile(outputDir):
        """
        Gets data from the cardData text file from the previous run
        Gets things like the injection mapping, QIE ranges used, etc.
        """

        dataFile = open(outputDir+"/cardData.txt",'r')
        for line in dataFile:
                if 'DAC' in line and 'Used' in line:
                        dacNumber = line.split()[1]
                if 'linkMap' in line:
                        linkMap = eval(line.split('linkMap')[-1])
                if 'injectionCardMap' in line:
                        injectionCardMap = eval(line.split('injectionCardMap')[-1])
        return linkMap, injectionCardMap 
                

def ShuntScan(shuntMult=1):
         

         #relayOn = False

         val={}
         output={}
         outputDirectory = options.Directory + '/'
         rootfile = options.filename
         final_file = outputDirectory+rootfile
         #print  final_file
         val= read_histo_2d(file_in=final_file,shuntMult=shuntMult)
      #   output[shuntMult]=val 
         
                 

         return val

def QIECalibrationScan(options):

        ts = None



        outputDirectory = options.Directory + '/'
        rootfile = options.filename
        final_file = outputDirectory+rootfile
        
        print "the root file is %s"%rootfile
        print "Reading from directory %s"%outputDirectory
        print "final file is %s"%final_file

        print '-'*30
        print 'Start Mapping'
        print '-'*30
        ## run mapping of injection cards to qie cards


        linkMap, injectionCardMap = getValuesFromFile(outputDirectory)


        simpleCardMap = fakesimpleCardMap
        histoList=[ i for i in range(15*6+6)]

        print '-'*30
        print 'Histograms List'
        print '-'*30
        print histoList



        outputParamFile = open(outputDirectory+"calibrationParams.txt",'w')
        outputParamFile.write('(qieID, serialNum, qieNum, capID, qieRange,shuntMult, outputDirectory, timeStamp, slope, offset)\n')

        uID_list = []
        for link in linkMap:
                uID = linkMap[link]['unique_ID'].replace(' ','_')
                if not uID in uID_list:
                        uID_list.append(uID)




        qieParams={}
        cursor = {}
        for uID in uID_list:
                 outputGraphFile = TFile("%s/fitResults_%s.root"%(outputDirectory, uID),"recreate")
                 outputGraphFile.mkdir("adcVsCharge")
                 outputGraphFile.mkdir("LinadcVsCharge")
                 outputGraphFile.mkdir("fitLines")
                 outputGraphFile.mkdir("Shunted_adcVsCharge")
                 outputGraphFile.mkdir("Shunted_LinadcVsCharge")
                 outputGraphFile.mkdir("Shunted_fitLines")
                 outputGraphFile.mkdir("SummaryPlots")
                 outputGraphFile.Close()
 
                 qieParams[uID] = lite.connect(outputDirectory+"qieCalibrationParameters_%s.db"%(uID))
                 cursor[uID] = qieParams[uID].cursor()
                 cursor[uID].execute("create table if not exists qieparams(id STRING, serial INT, qie INT, capID INT, range INT, directoryname STRING, date STRING, slope REAL, offset REAL)")
 
                 cursor[uID].execute("create table if not exists qieshuntparams(id STRING, serial INT, qie INT, capID INT, range INT, shunt INT, directoryname STRING, date STRING    , slope REAL, offset REAL)")

                 cursor[uID].execute("create table if not exists qietdcparams(id STRING, qie INT, tdcstart REAL)")



        ### Graph parameters
        outputParamFile_shunt = open(outputDirectory+"calibrationParams_shunt.txt",'w')
        outputParamFile_shunt.write('(qieID, serialNum, qieNum, capID, qieRange, shuntMult,outputDirectory, timeStamp, slope, offset)\n') 
        
        if options.RunShunt:
                print " Shunt Scans begin"
                shuntMult_list = shunt_Val.keys()
                shuntMult_list.sort()
                for shuntMult in shuntMult_list:
                    graphs_shunt ={}
                    output={}
                    print "Now on shuntMult %.1f"%shuntMult
                    shuntOutputDirectory = outputDirectory #+ "Data_%s_%s/"%(rangeMode, shuntMode)
                    vals = ShuntScan(shuntMult=shuntMult)
                    #print vals[shuntMult]
                    #sys.exit()
                    #qieRange = vals.keys()
                    #qieRange.sort()
                    #print qieRange
                    #sys.exit()
                    if shuntMult ==1:
                        qieRange= range(4)
                    else:
                        qieRange=range(3)
                    for i_range in qieRange:
                        histoList =  vals[i_range].keys()
                        histoList.sort()
                        for i_channel in histoList:
                           dac =  vals[i_range][i_channel].keys()
                           dac.sort()
                        #   print "dac values are", dac
                           linkMap=linkMap
                    
                           injectionCardMap=injectionCardMap
                            #qieRange=i_range
                           shuntMult = shuntMult
                         #  dac=[]
                        #print "dac values are",dac
                        graphs_shunt[i_range] = makeADCvsfCgraphSepCapID(dac,vals[i_range],histoList,linkMap=linkMap,injectionCardMap=injectionCardMap,qieRange=i_range,shuntMult=shuntMult)
                   #    print "Now printing out put from adcTofC"            
                        #print graphs_shunt
                        for ih in histoList:

                            linkNum = int(ih/6)
                            qieID = linkMap[linkNum]['unique_ID']
                    #injectionMapping[simpleCardMap[int(ih/12)]]['id']
                            serial = 699999

                            qieNum =ih%24 + 1
                            graphList_shunt=[]
                    #if 1 in graphs_shunt:

                            if 0 in graphs_shunt:
                                graphList_shunt.append(graphs_shunt[0][ih])
                            else:
                                graphList_shunt.append(None)
                            if 1 in graphs_shunt:
                                graphList_shunt.append(graphs_shunt[1][ih])
                            else:   
                                graphList_shunt.append(None)
                            if 2 in graphs_shunt:
                                graphList_shunt.append(graphs_shunt[2][ih])
                            else:
                                graphList_shunt.append(None)
                            if 3 in graphs_shunt:
                                graphList_shunt.append(graphs_shunt[3][ih])
                            else:
                                graphList_shunt.append(None)

                            params_shunt =  doFit_combined(graphList = graphList_shunt, saveGraph = False, qieNumber = qieNum, qieUniqueID = qieID.replace(' ', '_'), useCalibrationMode = False, outputDir = outputDirectory, shuntMult=shuntMult)

                            uID = qieID.replace(' ', '_')
                            for i_range in graphs_shunt:
                                for i_capID in range(4):
                                    values_shunt = (qieID, serial, qieNum, i_capID, i_range, shuntMult, outputDirectory, str(datetime.now()), params_shunt[i_range][i_capID][0], params_shunt[i_range][i_capID][1])
                                    cursor[uID].execute("insert into qieshuntparams values (?, ?, ?, ?, ?, ?, ?, ?, ? , ?)",values_shunt)
                                    print values_shunt
                                    outputParamFile_shunt.write(str(values_shunt)+'\n')
         
        #outputParamFile_shunt.close()
        for uID in uID_list:
                graphParamDist(outputDirectory+"qieCalibrationParameters_%s.db"%uID)

        for uID in uID_list:
                cursor[uID].close()
                qieParams[uID].commit()
                qieParams[uID].close()


        problemCards = []
        for uID in uID_list:
                outputFileName = "%s/fitResults_%s.root"%(outputDirectory, uID)
                badChannels = fillFitUncertaintyHists(outputFileName)
                if len(badChannels) > 0:
                        slot = -1
                        for i_link in linkMap:
                                if linkMap[i_link]['unique_ID']==uID.replace('_',' '):
                                        slot = linkMap[i_link]['slot']
                        problemCards.append([slot,uID.replace('_',' ')])
        outputParamFile_shunt.close()
        for card in problemCards:
                print '*'*40
                print 'PROBLEM WITH FIT IN QIE CARD'
                print '    Slot: ',card[0]
                print '    UnID: ',card[1]

                
if __name__ == "__main__":
        parser = OptionParser()
        parser.add_option("-r", "--range", dest="range", default=-1,type='int',
                          help="Specify range to be used in scan (default is -1, which does all 4 ranges)" )
        parser.add_option("--NoSepCapID", action="store_false",dest="sepCapID",default=True,
                          help="don't separate the different capID histograms")
        parser.add_option("--SkipScan", action="store_true",dest="SkipScan",default=False,
                          help="Skip the scan, using presaved scan")
        parser.add_option("--SkipFit", action="store_true",dest="SkipFit",default=False,
                          help="Skip the fitting step")
        parser.add_option("--NoLinkInit", action="store_true",dest="NoLinkInit",default=False,
                          help="Skip the scan, using presaved scan")
        parser.add_option("--SkipTDC", action="store_false",dest="RunTDCScan",default=True,
                          help="Skip the TDC scans")
        parser.add_option("--SkipExtraTests", action="store_false",dest="RunExtraTests",default=True,
                          help="Skip the Range Transistion and TDC tests")
        parser.add_option("--SkipShunt", action="store_false",dest="RunShunt",default=True,
                          help="Skip the Shunt Scans")
        parser.add_option("-d","--dir", dest="Directory",default="",type="str",
                          help="Data file from previous data taking run to redo the fit on")
        parser.add_option("-f","--filename",dest="filename",default="",type="str",
                         help="Root file to run on")
        (options, args) = parser.parse_args()
        print 'start'
        if not options.range == -1:
                options.RunTDCScan=False
        if not options.RunTDCScan:
                options.RunExtraTests = False

        options.RunExtraTests = False

        QIECalibrationScan(options)
        


