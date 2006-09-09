import string
import time
import os
import sys
import socket
import gnpcMessage


######################################################################
#
# Inventory of a system
#
######################################################################
#
#   The following attributes are recorded:
#
#    - Short_hostname
#    - ip_address
#    - fqdn_hostname
#    - aliases
#    - addresses
#    - platform
#    - operating_system_name
#    - sys_hostname
#    - os_release
#    - patch_level
#    - architecture
#
#  Big outstanding problems are that I don't know how to get
#  os_release and patch_level on MS-Windows.  In fact,  I don't
#  know how to distinguish between different versions of MS-Windows
#  ('95, '98, NT 3.51, NT 4, Win2k) or releases (e.g SP1-SP6)
#
#  MPE, VMS, MacOS are all unimplemented.  MS-DOS and OS/2 aren't
#  tested.
#
#  Netware would be good to do here.
#
#
#  Vague thoughts of other things that would be nice to know
# about:
#   - NIS/NIS+/SMB/NetWare domain of the computer
#   - distribution name and release (for Linux systems)
#   - hardware inventory (e.g. amount of memory,  CPU speeds, total
#     disk space?)
#
#######################################################################
#
# Installed software inventory
#
######################################################################
#
# There's a big of a software listing mechanism,
# which should give:
#    - package name
#    - package version
#    - a short package description
#    - package install date
#
# HP-UX data is rather big,  as it gets every last little drop of
# data from swlist -v.  (On an HP-UX 10.20 system,  the pickle of
# it was 150k in size!)
#
# Linux RPM is probably OK,  but maybe we want to include more
# information.
#
#
# Big issues here..
#
# -  I don't have the first clue how to start doing this on MS-Windows,
# (nor OS/2 nor MacOS).
#
# -  Can't test Linux/Hurd Debian packages
#
# -  Haven't implemented Solaris, AIX, Tru64, IRIX, or *BSD.
#
# -  Don't think that it is possible on Slackware (.tgz),
#    SCO (no package management) or BSDI.


DO_SEND_SOFTWARE_LISTING = 1
COMMON_UNIX_PATHNAMES_FOR_SOFTWARE_LISTING_TOOL = ['/sbin','/bin','/usr/sbin','/usr/bin','/usr/local/bin','/usr/local/sbin']

class InventoryOfSystem(gnpcMessage.gnpcMessage):
    """Has to be constructed with unpickling=0 if you want it to
    actually do anything"""
    def __init__(self,unpickling=1):
        if unpickling == 1:
            return
        short_hostname = socket.gethostname()
        ip_address = socket.gethostbyname(short_hostname)
        fqdn_hostname = socket.gethostbyaddr(ip_address)[0]
        aliases = socket.gethostbyaddr(ip_address)[1]
        addresses = socket.gethostbyaddr(ip_address)[1]
        platform  = sys.platform
        if os.name == 'posix':
            operating_system_name = os.uname()[0]
            sys_hostname = os.uname()[1]
            os_release = os.uname()[2]
            patch_level = os.uname()[3]
            architecture = os.uname()[4]
        elif os.name == 'nt':
            # ### WinNT alternatives ... can I distinguish
            # ### Win95 from WinNT or from Win2000?  This would
            # ### probably be helpful.
            operating_system_name = 'WinNT'
            sys_hostname = short_hostname
            os_release = 'unknown'
            # this would be nice also
            patch_level = 'unknown'  # this would be nice also
            architecture = 'probably x86' # /alpha/ppc/mips' etc????
        elif os.name == 'os2':
            operating_system_name = 'OS2'
            sys_hostname = short_hostname
            os_release = 'unknown'
            patch_level = 'unknown'
            architecture = 'x86'
        elif os.name == 'dos':
            # this would be very odd!
            operating_system_name = 'dos'
            sys_hostname = short_hostname
            os_release = 'unknown'
            patch_level = 'unknown'
            architecture = 'x86'
        elif os.name == 'mac':
            # don't know about MacOS/X
            operating_system_name = 'MacOS'
            sys_hostname = short_hostname
            os_release = 'unknown'
            patch_level = 'unknown'
            architecture = 'powerpc? 68k?'
        else:
            operating_system_name = platform
            # possibilities here would be MPE, VMS, MVS and a few others???
            sys_hostname = short_hostname
            os_release = 'totally unknown'
            patch_level = 'totally unknown'
            architecture = 'totally unknown'
        self.dictionary = {}
        self.dictionary['short_hostname'] = short_hostname
        self.dictionary['ip_address'] = ip_address
        self.dictionary['fqdn_hostname'] = fqdn_hostname
        self.dictionary['aliases'] = aliases
        self.dictionary['addresses'] = addresses
        self.dictionary['platform'] = platform
        self.dictionary['operating_system_name'] = operating_system_name
        self.dictionary['sys_hostname'] = sys_hostname
        self.dictionary['os_release'] = os_release
        self.dictionary['patch_level'] = patch_level
        self.dictionary['architecture'] = architecture
        if DO_SEND_SOFTWARE_LISTING == 1:
            self.software_listing()

    def software_listing(self):
        self.software_list = []
        if os.name == 'posix':
            unix = os.uname()[0]
            if unix == 'HP-UX':
                self.do_hpux_software_listing()
            if unix == 'Linux':
                self.do_rpm_software_listing()
                # rpm could be on almost anything (but probably Linux)
                # self.do_debian_software_listing()
            if unix == 'Solaris':
                # self.do_solaris_software_listing()

    def nature(self):
        return InventoryOfSystem


    ###################################################


    def do_hpux_software_listing(self):
        # swlist will be on HP-UX only
        swlist = os.popen("/usr/sbin/swlist -v",'r')
        try:
            while 1:
                self.software_list.append(
                    HPUX_swdistributor_SoftwareItem(swlist)
                    )
        except NoMoreLinesOfData:
            pass
        swlist.close()

    def do_rpm_software_listing(self):
        # I'd love to use the Python RPM access library,  but
        # it appears to be only on RedHat.  Anyway,  this seems
        # to work without too much trouble.
        rpm = None
        for path in COMMON_UNIX_PATHNAMES_FOR_SOFTWARE_LISTING_TOOL:
            fname = os.path.join(path,'rpm')
            if os.path.exists(fname):
                rpm = fname
                break
        if rpm is None: return
        rpmoutput = os.popen(rpm + " -q -a --queryformat '%{NAME}\\t%{VERSION}\\t%{SUMMARY}\\t%{INSTALLTIME}\\n'")
        for line in rpmoutput.readlines():
            self.software_list.append(SoftwareItem(line))

    def do_debian_software_listing():
        raise "I don't have a Debian machine to test this on"

    def do_solaris_software_listing():
        raise "Solaris software listing not implemented yet"

    def do_winnt_software_listing():
        raise "I don't know how to do a software listing on WinNT"
    
    def do_tru64_software_listing():
        # something about setld -i here
        raise "Tru64 software listing not implemented yet" 

    def pkg_info_software_listing():
        # /usr/sbin/pkg_info -a
        if os.path.exists('/usr/sbin/pkg_info'):
            data = os.popen('/usr/sbin/pkg_info -a').readline()
            
        raise "*BSD software listing not implemented yet"

        


class SoftwareItem:
    def __init__(self,str=None,version=None,description=None,install_date=None):
        if str is None:
            # I must be being unpickled,  or subclassed
            return
        if (version,description,install_date) == (None,None,None):
            # then I am being constructed from a line of tab-separated
            # data (from a  program's output?)
            try:
                parts = string.split(str,'\t',4)
                name = parts[0]
                version = parts[1]
                description = parts[2]
                install_date = string.atof(parts[3])
            except IndexError:
                raise "Couldn't make sense out of the line",str
            except ValueError:
                raise "Couldn't understand the following floating point number for an install time",parts[3]
        else:
            name = str
        self._name = name
        self._version = version
        self._description = description
        self._install_date = install_date
    def name(self): return self._name
    def version(self): return self._version
    def description(self): return self.__description
    def install_date(self): return self._install_date
    def readable_install_date(self): return time.asctime(time.gmtime(self._install_date))

class NoMoreLinesOfData:
    def __init__(self): pass


whitespace_simplification_translation = string.maketrans(string.whitespace,' ' * len(string.whitespace))




######################################################################
####################### HPUX Software Distributor ####################
######################################################################

class HPUX_swdistributor_SoftwareItem(SoftwareItem):
    def __readline(self):
        line = '#'
        while (line != '') and (line[0] == '#'):
           line = self.fd.readline()
           #print line
        if line == '':
            del self.fd
            raise NoMoreLinesOfData()
        return line
    def __init__(self,fd=None):
        SoftwareItem.__init__(self)
        if fd is None:
            # being unpickled,  don't need to do anything then
            return
        self.fd = fd
	self.data = {}
        # An individual package in an swlist -v output
        #  - begins with a name (indented by two spaces)
        #  - then many lines of attribute      value
        #      - some values are multi-line beginning with "
        #      - install_date is a floating point number
        #      - some values are blank
        #  - ends with a blank line or EOF.
        line = ''
        while (len(line) < 3) or ((line[0:1] == '  ') and (line[2] != ' ')):
            line = self.__readline()
        self._name = line[2:-1]  # get rid of that pesky new line
        line = self.__readline()
        #print line
        while string.strip(line) != '':
            #line = string.translate(line,whitespace_simplification_translation)
            parts = string.split(line,' ',1)
            #print "<<PARTS>>: ",len(parts)," length ",parts
            for i in range(len(parts)):
                parts[i] = string.strip(parts[i])
            if (len(parts) == 1) or (parts[1]==''):
                self.add_software_attribute(line)
                line = self.__readline()
                continue
            if parts[1][0] == '"':
                #print " <<###>>> CONTINUATION"
                # hmm, continuation.
                text = parts[1]
                while text[-1] != '"':
                    cont_line = self.__readline()
                    #print " <<###>>> CONTINUATION",cont_line
                    cont_line = string.rstrip(cont_line)
                    text = text + '\n' + cont_line
            elif parts[0] == 'install_date':
                #text = time.asctime(time.localtime(string.atof(parts[1])))
                # on second thoughts,  maybe I want to have the
                # install time as a number
                text = string.atof(parts[1])
            else:
                text = parts[1]
            key = parts[0]
            self.add_software_attribute(key,text)
            line = self.__readline()
            #print line
        # Let's get the version number.
        if self.data.has_key('revision'): self._version = self.data['revision']
        elif self.data.has_key('version'): self._version = self.data['version']
        else: self._version = 'unknown'
        #self._version  = self.data['revision']
        try:
            self._install_date = self.data['install_date']
        except:
            self._install_date = 'unknown'
        try:
            self._description = self.data['description']
        except:
            self._description = '<<No description>>'
        del self.fd
    def add_software_attribute(self,key,text=''):
        if self.data.has_key(key):
            if type(self.data[key]) == type([]):
                self.data[key].append(text)
            else:
                self.data[key] = [self.data[key],text]
        else:
            self.data[key] = text

#def hpux_software_listing():


#def rpm_software_listing():
#    rpm = os.popen('rpm -q -a --queryformat "%{NAME}\\t%{VERSION}"') 
#    return rpm 

