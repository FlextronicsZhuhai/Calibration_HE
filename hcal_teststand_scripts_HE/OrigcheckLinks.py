from hcal_teststand import *
from time import sleep
import sys
skipLinks = []

def initLinks(ts,OrbitDelay=3504, Auto_Realign=1, OnTheFlyAlignment=0, CDRreset=1,GTXreset=1, verbose=True):
    outLine = 'Init Links with orbit delay %i'%OrbitDelay
    if Auto_Realign: outLine+= ", with auto realign" 
    if OnTheFlyAlignment: outLine += ", with on the fly alignment"
    if CDRreset: outLine += ", with CDR reset"
    if GTXreset: outLine += ", with GTX reset"

    if verbose: print outLine
    
    cmds = [
        '0',
        'link',
        'init',
        str(Auto_Realign),
        str(OrbitDelay),
        str(OnTheFlyAlignment),
        str(CDRreset),
        str(GTXreset),
        'quit',
        'exit',
        '-1'
        ]
    output = uhtr.send_commands(ts, crate = ts.be_crates[0],  slot=ts.uhtr_slots[0], cmds=cmds,script=True)
    sleep(2)

    return output

def linkStatus(ts):
    cmds = [
        '0',
        'link',
        'status',
        'quit',
        'exit',
        '-1'
        ]
    
    output_status = uhtr.send_commands(ts, crate =  ts.be_crates[0], slot=ts.uhtr_slots[0], cmds=cmds,script=True)
    
    return output_status

def linkStatus2(ts):
    cmds = [
        '0',
        'link',
        'status',
        'quit',
        'exit',
        '-1'
        ]
    
    output_status = uhtr.send_commands(ts, crate=ts.be_crates[0],slot=ts.uhtr_slots[0], cmds=cmds, script=True)[(ts.be_crates[0],ts.uhtr_slots[0][0])].split('\n')

    # print output_status
    # print output_status[(41,4)]
    # print (ts.be_crates[0],ts.uhtr_slots[0][0])
    # print (ts.be_crates[0],ts.uhtr_slots[0][0])==(41,4)
    # print output_status[(ts.be_crates[0],ts.uhtr_slots[0][0])]

    
    return output_status[48:80]


def parseStatus(linkStatLines):

    linkStat = {}
    for i in range(24): linkStat[i]={}

    values = {1:['On',1],
              2:['BadData',2],
              3:['RolloverCount',2],
              4:['BadDataRate',3],
              5:['GTXResetCnt',3],
              7:['BPRStatus',2],
              8:['AODStatus',2],
              10:['AlignBCN',2],
              11:['AlignOCC',2],
              12:['AlignDelta',2],
              13:['OrbitRate',0],
              14:['BadAlign',2],
              }

    for ival in values:
        if not 'OrbitRate' in values[ival][0]:
            top = linkStatLines[ival].split()
            bottom = linkStatLines[ival+17].split()
        else:
            top = linkStatLines[ival].split('(kHz)')[-1].split()          
            bottom = linkStatLines[ival+17].split('(kHz)')[-1].split()          
        for i in range(12):
            linkStat[i][values[ival][0]] = top[i+values[ival][1]]
            linkStat[i+12][values[ival][0]] = bottom[i+values[ival][1]]

    return linkStat


def checkLinkStatus(ts, verbose=True):
    if verbose: print 'Checking Link Status'

    output_status = linkStatus2(ts)
    linkStat = parseStatus(output_status)

    linksGood = True
    problemType = 0  #Problem type, type 1 needs a link init, type 2 is orbit rate related, which means just wait to see if it improve
    problemLinks = []

    for i in linkStat:
        if linkStat[i]['On']=='ON' and i not in skipLinks:
            if not float(linkStat[i]['OrbitRate']) == 1.12e+01:
                linksGood = False
                if not i in problemLinks: problemLinks.append(i)
#                print i, 'Orbit'
                if problemType==0: problemType+=2
            if not linkStat[i]['BPRStatus']=='111':
                linksGood = False
                if not i in problemLinks: problemLinks.append(i)
#                print i, 'BPR'
                problemType = 1
            if not linkStat[i]['AODStatus']=='111':
                linksGood = False
                if not i in problemLinks: problemLinks.append(i)
#                print i, 'AOD'
                problemType = 1
            if int(linkStat[i]['AlignOCC']) == 0 or int(linkStat[i]['AlignOCC']) > 15:
                linksGood = False
                if not i in problemLinks: problemLinks.append(i)
#                print i, 'OCC'
                problemType = 1
            if int(linkStat[i]['AlignDelta']) == 0 or int(linkStat[i]['AlignDelta']) > 15:
                linksGood = False
                if not i in problemLinks: problemLinks.append(i)
#                print i, 'Delta'
                problemType = 1

    output_status2 = []

    dataBurstLinks = []
    if linksGood:
        sleep(0.1)
        output_status2 = linkStatus2(ts)
        linkStat2 = parseStatus(output_status2)
        for i in linkStat2:
            if linkStat[i]['On']=='ON' and i not in skipLinks:
                if not linkStat[i]['BadAlign']==linkStat2[i]['BadAlign']:
                    linksGood=False
                    if not i in problemLinks: problemLinks.append(i)
                    problemType = 3
                if not linkStat[i]['BadData']==linkStat2[i]['BadData']:
                    linksGood=False
                    if not i in problemLinks: problemLinks.append(i)
                    problemType = 3
                
                if not int(linkStat2[i]['BadData'])==0:
                    if not i in dataBurstLinks:
                        dataBurstLinks.append(i)
                    

    linkStatusText = ''
    for line in output_status:
        linkStatusText += line + '\n'
    linkStatusText2 = ''
    for line in output_status2:
        linkStatusText2 += line + '\n'

    return linksGood, [linkStatusText,linkStatusText2], problemLinks,problemType,dataBurstLinks


def print_links(ts, verbose = True):
    """
    checks the status of the links, and prints out either 'links good', or the link status output allowing with a list of problem links
    """
    linksGood, linkOutput, problemLinks, problemType, badDataBursts= checkLinkStatus(ts)
    if not linksGood:
        if verbose: print linkOutput[0]
        print "Problem with Links:",problemLinks
    else:
        print 'Links Good'
        
    return linksGood, problemType



def getGoodLinks(ts, orbitDelay = 28, CDRreset=True, GTXreset=True, forceInit = False):
    if forceInit: initLinks(ts,OrbitDelay=orbitDelay, CDRreset=CDRreset, GTXreset=GTXreset)
    counter = 0
    linksGood, linkOutput, problemLinks, problemType, badDataBursts = checkLinkStatus(ts, verbose=False)        
    while not linksGood:
        if not linksGood:
            if problemType == 1:
                initLinks(ts,OrbitDelay=orbitDelay, CDRreset=CDRreset, GTXreset=GTXreset)
            if problemType == 2:
                sleep(5)
                if counter in range(5,50,5):
                    initLinks(ts,OrbitDelay=orbitDelay, CDRreset=CDRreset, GTXreset=GTXreset)
        else:
            print "Links Good"
        linksGood, linkOutput, problemLinks, problemType, badDataBursts = checkLinkStatus(ts, verbose=False)        
        
        counter += 1        
        if counter > 10:
            print 'Bad Links'
            for line in linkOutput: print line
            from DAC import setDAC
            setDAC(0)
            sys.exit()
