from __future__ import print_function
import TimestampComparer as ts

def getCavityTempsDocAge(LatestEntry):
    comparer = ts.TimestampComparer(LatestEntry)
    return comparer.compare()
def getIOSDocAge(IOSnum,LatestEntry):
    comparer = ts.TimestampComparer(LatestEntry)
    return comparer.compare()

def getDeltaVDocAge(LatestEntry):
    #poll the DeltaV database and check the   timestamp
    dvcomparer = ts.TimestampComparer(LatestEntry)
    return dvcomparer.compare()

