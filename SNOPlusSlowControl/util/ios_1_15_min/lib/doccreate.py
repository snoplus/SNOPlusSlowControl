
#Useful for igrnoring "N/A" values
def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

#Finds the max, min and avg of the documents above and creates a new document to put them in
def createDoc(documents,latest_time,time_interval,ios):
    cardlist = []
    ios_doc = {}
    ios_doc["timestamp"] = latest_time + time_interval
    ios_doc["ios"] = ios
    if documents == []:
        pass
    else:
        for key in documents[0]:
            if key.startswith("card"):
                cardlist.append(key)
        for card in cardlist:                
            numchannels = len(documents[0][card]["voltages"])
            ios_doc[card] = {}
            max_volts = [-9000]*numchannels
            min_volts = [9000]*numchannels
            sum_volts = [0]*numchannels
            for doc in documents:
                try:
                    volts = doc[card]["voltages"]
                    for i in range(numchannels):
                        if isfloat(volts[i]):    
                            sum_volts[i] = sum_volts[i] + volts[i]
                            max_volts[i] = max(max_volts[i], volts[i])
                            min_volts[i] = min(min_volts[i], volts[i])
                except:
                    pass
            avg_volts = ["N/A"]*numchannels
            for i in range(numchannels):
                avg_volts[i] = sum_volts[i]/float(len(documents))
                if max_volts[i] == -9000:
                    max_volts[i] = "N/A"
                    min_volts[i] = "N/A"
                    avg_volts[i] = "N/A"
            ios_doc[card]["maximum"] = max_volts
            ios_doc[card]["minimum"] = min_volts
            ios_doc[card]["average"] = avg_volts
    return ios_doc

