import gnpcScheduler  # for gnpcFileDescriptorWrapper and Global_Scheduler
import socket

class gnpcIncomingConnectionWrapper(gnpcScheduler.gnpcFileDescriptorWrapper):
    def __init__(self,connection_constructor,hostname=None,portnum=None,family=None):
        if family is None: family = socket.AF_INET
        if portnum is None:
            portnum = gnpcSendMessage.default_send_port
        if hostname is None: hostname = ''
        self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection.bind(bind_hostname,bind_portnum)
        self.connection.listen(5)  # I think 5 here is OK.
        gnpcScheduler.gnpcFileDescriptorWrapper(self.connection)
        self.connection_constructor = connection_constructor
    def read_action(self):
        conn,addr = self.connection.accept()
        print "Right here I should be checking the source"
        print "address against a /etc/hosts.allow and"
        print "/etc/hosts.deny kind-of-thing.  This has not"
        print "yet been implemented,  and is a _major_ problem."
        print
        print "Connection from ",addr,"handle is",conn.fileno()
        gnpcScheduler.Global_Scheduler.add_input_source(self.connection_constructor(conn,addr))
        continue
