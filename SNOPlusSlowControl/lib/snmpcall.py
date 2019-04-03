from pysnmp.entity.rfc3413.oneliner import cmdgen

class SNMPConnector(object):
    ''''Class that allows for connecting to a server with
    an SNMP protocol and pulling oneliners of data.  snmpget
    function modeled after an example on jcutrer.com'''
    def __init__(self,host, port, community):
        self.host = host
        self.port = port
        self.community = community


    def setHost(self,host):
        self.host = host

    def setPort(self,port):
        self.port = port

    def setCommunity(self,community):
        self.community = community

    def snmpget(self,oid):
        ''' One liner for grabbing data from the given OID for
        the currently connected SNMP interface''' 
       
        cmdGen = cmdgen.CommandGenerator()
       
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            cmdgen.CommunityData(self.community),
            cmdgen.UdpTransportTarget((self.host,self.port)),
            oid
        )
        print("GOT COMMAND") 
        # Check for errors and print out results
        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s'%( errorStatus.prettyPrint(),\
                    errorIndex and varBinds[int(errorIndex)-1] or '?'))
            else:
                for name, val in varBinds:
                    print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
                    return val
