import struct

from pdubase import *

'''class definition for Entity Id Record'''
class IdRecord(Record):
    def __init__(self,packet=None,endianess='LITTLE'):
        super(IdRecord,self).__init__(packet,endianess)
        self._fmt = 'HHH'
        if not packet:
            self.SiteNum, self.AppNum, self.RefNum = 0,0,0
        else:
            self.SiteNum,self.AppNum,self.RefNum = struct.unpack_from(self._getFullFmt(),packet)

    def Pack(self):
        return struct.pack(self._getFullFmt(),self.SiteNum,self.AppNum,self.RefNum)

    def __str__(self):
        return\
        "SiteNum: %r\n" \
        "AppNum: %r\n" \
        "RefNum: %r" % (self.SiteNum,self.AppNum,self.RefNum)

class FixedDatumRecord(Record):
    def __init__(self,packet=None,endianess='LITTLE'):
        super(FixedDatumRecord,self).__init__(packet,endianess)
        self._fmt = 'I4s'
        if not packet:
            self.Id, self.Value, = 0,""
        else:
            self.Id,self.Value = struct.unpack_from(self._getFullFmt(),packet)

    def Pack(self):
        return struct.pack(self._getFullFmt(),self.Id,self.Value)

    def __str__(self):
        return\
        "ID: {0}\n" \
        "Value: {1}".format(self.Id,self.Value)

class VariableDatumRecord(Record):
    def __init__(self,packet=None,endianess='LITTLE'):
        super(VariableDatumRecord,self).__init__(packet,endianess)
        if not packet:
            self.Id,self.Length,self.Value = 0,0,""
        else:
            self.Id,self.Length = struct.unpack_from(self._getFullFmt("II"),packet)
            self.Value = struct.unpack_from(self._getFullFmt("{0}s".format(self.Length)),packet,8)[0]
        self._generateFmt()

    def Pack(self):
        return struct.pack(self._getFullFmt(),self.Id,self.Length,self.Value,'\x00'*self._getBufferLength())

    def _getBufferLength(self):
        return 8-(self.Length%8)

    def _generateFmt(self):
        self._fmt = "II{0}s{1}s".format(self.Length,self._getBufferLength())

    def __str__(self):
        return\
        "ID: {0}\n" \
        "Length: {1}\n" \
        "Value: {2}".format(self.Id,self.Length,self.Value)

class SetDataPdu(Record):
    def __init__(self,packet=None,endianess='LITTLE'):
        super(SetDataPdu,self).__init__(packet,endianess)        
        if not packet:
            self.PduHeader = PduHeaderRecord(endianess=endianess)
            self.OrigId = IdRecord(endianess=endianess)
            self.RecvId = IdRecord(endianess=endianess)
            self.RequestId = 0
            self.FixedDatumCount = 0
            self.VarDatumCount = 0
            self.FixedDatums = []
            self.VarDatums = []
        else:
            self.PduHeader = PduHeaderRecord(packet,endianess)
            packet = packet[self.PduHeader.Size():]  #@remark - best way i could think of for shifting bytes in packet over
            self.OrigId = IdRecord(packet,endianess)
            packet = packet[self.OrigId.Size():]
            self.RecvId = IdRecord(packet,endianess)
            packet = packet[self.RecvId.Size():]
            self.RequestId = struct.unpack_from(self._getFullFmt("I"),packet)[0]
            packet = packet[8:] #includes 4 byte padding
            self.FixedDatumCount = struct.unpack_from(self._getFullFmt("I"),packet)[0]
            packet = packet[4:]
            self.VarDatumCount = struct.unpack_from(self._getFullFmt("I"),packet)[0]
            packet = packet[4:]
            self.FixedDatums = []
            #import pdb;pdb.set_trace()
            for cntr in xrange(self.FixedDatumCount):
                tmpFixDatum = FixedDatumRecord(packet,endianess)
                self.FixedDatums.append(tmpFixDatum)
                packet = packet[tmpFixDatum.Size():]
            self.VarDatums = []
            for cntr in xrange(self.VarDatumCount):   
                tmpVarDatum = VariableDatumRecord(packet,endianess)
                self.VarDatums.append(tmpVarDatum)
                packet = packet[tmpVarDatum.Size():]


    def Pack(self):
        retVal = ''.join([rec.Pack() for rec in [self.PduHeader,self.OrigId,self.RecvId]])
        retVal += struct.pack(self._getFullFmt("IIII"),self.RequestId,0,self.FixedDatumCount,self.VarDatumCount)
        retVal += ''.join([rec.Pack() for rec in self.FixedDatums + self.VarDatums])
        return retVal
    
    def __str__(self):
        baseStr = \
        "PDU Header:\n  %s\n"\
        "Orig ID:\n  %s\n"\
        "Recv ID: %s\n"\
        "Request ID: %s\n"\
        "Fixed Datum Count: %s\n" % ('\n  '.join(str(self.PduHeader).splitlines()),
                                '\n  '.join(str(self.OrigId).splitlines()), 
                                '\n  '.join(str(self.RecvId).splitlines()), 
                                self.FixedDatumCount,self.VarDatumCount)
        fixStr = ""
        for cntr,fixDatum in enumerate(self.FixedDatums):
            fixStr += \
                "Fixed Datum {0}:\n  {1}\n".format(cntr,'\n  '.join(str(fixDatum).splitlines()))
        varStr = ""
        for cntr,varDatum in enumerate(self.VarDatums):
            varStr += \
                "Variable Datum {0}:\n  {1}\n".format(cntr,'\n  '.join(str(varDatum).splitlines()))

        return baseStr + fixStr + varStr


            
