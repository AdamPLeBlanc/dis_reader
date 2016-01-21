import struct
from pdubase import *


'''class definition for Force Identification Record'''
class ForceIdRecord(Record):
    #Length = 1

    def __init__(self,packet=None,endianess='LITTLE'):
        Record.__init__(self,packet)
        self._fmt = 'B'
        if not packet:
            self.Value = 0
        else:
            self.Value = struct.unpack_from(self._fullFmt,packet)[0]
        if self.Value < 0 or self.Value > 30:
            raise ValueError

    def Pack(self):
        return struct.pack(self._fullFmt,self.Value)

    def __str__(self):
        return 'Value: %r' % self.Value
    
'''class definition for Force Identification Record'''
class VariableParameters(Record):
    #Length = 1

    def __init__(self,packet=None,endianess='LITTLE'):
        Record.__init__(self,packet)
        self._fmt = 'B'
        if not packet:
            self.Value = 0
        else:
            self.Value = struct.unpack_from(self._fullFmt,packet)[0]

    def Pack(self):
        return struct.pack(self._fullFmt,self.Value)

    def __str__(self):
        return 'Value: %r' % self.Value    

'''class definition for Entity Id Record'''
class EntityIdRecord(Record):
    #Length = 6

    def __init__(self,packet=None,endianess='LITTLE'):
        Record.__init__(self,packet,endianess)
        self._fmt = 'HHH'
        if not packet:
            self.SiteNum, self.AppNum, self.EntityNum = 0,0,0
        else:
            self.SiteNum,self.AppNum,self.EntityNum = struct.unpack_from(self._fullFmt,packet)

    def Pack(self):
        return struct.pack(self._fullFmt,self.SiteNum,self.AppNum,self.EntityNum)

    def __str__(self):
        return\
        "SiteNum: %r\n" \
        "AppNum: %r\n" \
        "EntityNum: %r" % (self.SiteNum,self.AppNum,self.EntityNum)

'''class definition for Entity Type Record'''
class EntityTypeRecord(Record): 
    #Length = 8
    _entitymapper = None
    def __init__(self,packet=None,endianess='LITTLE',entitymapper=None):
        Record.__init__(self,packet,endianess)
        if not self._entitymapper:
            EntityTypeRecord._entitymapper = entitymapper  #@remark - Is it ok to set class variable this way?.. i guess i could use class method
        self._fmt = 'BBHBBBB'
        if not packet:
            self.Kind,self.Domain,self.Country,self.Category,self.SubCat,self.Specific,self.Extra = 0,0,0,0,0,0,0
            self.SimNames = None
        else:
            self.Kind,self.Domain,self.Country,self.Category,self.SubCat,self.Specific,self.Extra = \
                struct.unpack_from(self._fullFmt,packet)
            self.SimNames = None if not self._entitymapper else self._entitymapper.GetEntityNames([self.Kind,self.Domain,self.Country,self.Category,self.SubCat,self.Specific,self.Extra])

    def Pack(self):
        return struct.pack(self._fullFmt,self.Kind,self.Domain,self.Country,self.Category,self.SubCat,self.Specific,self.Extra)

    def __str__(self):
        return \
        "Sim Names: %r\n" \
        "Kind: %r\n" \
        "Domain: %r\n" \
        "Country: %r\n" \
        "Category: %r\n" \
        "SubCat: %r\n" \
        "Specific: %r\n" \
        "Extra: %r" % (None if not self.SimNames else self.SimNames,self.Kind,self.Domain,self.Country,self.Category,self.SubCat,self.Specific,self.Extra)

'''class definition for Entity State PDU'''
class EntityStatePdu(Record):
    _entitymapper = None
    def __init__(self,packet=None,endianess='LITTLE',entitymapper=None):
        super(EntityStatePdu,self).__init__(packet,endianess)
        if not self._entitymapper:
            EntityStatePdu._entitymapper = entitymapper
        if not packet:
            self.PduHeader = PduHeaderRecord(endianess=endianess)
            self.EntityId = EntityIdRecord(endianess=endianess)
            self.ForceId = ForceIdRecord()
            self.VarParamRecs = VariableParameters(endianess=endianess)
            self.EntityType = EntityTypeRecord(endianess=endianess,entitymapper=entitymapper)
        else:
            self.PduHeader = PduHeaderRecord(packet,endianess)
            packet = packet[self.PduHeader.Size():]  #@remark - best way i could think of for shifting bytes in packet over
            self.EntityId = EntityIdRecord(packet,endianess)
            packet = packet[self.EntityId.Size():]
            self.ForceId = ForceIdRecord(packet)
            packet = packet[self.ForceId.Size():]
            self.VarParamRecs = VariableParameters(packet,endianess)
            packet = packet[1:]
            self.EntityType = EntityTypeRecord(packet,endianess,entitymapper)

        self._fmt = ''.join([r._fmt for r in [self.PduHeader,self.EntityId,self.ForceId,self.VarParamRecs,self.EntityType]])

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