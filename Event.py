import UserDictCaseless
import string
import sys
import time
import rfc822 # for parsedate

standard_fields=['SEVERITY','TIMESTAMP','NODE','APPLICATION','OBJECT','CATEGORY','TYPE','TEXT']


class Event(UserDictCaseless.UserDictCaseless):
    def __init__(self,dictionary=None,*largs,**kwargs):
        UserDictCaseless.UserDictCaseless.__init__(self,dictionary)
        self.dict = {}
        for str in largs:
            try:
                [l,r] = string.split(str,'=',2)
                self[l] = r
            except:
                pass
        self.dict.update(kwargs)
        if not(self.has_key('severity')):
            self['severity']='unknown'
        else:
            self['severity']=up(self['severity'])
        if not(self.has_key('timestamp')):
            self['timestamp'] = time.time()
        else:
            tstamp = self['timestamp']
            if type(tstamp) == type(0.0):
                # good
                pass
            elif type(tstamp) == type(0):
                tstamp = tstamp + 0.0
            elif type(tstamp) == type(''):
                parsedtime = rfc822.parsedate(tstamp)
                if parsedtime is None:
                    raise 'Timestamp not understood',parsedtime
                tstamp = time.mktime(parsedtime)
            elif type(tstamp) == type( (0,) ):
                tstamp = time.mktime(tstamp)
            else:
                raise 'Timestamp not understood',tstamp
            self['timestamp'] = tstamp
        if not(self.has_key('node')):
            try:
                import socket
                self['NODE'] = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))[0]
            except:
                raise 'Nodename undefined in event'
        for field in ['application','object','category','type','text']:
            if not(self.has_key(field)):
                self[field] = 'unknown'
    def TextDisplay(self,fp=None):
        print self.data
        if fp is None: fp = sys.stdout
        if self.has_key('ID'):
            fp.write('['+`self['ID']`+']')
        fp.write('Severity='+self['Severity']+'\n')
        fp.write('Timestamp='+time.ctime(self['Timestamp'])+'\n')
        for field in standard_fields[2:]:
            fp.write(field+'='+self[field]+'\n')
        fp.write('\n')
        for k in self.keys():
            if k not in standard_fields:
                if type(self[k])==type(''):
                    fp.write('OTHER FIELD('+k+')='+self[k])
                else:
                    fp.write('OTHER FIELD('+k+')='+`self[k]`)
