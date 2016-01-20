#!/usr/bin/env python
import struct

ENDIANESS = {'LITTLE':'<','BIG':'>'}  #endianess struct format character mapping



class Record(object): 
    #Length = 0
    def __init__(self,packet=None,endianess='LITTLE'):
        self._packet = packet
        self._endianess = endianess
        self._fmt = None
    
    @property
    def _fullFmt(self):
        return "{0}{1}".format(ENDIANESS[self._endianess],self._fmt)

    def Pack(self):
        pass

    def Size(self):
        retVal = 0
        if self._fmt:
            retVal = struct.calcsize(self._fmt)
        return retVal

class CustomRecord(Record):
    def __init__(self,fmt,packet=None,endianess='LITTLE',valDecoder=None):
        super(CustomRecord,self).__init__(packet,endianess)
        self._fmt = fmt
        self._valDecoder = valDecoder
        if self._valDecoder:
            self.Value = self._valDecoder(struct.unpack_from(self._fullFmt,packet))
        else:
            self.Value = None

    def Pack(self):
        return struct.pack(self._fullFmt,self.Value)

    def __str__(self):
        return str(self.Value)

'''class definition for Pdu Status Record'''
class PduStatusRecord(Record):
    #Length = 1
    #@remark - see pduStatusRules.png to visualize _rules
    _rules = {'TEI':[1,31,32,41,67] + range(23,29), 'LVC':range(1,73),'CEI':range(1,72),
                     'FTI':[2],'DTI':[3],'RAI':[25,26,27],'IAI':[31,32],'ISM':[28],'AII':[28]}
    def __init__(self,pduType,packet=None,endianess='LITTLE'):
        Record.__init__(self,packet,endianess)
        self._fmt = 'B'
        if pduType < 1 or pduType > 255:
            raise ValueError
        self.PduType = pduType
        if not packet:
            self._value = 0
        else:
            self._value = struct.unpack_from(self._fullFmt,packet)[0]
    @property
    def TEI(self):  #transfered entity indicator - no difference:0,  difference:1
        return self._value & 0x01 if self.PduType in self._rules['TEI'] else None
    @property
    def LVC(self):  #LVC indicator - live:0, virtual:1, constructive:2
        return (self._value >> 1) & 0x03 if self.PduType in self._rules['LVC'] else None
    @property
    def CEI(self):  #coupled extension indicator - not coupled:0, coupled(1)
        return (self._value >> 3) & 0x01 if self.PduType in self._rules['CEI'] else None
    @property
    def FTI(self):  #fire type indicator - munition:0, expendable:1
        return (self._value >> 4) & 0x01 if self.PduType in self._rules['FTI'] else None
    @property
    def DTI(self):  #detonation type indicator - munition:0, expendable:1, non-munition:2
        return (self._value >> 5) & 0x03 if self.PduType in self._rules['DTI'] else None
    @property
    def RAI(self):  #radio attached indicator - no statement:0, unattached:1, attached:2
        return (self._value >> 5) & 0x03 if self.PduType in self._rules['RAI'] else None
    @property
    def IAI(self):  #intercom attached indicator - no statement:0, unattached:1, attached:2
        return (self._value >> 5) & 0x03 if self.PduType in self._rules['IAI'] else None
    @property
    def ISM(self):  #iff sim mode - regeneration:0, interactive:1
        return (self._value >> 4) & 0x01 if self.PduType in self._rules['ISM'] else None
    @property
    def AII(self):  #active interogation indicator - not active:0, active:1
        return (self._value >> 5) & 0x01 if self.PduType in self._rules['AII'] else None

    def Pack(self):
        return struct.pack(self._fullFmt,self._value)

    def __str__(self):
        return \
        "TEI: %r\n"\
        "LVC: %r\n"\
        "CEI: %r\n"\
        "FTI: %r\n"\
        "DTI: %r\n"\
        "RAI: %r\n"\
        "IAI: %r\n"\
        "ISM: %r\n"\
        "AII: %r" % (self.TEI, self.LVC, self.CEI, self.FTI, self.DTI, self.RAI, self.IAI, self.ISM, self.AII)

'''class definition for PDU Header Record class '''
class PduHeaderRecord(Record):
    protocolVersionRange = range(7)            #protocolVersion range is 0-6
    pduTypeRange = range(68) + range(129,136)  #pduType range is 0-67 & 129-135
    protocolFamilyRange = range(13) + [129]    #protocolFamily range is 0-12 & 129
    #Length = 12
    def __init__(self,packet=None,endianess='LITTLE'):
        Record.__init__(self,packet,endianess)
        self._fmt = 'BBBBIHBB'
        if not packet:
            self._pVersion,self._exId,self._pduType,self._pFam,self._tStamp,self._pduStat,self._totalLen = 0,0,0,0,0,0,0
        if packet:
            self.ProtocolVersion, self.ExerciseId,self.PduType,self.ProtocolFamily,self.Timestamp,self.TotalLength,self.PduStatus,self.Padding = \
                struct.unpack_from(self._fullFmt,packet)

    @property
    def ProtocolVersion(self):
        return self._pVersion
    @ProtocolVersion.setter
    def ProtocolVersion(self,value):
        if value not in self.protocolVersionRange:
            raise ValueError
        self._pVersion = value
    @property
    def ExerciseId(self):
        return self._exId
    @ExerciseId.setter
    def ExerciseId(self, value):
        self._exId = value
    @property
    def PduType(self):
        return self._pduType
    @PduType.setter
    def PduType(self,value):
        if value not in self.pduTypeRange:
            raise ValueError
        self._pduType = value
    @property
    def ProtocolFamily(self):
        return self._pFam
    @ProtocolFamily.setter
    def ProtocolFamily(self,value):
        if value not in self.protocolFamilyRange:
            raise ValueError
        self._pFam = value
    @property
    def Timestamp(self):
        return self._tStamp
    @Timestamp.setter
    def Timestamp(self,value):
        self._tStamp = value
    @property
    def TotalLength(self):
        return self._totalLen
    @TotalLength.setter
    def TotalLength(self,value):
        self._totalLen = value;
    @property
    def PduStatus(self):
        return PduStatusRecord(self.PduType,struct.pack('B',self._pduStat))
    @PduStatus.setter
    def PduStatus(self,value):
        self._pduStat = value

    def Pack(self):
            return struct.pack(self._fullFmt,self.ProtocolVersion,self.ExerciseId, \
                               self.PduType,self.ProtocolFamily,self.Timestamp,self.TotalLength,self._pduStat,self.Padding)
    def __str__(self):
        return \
        "ProtocolVersion: %r\n" \
        "ExerciseId: %r\n" \
        "PduType: %r\n" \
        "ProtocolFamily: %r\n" \
        "Timestamp: %r\n" \
        "TotalLength %r\n" \
        "PduStatus:\n  %s" % (self.ProtocolVersion,self.ExerciseId,self.PduType,self.ProtocolFamily,
                                self.Timestamp,self.TotalLength,'\n  '.join(str(self.PduStatus).splitlines()))

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
            self.VarParamRecs = CustomRecord('B')
            self.EntityType = EntityTypeRecord(endianess=endianess,entitymapper=entitymapper)
        else:
            self.PduHeader = PduHeaderRecord(packet,endianess)
            packet = packet[self.PduHeader.Size():]  #@remark - best way i could think of for shifting bytes in packet over
            self.EntityId = EntityIdRecord(packet,endianess)
            packet = packet[self.EntityId.Size():]
            self.ForceId = ForceIdRecord(packet)
            packet = packet[self.ForceId.Size():]
            self.VarParamRecs = CustomRecord('B',packet,endianess,lambda valLst : valLst[0])#  struct.unpack_from('B',packet)[0]
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


class SetDataPdu(object):
    def __init__(self,packet=None,endianess='LITTLE'):        
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
            