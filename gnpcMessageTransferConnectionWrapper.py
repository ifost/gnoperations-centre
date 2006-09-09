import gnpcScheduler
import gnpcActivity
import gnpcEncoding
import string
import binascii
import pickle

try:
    import zlib
    have_zlib = 1
except ImportError:
    gnpcActivity.record(gnpcActivity.WARNING,"Couldn't find zlib module -- proceeding anyway,  hoping that no-one sends compressed data")
    have_zlib = 0

class gnpcMessageTransferConnectionWrapper(gnpcScheduler.gnpcFileDescriptorWrapper):
    def __init__(self,conn,addr):
        gnpcScheduler.gnpcFileDescriptorWrapper(conn)
        self.data_so_far = ''
        self.halfway_through_line = 0
        self.last_line_fraction = None
        self.conn = conn
        self.addr = addr
        self.is_compressed = 0
        
    def handle_line(self,line):
        data = string.split(line,':',2)
        if len(data) != 2:
            gnpcActivity.record(gnpcActivity.ERROR,'Dropping connection from address because of incorrectly formatted line:  '+ line)
            self.error_action()
        left_data = string.strip(string.upper(data[0]))
        right_data = string.strip(data[1])
        if left_data not in gnpcEncoding.LeftSets:
            gnpcActivity.record(gnpcActivity.ERROR,'Dropping connection from address because of incorrectly formatted line:  '+ line)
            self.error_action()

        ########################################
        # At this point I would like to say that this protocol is a
        # shameful mess,  and that I should structure this code
        # a little better to handle it.  This rather strange re-entrant
        # structure was the easiest kludge I could come up with.
        ########################################
        
        # OK,  so we know it's a valid line.  Let's do something with it
        if left_data == gnpcEncoding.Data:
            try:
                decoded = binascii.a2b_base64(right_data)
                if self.is_compressed == 1:
                    decoded = zlib.decompress(decoded)
            except:
                gnpcActivity.record(gnpcActivity.ERROR,'Incorrect data in line: '+line)
                self.error_action()
            # This next could be a big performance hit -- for a big message
            # will I be doing vast amounts of copying here?
            self.data_so_far = self.data_so_far + decoded
            return

            
        elif left_data == gnpcEncoding.Connection_Control:
            self.data_so_far = ''
            if right_data == gnpcEncoding.CompressedMessage:
                if have_zlib == 0:
                    # Oh flip.  They requested compression,  and
                    # we don't have it.
                    gnpcActivity.record(gnpcActivity.NOTICE,"Remote connection tried to request compression which I was unable to provide.")
                    self.conn.send(gnpcEncoding.CompressionNope)
                    return
                else:
                    self.conn.send(gnpcEncoding.CompressionOK)
                    self.is_compressed = 1
                    return
            elif right_data == gnpcEncoding.UncompressedMessage:
                self.is_compressed = 0
                return

            elif right_data = gnpcEncoding.EndData:
                try:
                    object = pickle.loads(self.data_so_far)
                except:
                    gnpcActivity.record(gnpcActivity.WARNING,"Could not unpickle message sent")
                    self.conn.send(gnpcEncoding.MessageNope)
                    self.error_action()
                    return
                self.conn.send(gnpcEncoding.MessageOK)
                # Now I can close the connection happily.
                self.close()
                # But what do I do with object?????
                object.method_invoke()
                
            else:
                gnpcActivity.record(gnpcActivity.ERROR,"Incomprehensible connection control message")
                
        
    def read_action(self):
        new_data = self.conn.recv(1024)
        if new_data == '':
            self.error_action()
            return
        splitup = string.split(new_data,'\n')
        if self.halfway_through_line == 1:
            this_one = self.last_line_fraction + splitup[0]
            if len(splitup)!=0:
                splitup = splitup[1:]
                self.handle_line(this_one)
            else:
                self.last_line_fraction = this_one
                return
        
        if new_data[-1] != '\n':
            self.halfway_through_line = 1
            self.last_line_fraction = splitup[-1]
            splitup = splitup[:-1]
        else:
            self.halfway_through_line = 0
            self.last_line_fraction = ''

        for line in splitup:
            self.handle_line(line)
        return
    
        
        
