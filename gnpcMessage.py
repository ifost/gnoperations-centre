import socket
import string
import os
import time
import pickle
import gnpcMessageHeaders

default_send_port = 5329

my_hostname = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))[0]


# A base class for all things that get transmitted across a
# network (except for the data transferred between proxies).
# This,  and all its subclasses need to be pickle-able.
# Maybe one day in the future this constrain will be changed
# (and they might implement a different  message.marshall()
# method).
#
# It has a method message.send(destination)
#
# The destination should be a string,  but it can be quite complicated.
# The destination could be in an of the following forms...
#
#   computer_name
#   computer_name:portnumber
#   computer_name1!computer_name2
#   computer_name1/computer_name2 
#   computer_name1,computer_name2
#
# or variations or combinations thereof.
#
# The  x!y syntax means "the ultimate destination is y,  but I
# get there by sending it to x".  This can be useful for
# networks hidden by NAT or firewalling.
#
# x/y means "try x,  if it fails,  try y"
#
# x,y means "send to x,  then send to y regardless of whether
# we succeeded with x"
#
#
#
# Precendence is  (,) then (/) then (!) then (:)
#
#
# This probably urgently needs to get turned into a full-blown
# scheme that supports parenthesis,  and such like.
#
# Here are some ideas for further extensions that I have had:
#
#
#   computer_name=30s
# x=30s means try x every 30 seconds until you succeed.
#
# Maybe one day I'll get really smart,  and there will be
# several different protocols also.  (e.g. http, smtp)
#
# Other thoughts are for notations to say "queue this gently", etc.
# I'm thinking this might be implemented by having a destination
# like   computer_name#30  (send to computer_name after a
# delay of 30 seconds),  computer_name@12:45:33 (send at a
# particular time),  fork()'ing off a deamon in the background
# to waiting for that send,  and then sending.  But that's a
# lot of processes sitting around until (say) and end-of-day,
# so perhaps that syntax should mean "send to computer_name
# now,  who will then wait until such-and-such a time,  to
# actually do something with it."  This would be nice for
# occasional dial-up networks.
#
# More thoughts.  Perhaps we could attach credentials somehow.
# Other goodies would be encrypted connections.


class CouldNotSendException:
    pass

class NonnumericPortException:
    def __init__(self,pstr):
        self.pstr = pstr


class gnpcMessage:
    def nature(self):
        """This method should be overridden by any subclass!"""
        return gnpcMessage

    def __init__(self):
        self.identifiers = []
        # Initially we have no identifiers
        # If we are being unpickled,  then this will be overriden
        # with something else.  We will call place_message_number()
        # later which will put our contribution onto this.
        
        self.forward_to_destination = None
        # This gets used when a message is sent to
        # a message forwarding daemon (it needs to know where
        # to send on to).

        # It could also be used by a subclass that wants to
        # specify a destination (in anticipation of obj.send()
        # being called without a destination parameter).

    def place_message_identifier(self):
        """We place a unique identifier number on each gnpcMessage
        so that a redundant management system can work out which are
        duplicate messages,  and which aren't.
        
        You can do cute things with this like:
           fronthost1!backhost,fronthost2!backhost
        Then (a) backhost can correlate duplicates based on the
        unique_detail of the message,  and (b) you can be pretty sure they
        are going to get there!"""

        my_pid = os.getpid()
        timenow = time.time()
        unique_detail = (my_hostname,my_pid,timenow())
        self.identifiers.append(unique_detail)

    def send(self,destination=None):
        if destination is None:
            destination = event['GNPC_DEST']
        self.place_message_identifier()

    def _send(self,destination):
        """This is message.send(destination) without the
        self.place_message_identifier()"""
        
        successfully_sent = 0

        COMMA = ','
        SLASH = '/'
        
        # Multiple do-all destinations (COMMA separated)
        splitup = string.split(destination,COMMA)
        if len(splitup) != 1:
            any_successful = 0
            for portion in splitup:
                try:
                    self._send(portion)
                    any_successful = 1
                except CouldNotSendException:
                    pass
            if any_successful:
                return
            raise CouldNotSendException()

        # Multiple alternative destinations (SLASH separated)
        splitup = string.split(destination,SLASH)

        if len(splitup) != 1:
            for portion in splitup:
                try:
                    self._send(portion)
                    return
                except:
                    pass
            # Oops,  looks like we can't send to
            # anyone.
            raise CouldNotSendException()

        # Now we are obviously only one portion.
        # Let's strip off the final destinations ports.

        splitup = string.split(destination,'!')
        firstdest = splitup[0]
        if len(splitup) != 1:
            forwarding = 1
            self.forward_to_destination = string.join(splitup[1:],'!')
        else:
            forwarding = 0

        # Is there a destination port?  BTW I'm wondering
        # whether the ability to specify the port number here
        # is a good idea or not.  You could use it to port
        # scan a network from a _long_ way away.
        # I think it's OK as long as we don't start sending
        # responses,  or allow arbitrary data to be sent there.
        # Maybe.
        # Anyway,  it's possible that someone is wanting to
        # contact an IPv6 node by address not name (e.g.
        # wanting to send something to 2:f:6:3::1:2:9).  If
        # this is the case,  the port number is specified by
        # 2:f:6:3::1:2:9-3155
        ipv6_address = 0

        splitup = string.split(firstdest,':')
        if len(splitup)>2:
            ipv6_address = 1
            spl2 = string.split(firstdest,'-')
            if len(spl2) == 1:
                portnum = default_send_port
            elif len(spl2) == 2:
                try:
                    portnum = string.atoi(spl2[1])
                except:
                    raise NonnumericPortException(portnum)
                firstdest = spl2[0]
            else:
                raise NonnumericPortException(string.join(spl[1:],'-'))
        elif len(splitup)==2:
            firstdest = splitup[0]
            portnum = splitup[1]
            try:
                portnum = string.atoi(portnum)
            except:
                raise NonnumericPortException(portnum)
        else:
            portnum = default_send_port

        # I should check here that the name resolves to an IPv4
        # address,  and if it doesn't,  to set ipv6_address.
        # Later,  (when I implement it) I should check whether or
        # not it is an IPX/SPX address.

        if ipv6_address:
            connection = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
        else:
            connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
        #try:
        connection.connect(firstdest,portnum)
        if forwarding == 1:
            connection.send(gnpcMessageHeaders.event_for_forwarding)
        else:
            connection.send(gnpcMessageHeaders.incoming_event)
        connection.send(self.marshall)
        #except:
        #raise CouldNotSendException()

        connection.close()

    def marshall(self):
        return pickle.dumps(self)

                
            
    
