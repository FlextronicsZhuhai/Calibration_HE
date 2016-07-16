from hcal_teststand import *
from hcal_teststand.hcal_teststand import teststand
import sys
from optparse import OptionParser
adcorder=[8,0,11,3,10,2,9,1]
tdcorder=[14,6,13,5,12,4]
if __name__=="__main__":
	parser=OptionParser()
	parser.add_option('-t','--teststand',dest='name',default='904',help="The name of the teststand you want to use (default is \"904\").")
	parser.add_option('-q','--qieid',dest='qieid',default='0x8D000000 0xAA24DA70',help="The ID of the QIE card we read.")
	(options, args) = parser.parse_args()
	ts = teststand(options.name)
	crateslot=ts.crate_slot_from_qie(qie_id=options.qieid)
	crate=crateslot[0]
	slot=crateslot[1]
	fldec=open('igloodec.txt','w')
	sepcut='---------------------------------------------------------------------------------------------------------------\n'
	ostr=sepcut+'channel(T/B)\t'
	for i in range(12):
		ostr+='{0}/{1}\t'.format(i+1,i+13)
	ostr+='\n'
	fldec.write(ostr)
        command1=['put HF{0}-{1}-iTop_CntrReg 0x2'.format(crate,slot),'put HF{0}-{1}-iTop_CntrReg 0x0'.format(crate,slot)]
        command2=['put HF{0}-{1}-iBot_CntrReg 0x2'.format(crate,slot),'put HF{0}-{1}-iBot_CntrReg 0x0'.format(crate,slot)]
        command3=['get HF{0}-{1}-iTop_StatusReg'.format(crate,slot),'get HF{0}-{1}-iTop_inputSpy'.format(crate,slot)]*512
        command4=['get HF{0}-{1}-iBot_StatusReg'.format(crate,slot),'get HF{0}-{1}-iBot_inputSpy'.format(crate,slot)]*512
        command1.extend(command2)
        command1.extend(command3)
        command1.extend(command4)
        outp=ngccm.send_commands_parsed(ts,command1)['output']
        for opt in outp:
            if opt['cmd'][:3] == 'put':
                if opt['result']=='OK':
                    continue
                else:
                    print 'ERROR: Cannot put CntrReg,',opt['cmd'],'failed'
                    exit()
	    ostr=''
	    if opt['cmd'][-3:] == 'Reg':
		    deco=bin(int(opt['result'][:-5],16))
		    ostr+=sepcut
		    ostr+='(Data_left:{0},  Empty:{1},  Full:{2})\n'.format(int(deco[:-2],2),deco[-2],deco[-1])
	    if opt['cmd'][-3:] == 'Spy':
		    ostr+=''
		    if opt['cmd'][-12:-9] == 'Top':
			    ostrid='capid(T)\t'
		    else:
			    ostrid='capid(B)\t'
		    ostradc='ADC\t\t'
		    ostrtdc='TDC\t\t'
		    bindecos=[]
		    hexdecos=opt['result'].strip("'").split()[1:]
		    for deco in hexdecos:
			    bindecos.append(bin(int(deco[:-4],16))[2:])
			    bindecos.append(bin(int(deco[-4:],16))[2:])
		    for deco in bindecos:
			    deco='0'*(16-len(deco))+deco
			    adc=''
			    tdc=''
			    for i in adcorder:
				    adc+=deco[15-i]
			    for i in tdcorder:
				    tdc+=deco[15-i]
			    capid=deco[0]+deco[8]
			    ostrid+='{0}\t'.format(int(capid,2))
			    ostradc+='{0}\t'.format(int(adc,2))
			    ostrtdc+='{0}\t'.format(int(tdc,2))
		    ostr+='{0}\n{1}\n{2}\n'.format(ostrid,ostradc,ostrtdc)
	    fldec.write(ostr)
	fldec.write(sepcut)
	fldec.close()

