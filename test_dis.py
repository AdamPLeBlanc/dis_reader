#!/usr/bin/env python

import struct
import binascii
import pytest
from DIS.utils import *
from DIS.types import *


def TestFullPackAndUnpack():
    # buffer we will write to
    buffer = ''

    #Setup 96 bit/ 12 byte PDU header
    protocolVer = 5   #random protocol version   8-bits
    exId = 77         #random excercise id       8-bits
    pduType = 28      #random pdu type           8-bits
    protocolFam = 7   #random protocol family    8-bits
    timestamp = 77    #random timestamp          32-bits
    length = 12       #random length             16-bits
    pduStatus = 77    #random pdu status         8-bit
    padding = 0       #padding                   8-bit
    buffer += struct.pack('<BBBBIHBB',protocolVer,exId,pduType,protocolFam,timestamp,length,pduStatus,padding)

    #Setup 48 bit / 6 byte Entity Id
    siteNum = 77      #site number 16bit u-int
    appNum = 77       #application number 16bit u-int
    entityNum = 77    #entity number 16bit u-int
    buffer += struct.pack('<HHH',siteNum,appNum,entityNum)

    #setup 8bit/1byte force id record
    forceId = 7       #force ID  8-bit
    buffer += struct.pack('<B',forceId)

    #setup 8bit/1byte number of variable parameter record field
    varParams = 77     # 8-bits
    buffer += struct.pack('<B',varParams)

    #setup 64bit / 8byte entity type record
    kind = 2         # 8-bit
    domain = 7       # 8-bit
    country = 12      # 16-bit
    cat = 17          # 8-bit
    subCat = 22       # 8-bit
    spec = 27         # 8-bit
    extra = 32        # 8-bit
    buffer += struct.pack('<BBHBBBB',kind,domain,country,cat,subCat,spec,extra)

    entMapper = DisEntityMapper('EntityEnumerations.txt')
    ePdu = EntityStatePdu(packet=buffer,entitymapper=entMapper)
    
    print 'Testing Entity State Pdu Unpacking'

    assert ePdu.PduHeader.ProtocolVersion == protocolVer
    assert ePdu.PduHeader.ExerciseId == exId
    assert ePdu.PduHeader.PduType == pduType
    assert ePdu.PduHeader.ProtocolFamily == protocolFam
    assert ePdu.PduHeader.Timestamp == timestamp
    assert ePdu.PduHeader.TotalLength == length
    assert ePdu.PduHeader.PduStatus.Value == pduStatus
    assert ePdu.EntityId.SiteNum == siteNum
    assert ePdu.EntityId.AppNum == appNum
    assert ePdu.EntityId.EntityNum == entityNum
    assert ePdu.ForceId.Value == forceId
    assert ePdu.VarParamRecs == varParams
    assert ePdu.EntityType.Kind == kind
    assert ePdu.EntityType.Domain == domain
    assert ePdu.EntityType.Country == country
    assert ePdu.EntityType.Category == cat
    assert ePdu.EntityType.SubCat == subCat
    assert ePdu.EntityType.Specific == spec
    assert ePdu.EntityType.Extra == extra

    print 'Testing Entity State Pdu Packing'
    retBuffer = ePdu.Pack()
    assert buffer == retBuffer

    return ePdu


def TestPduHeaderRecord():
    #test protocolversion range
    tmp = PduHeaderRecord()
    failRange = [x for x in range(256) if x not in PduHeaderRecord.protocolVersionRange]
    print 'Testing PduHeader.ProtocolVersion for failure of %d values' % len(failRange)
    for i in failRange:
        with pytest.raises(ValueError):
            tmp.ProtocolVersion = i

    failRange = [x for x in range(256) if x not in PduHeaderRecord.pduTypeRange]
    print 'Testing PduHeader.PduType for failure of %d values' % len(failRange)
    for i in failRange:
        with pytest.raises(ValueError):
            tmp.PduType = i

    failRange = [x for x in range(256) if x not in PduHeaderRecord.protocolFamilyRange]
    print 'Testing PduHeader.ProtocolFamily for failure of %d values' % len(failRange)
    for i in failRange:
        with pytest.raises(ValueError):
            tmp.ProtocolFamily = i

def TestPduStatusRecord():
    packet = struct.pack('B',0xFF)
    print 'Testing PduStatusRecord to make sure it cant be initialized with zero as pdutype'
    with pytest.raises(ValueError):
        tmp = PduStatusRecord(0,packet)
    print 'Testing PduStatusRecord to make sure TEI,LVC,CEI,FTI,DTI,RAI,IAI,ISM,and AII\nvalues are correct for each pdutype'
    tmp = PduStatusRecord(1,packet)
    for k,v in PduStatusRecord._rules.items():
        for i in range(1,256):
            tmp.PduType = i
            val = getattr(tmp,k)
            if i in v:
                assert val

def TestLookupMapping():
    #setup table to match values in enumerations config file
    table = []
    for x in range(1,6):
        table.append([x + y*5 for y in range(0,7)])
    #setup mapper
    entMapper = DisEntityMapper('EntityEnumerations.txt')
    print 'Testing DisEntityMapper with %d values' % len(table)
    for vals in table:
        assert entMapper.GetEntityNames(vals)


if __name__ == '__main__':
    print
    print '*** Starting Tests ***'
    TestPduHeaderRecord()
    TestPduStatusRecord()
    TestLookupMapping()
    fullPdu = TestFullPackAndUnpack()
    print 'Test str override of Entity State PDU\n'
    print fullPdu

