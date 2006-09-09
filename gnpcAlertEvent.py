import gnpcMessage
import string
import sys
import time
import rfc822 # for parsedate
import socket
up = string.upper

# The order of the following is important (it is used when displaying as
# text).  Also it is important that they begin with different letters
# (for the benefit of [gnpc message])
standard_fields=['SEVERITY','WHEN','HOSTNAME','APPLICATION','OBJECT','CATEGORY','NATURE','TEXT']

# The is also for [gnpc message]'s benefit
field_acronyms = {}
short_options = ''
for s in standard_fields:
    # one letter, upper case and lower case
    field_acronyms[s[0]] = s
    field_acronyms[string.lower(s[0])] = s
    short_options = s[0] + string.lower(s[0])
    # full word,  all upper, all lower,  and first upper
    field_acronyms[s] = s
    field_acronyms[string.lower(s)] = s
    field_acronyms[s[0]+string.lower(s[1:])] = s




UNKNOWN = '<<value unknown/undefined>>'

class gnpcAlertEvent(gnpcMessage.gnpcMessage):
    def __init__(self,parameters=None):
        if parameters is None:
            # we are being unpickled
            return
        gnpcMessage.gnpcMessage.__init__(self)
        self.parameters = {}
        for (key,value) in parameters:
            self.parameters[up(key)] = value
        self.correct_any_missing_standard_fields()

    def set_severity(self):
        if not(self.parameters.has_key('SEVERITY')):
            self.parameters['SEVERITY']=UNKNOWN
        else:
            self.parameters['SEVERITY']=up(self.parameters['SEVERITY'])

    def set_node(self):
        if not(self.parameters.has_key('HOSTNAME')):
            try:
                ghba = socket.gethostbyaddr
                ghbn = socket.gethostbyname
                self.parameters['HOSTNAME'] = ghba(ghbn(socket.gethostname()))[0]
            except:
                raise 'Nodename undefined in event'

    def set_misc(self):
        for field in standard_fields:
            if not(self.parameters.has_key(field)):
                self.parameters[field] = UNKNOWN

    def set_when(self):
        if not(self.parameters.has_key('WHEN')):
            self.parameters['WHEN'] = time.time()
        else:
            tstamp = self.parameters['WHEN']
            if type(tstamp) == type(0.0):
                # good
                pass
            elif type(tstamp) == type(0):
                tstamp = tstamp + 0.0
            elif type(tstamp) == type(''):
                parsedtime = rfc822.parsedate(tstamp)
                if parsedtime is None:
                    raise 'WHEN not understood',parsedtime
                tstamp = time.mktime(parsedtime)
            elif type(tstamp) == type( (0,) ):
                tstamp = time.mktime(tstamp)
            else:
                raise 'WHEN not understood',tstamp
            self.parameters['WHEN'] = tstamp

    def correct_any_missing_standard_fields(self):
        set_severity()
        set_node()
        set_when()
        set_misc()

    def setAttribute(self,key,value):        self.parameters[up(key)] = value
    def getAttribute(self,key,value):        return self.parameters[up(key)]
    def keys(self):                          return self.parameters.keys()
    def values(self):                        return self.parameters.values()
    def items(self):                         return self.parameters.items()
            

    def TextDisplay(self,fp=None):
        print self.parameters
        if fp is None: fp = sys.stdout
        if self.parameters.has_key('ID'):
            fp.write('['+`self.parameters['ID']`+']')
        fp.write('Severity='+self.parameters['Severity']+'\n')
        fp.write('Timestamp='+time.ctime(self.parameters['Timestamp'])+'\n')
        for field in standard_fields[2:]:
            fp.write(field+'='+self.parameters[field]+'\n')
        fp.write('\n')
        for k in self.keys():
            if k not in standard_fields:
                if type(self[k])==type(''):
                    fp.write('OTHER FIELD('+k+')='+self.parameters[k])
                else:
                    fp.write('OTHER FIELD('+k+')='+`self.parameters[k]`)
