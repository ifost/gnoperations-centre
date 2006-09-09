# This module has one function:
#   forwardMessageToMsgd(destination,event)
#
# The event should be anything pickle-able.  The destination
# should be a string,  but it can be quite complicated.
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

import socket
import string
import os
import time
import pickle
import gnpcMessageHeaders

default_send_port = 5329

my_hostname = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))[0]

class CouldNotSendException:
    pass

class NonnumericPortException:
    def __init__(self,pstr):
        self.pstr = pstr


def forwardMessageToMsgd(event,destination=None):
    if destination is None:
        destination = event['GNPC_DEST']
    successfully_sent = 0
    splitup = string.split(destination,',')
    if len(splitup) != 1:
        # so that a redundant system can work out which are
        # duplicate messages,  and which aren't,  we'll attach
        # our own blob to the Event, uniquely identifying it
        # as ours.
        #
        # You can do cute things with this like:
        #   GNPC_DEST="fronthost1!backhost,fronthost2!backhost"
        # Then (a) backhost can correlate duplicates based on the
        # dmik of the message,  and (b) you can be pretty sure they
        # are going to get there!
        my_pid = os.getpid()
        timenow = time.time()
        unique_detail = my_hostname + '-' + `my_pid` + '-' + `timenow()`
        dmik = 'DUPLICATE_MESSAGE_IDENTIFIER_KEY'
        if event.has_key(dmik):
            event[dmik] = event[dmik] + '&' + unique_detail
        else:
            event[dmik] = unique_detail

        any_successful = 0
        for portion in splitup:
            try:
                forwardMessageToMsgd(event,portion)
                any_successful = 1
            except CouldNotSendException:
                pass
        if any_successful:
            return
        raise CouldNotSendException()

    # Now let's try alternatives
    splitup = string.split(destination,'/')

    if len(splitup) != 1:
        for portion in splitup:
            try:
                forwardMessageToMsgd(event,portion)
                return
            except:
                pass
        # Oops,  looks like we can't send to
        # anyone.
        raise CouldNotSendException()

    # Now we are obviously only one portion.
    # Let's strip off some the final destinations ports.

    splitup = string.split(destination,'!')
    firstdest = splitup[0]
    if len(splitup) != 1:
        forwarding = 1
        event['GNPC_DEST'] = string.join(splitup[1:],'!')
    else:
        forwarding = 0

    # Is there a destination port?  BTW I'm wondering
    # whether the ability to specify the port number here
    # is a good idea or not.  You could use it to port
    # scan a network from a _long_ way away.
    # I think it's OK as long as we don't start sending
    # responses,  or allow arbitrary data to be sent there.
    # Maybe.

    splitup = string.split(firstdest,':')
    if len(splitup)==2:
        firstdest = splitup[0]
        portnum = splitup[1]
        try:
            portnum = string.atoi(portnum)
        except:
            raise NonnumericPortException(portnum)
    else:
        portnum = default_send_port

    connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    #try:
    connection.connect(firstdest,portnum)
    if forwarding == 1:
        connection.send(gnpcMessageHeaders.event_for_forwarding)
    else:
        connection.send(gnpcMessageHeaders.incoming_event)
    connection.send(pickle.dumps(event))
    #except:
    #raise CouldNotSendException()

    connection.close()

    
    
