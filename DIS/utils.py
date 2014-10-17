#!/usr/bin/env python

class DisEntityMapper(object):
    
    def __init__(self,mappingFileLocation):
        self.FullList = {}
        for line in open(mappingFileLocation,'r'):
            line = line.strip()
            if line and line[0] != '#':
                tmp = line.split()
                try:
                    self.FullList[tuple(tmp[:7])].append(tmp[-1])
                except:
                    self.FullList[tuple(tmp[:7])] = [tmp[-1]]

    def GetEntityNames(self,valueList):

        if len(valueList) != 7:
                raise Exception
        strList = tuple([str(x) for x in valueList]) #@remark - best way i could think of for making sure arguments are always strings
        return self.FullList[strList]
    


    #@remark - this was my first implementation, wonder if you think the way i finally did it is more efficient. i'll have to run some timing tests maybe
    '''

    def __init__(self,mappingFileLocation):
        self.FullList = []
        for line in open(mappingFileLocation,'r'):
            line = line.strip()
            if line and line[0] != '#':
                self.FullList.append(line.split())

    def GetEntityNames(self,valueList):

        if len(valueList) != 7:
                raise Exception
        strList = [str(x) for x in valueList] #@remark - best way i could think of for making sure arguments are always strings
        return [x[-1] for x in self.FullList if strList == x[:7]]
   '''
