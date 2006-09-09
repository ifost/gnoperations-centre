######################################################################
# Everything that gets transferred across the network has to
# be of the form
#  LeftData:  RightData
#

######################################################################
# Some LeftData...
Connection_Control = 'Connection-Control'
Data = 'Data'
CompressionAcknowledge = 'CompressionAcknowledge'
MessageAcknowledge = 'MessageAcknowledge'

# The following things make sense to appear at the beginning of a line
LeftSets =[Connection_Control,
           # which may have RightData of
           #   - Ping???    (which is requesting a response, maybe?)
           #   - CompressedMessage
           #   - UncompressedMessage
           #   - ProxyTelnetSetup ????
           #   - Something about registering interest in seeing Messages???
           #   - EndData    
           Data,
           # which will have RightData of a line of Base64 encoded
           # text; it follows on from a CompressedMessage or
           # UncompressedMessage & NumberOfDataLines
           CompressionAcknowledge,
           # The thing to send _back_ when a CompressedMessage is
           # requested
           MessageAcknowledge
           # The thing to send back after EndData is received.
           ]


######################################################################
# Some RightData
Compressed_Message = 'CompressedMessage'
Uncompressed_Message = 'UncompressedMessage'
End_Data = 'EndData'
Can_Do_Compression = 'CanDoCompression'
No_Can_Do_Compression = "NoCanDoCompression"
Message_Understood = 'MessageUnderstood'
Message_Garbled = 'MessageGarbled'

######################################################################
# Some Combinations...
CompressionOK = CompressionAcknowledge + ': ' + Can_Do_Compression + '\n'
CompressionNope = CompressionAcknowledge + ': ' + No_Can_Do_Compression + '\n'
MessageOK = MessageAcknowledge + ': ' + Message_Understood + '\n'
MessageNope = MessageAcknowledge + ': ' + Message_Garbled + '\n'
