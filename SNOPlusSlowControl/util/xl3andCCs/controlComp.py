import httplib, time, json, sys, getopt

def processArgs(argv):
        chn = -1
        try:
                opts, args = getopt.getopt(argv,"hsrpn:",["num="])
        except getopt.GetoptError:
                print 'type \"test.py -h\" for correct usage'
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h':
                        print 'test.py -n \# to get Temp and Voltage status of XL3 #'
                        sys.exit()
                elif opt in ("-n","--num"):
                        chn = arg
        return chn


def getStatus(chn):
        conn = httplib.HTTPConnection("localhost",8000,timeout=2)
	card = "D"
	if (chn>9):
		card = "A"
		chn = chn-10
        conn.request("GET","/data/card"+card)
        result = conn.getresponse()
        data = json.loads(result.read())
        conn.close()
        return data["card"+card]["channel"+str(chn*2+1)]["voltage"], data["card"+card]["channel"+str(chn*2+2)]["voltage"]


chn = processArgs(sys.argv[1:])
print getStatus(int(chn))

#for i in range(10):
#       reset(i)
#       print i
#       print getStatus()
#       print "on"
#       setChannel(i,1)
#       print getStatus()
#       time.sleep(1)
#       setChannel(i,0)
#       print getStatus()
#       print "off"
#       time.sleep(1)
#       print

