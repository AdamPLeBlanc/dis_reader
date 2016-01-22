#!/usr/bin/env python

import struct
import binascii
import unittest
from DIS.utils import *
from DIS.setdatapdu import *


class DisPacketTest(unittest.TestCase):

    def testFullPackAndUnpack(self):
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
        origSiteNum = 77      #site number 16bit u-int
        origAppNum = 77       #application number 16bit u-int
        origRefNum = 77    #entity number 16bit u-int
        buffer += struct.pack('<HHH',origSiteNum,origAppNum,origRefNum)

        #setup 48 bit /6 byte Receiving ID
        recvSiteNum = 88
        recvAppNum = 88
        recvRefNum = 88
        buffer += struct.pack('<HHH',recvSiteNum,recvAppNum,recvRefNum)

        #setup 32 bit / 4 byte Request ID
        requestId = 77
        buffer += struct.pack('<I',requestId)

        #add 32 bit / 4 byte padding
        buffer += struct.pack('<I',0)

        #add 32 bit / 4 byte fixed datum number
        fixedDatNum = 2
        buffer += struct.pack('<I',fixedDatNum)

        #add 32 bit / 4 byte variable datum number
        varDatNum = 2
        buffer += struct.pack('<I',varDatNum)

        #create 64 bit / 8 byte fixed datum and add it twice to buffer
        fixDatId = 77
        fixDatVal = 'A' * 4
        buffer += struct.pack('<I4s',fixDatId,fixDatVal) * 2

        #create 96 bit / 12 byte variable datum and add it twice to buffer
        varDatId = 88
        varDatLen = 7
        varDatVal = 'B' * varDatLen
        buffer += (struct.pack('<II7ss',varDatId,varDatLen,varDatVal,'\x00') * 2)


        sdPdu = SetDataPdu(buffer)
    
        print 'Testing SetData Pdu Unpacking'

        self.assertEqual(sdPdu.PduHeader.ProtocolVersion,protocolVer)
        self.assertEqual(sdPdu.PduHeader.ExerciseId,exId)
        self.assertEqual(sdPdu.PduHeader.PduType,pduType)
        self.assertEqual(sdPdu.PduHeader.ProtocolFamily,protocolFam)
        self.assertEqual(sdPdu.PduHeader.Timestamp,timestamp)
        self.assertEqual(sdPdu.PduHeader.TotalLength,length)
        self.assertEqual(sdPdu.PduHeader.PduStatus._value,pduStatus)
        self.assertEqual(sdPdu.OrigId.SiteNum,origSiteNum)
        self.assertEqual(sdPdu.OrigId.AppNum,origAppNum)
        self.assertEqual(sdPdu.OrigId.RefNum,origRefNum)
        self.assertEqual(sdPdu.RecvId.SiteNum,recvSiteNum)
        self.assertEqual(sdPdu.RecvId.AppNum,recvAppNum)
        self.assertEqual(sdPdu.RecvId.RefNum,recvRefNum)
        self.assertEqual(sdPdu.RequestId,requestId)
        self.assertEqual(sdPdu.FixedDatumCount,fixedDatNum)
        self.assertEqual(sdPdu.VarDatumCount,varDatNum)
        self.assertEqual(sdPdu.FixedDatums[0].Id,fixDatId)
        self.assertEqual(sdPdu.FixedDatums[0].Value,fixDatVal)
        self.assertEqual(sdPdu.FixedDatums[1].Id,fixDatId)
        self.assertEqual(sdPdu.FixedDatums[1].Value,fixDatVal)
        self.assertEqual(sdPdu.VarDatums[0].Id,varDatId)
        self.assertEqual(sdPdu.VarDatums[0].Length,varDatLen)
        self.assertEqual(sdPdu.VarDatums[0].Value,varDatVal)
        self.assertEqual(sdPdu.VarDatums[1].Id,varDatId)
        self.assertEqual(sdPdu.VarDatums[1].Length,varDatLen)
        self.assertEqual(sdPdu.VarDatums[1].Value,varDatVal)        

        print 'Testing Entity State Pdu Packing'
        retBuffer = sdPdu.Pack()
        self.assertEqual(buffer,retBuffer)

        print sdPdu


    

if __name__ == '__main__':
    print
    print '*** Starting Tests ***'
    unittest.main()

