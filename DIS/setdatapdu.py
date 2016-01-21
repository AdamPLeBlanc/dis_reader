import struct

from pdubase import *

class IdRecord(Recordd):
    def __init__(self,packet=None,endianess='LITTLE'):
        super(IdRecord,self).__init__(packet,endianess)
        self._fmt = ""

class SetDataPdu(Record):
    def __init__(self,packet=None,endianess='LITTLE'):
        super(SetDataPdu,self).__init__(packet,endianess)        
        if not packet:
            self.PduHeader = PduHeaderRecord(endianess=endianess)
            self.EntityId = EntityIdRecord(endianess=endianess)
            self.ForceId = ForceIdRecord()
            self.VarParamRecs = 0
            self.EntityType = EntityTypeRecord(endianess=endianess,entitymapper=entitymapper)
        else:
            self.PduHeader = PduHeaderRecord(packet,endianess)
            packet = packet[self.PduHeader.Size():]  #@remark - best way i could think of for shifting bytes in packet over
            self.EntityId = EntityIdRecord(packet,endianess)
            packet = packet[self.EntityId.Size():]
            self.ForceId = ForceIdRecord(packet)
            packet = packet[self.ForceId.Size():]
            self.VarParamRecs = struct.unpack_from('B',packet)[0]
            packet = packet[1:]
            self.EntityType = EntityTypeRecord(packet,endianess,entitymapper)

    def Pack(self):
        return self.PduHeader.Pack() + self.EntityId.Pack() + self.ForceId.Pack() \
            + self.VarParamRecs.Pack() + self.EntityType.Pack()
    
    def __str__(self):
        return\
        "PDU Header:\n  %s\n"\
        "Entity ID:\n  %s\n"\
        "Force ID: %s\n"\
        "Variable Parameter Records: %s\n"\
        "Entity Type:\n  %s" % ('\n  '.join(str(self.PduHeader).splitlines()),
                                '\n  '.join(str(self.EntityId).splitlines()), self.ForceId, self.VarParamRecs,
                                '\n  '.join(str(self.EntityType).splitlines()))
            
