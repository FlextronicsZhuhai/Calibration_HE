import subprocess
import commands

def initLinks(ts,OrbitDelay=31, Auto_Realign=1, OnTheFlyAlignment=0, CDRreset=1,GTXreset=1, verbose=True):
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

def linkStatus():
    cmds = [
        '0',
        'link',
        'status',
        'quit',
        'exit',
        '-1'
        ]
    p = subprocess.Popen(cmds,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    output_status = uhtr.send_commands(ts, crate =  ts.be_crates[0], slot=ts.uhtr_slots[0], cmds=cmds,script=True)

    return output_status

