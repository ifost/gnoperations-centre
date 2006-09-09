### This class is not used???



class gnpcConnectionRegister:
    """There should only be one of these objects for any given
    process."""
    def __init__(self):
        self.connections = []
        # Holding everything as a list is not terribly efficient,
        # but we are unlikely to have more than a handful of
        # connections open at any time.
    def new_connection_accepted(self,connection,address):
        connection_name = socket.gethostbyaddr(address)
        filenum = connection.fileno()
        self.connections.append(connection_name,filenum,connection,address)
    def filenums(self):
        result  = []
        for (name,fnum,conn,addr) in self.connections:
            result.append(fnum)
        return result
    def connection_closed(self,connection):
        index = -1
        if type(connection) == type(0):
            for i in range(len(self.connections)):
                (name,fnum,conn,addr) = self.connections[i]
                if fnum == connection:
                    index = i
                    break
        else:
            for i in range(len(self.connections)):
                (name,fnum,conn,addr) = self.connections[i]
                if conn == connection:
                    index = i
                    break
        if index == -1:
            raise 'Unknown connection',connection
        if index == 0:
            self.connections = self.connections[1:]
        elif index == len(self.connections):
            self.connections = self.connections[:-1]
        else:
            self.connections = self.connections[:index] + self.connections[index+1:]
    def give_me_a_connection(self,hostname):
        for i in range(len(self.connections)):
            (name,fnum,conn,addr) = self.connections[i]
            if name == hostname:
                return conn
        # OK,  need to make a new one
        
        
