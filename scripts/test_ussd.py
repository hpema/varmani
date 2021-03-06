# telnet program example
import datetime
import select
import socket
import sys
import threading
import time
import xml.etree.ElementTree as ET

import json
import requests
from frappeclient import FrappeClient

exitFlag = 0
accessDetails = open('/home/hemant/access.txt')
aD = json.loads(accessDetails.read())

# print aD
def logMe(msg):
	localtime = datetime.datetime.now().replace(microsecond=0)
	message = "[" + localtime.strftime("%Y-%m-%d %H:%M:%S") + "] " + msg + "\r\n"
	sys.stdout.write(message)
	sys.stdout.flush()

if __name__ == "__main__":
    client = FrappeClient(aD['url'], aD['username'], aD['password'])
    settingObj = client.get_api("varmani.getMTNServiceSettings")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)

    # connect to remote host
    try:
        s.connect((settingObj['ussd_server_socket_ip'],int(settingObj['ussd_server_socket_port'])))
    except Exception as e:
        #print(sys.exc_info()[0])
        logMe('Unable to connect: ' + str(e))
    # sys.exit()
    subsribe = "<usereq USERNAME='"+settingObj['ussd_username']+"' PASSWORD='"+settingObj['ussd_password']+"' VERBOSITY='0'><subscribe NODE='.*' TRANSFORM='USSD' PATTERN='.*'/></usereq>END"
    print (subsribe)
    s.send(subsribe)
    #"<usereq USERNAME='"+settingObj['ussd_username']+"' PASSWORD='"+settingObj['ussd_password']+"' VERBOSITY='0'><subscribe NODE='.*' TRANSFORM='USSD' PATTERN='\*130\*826'/></usereq>END"
    logMe('Connected to remote host. Start sending messages')
    ##prompt()

    while not exitFlag:
        # print "running...."

        socket_list = [s]
        #        time.sleep(30)
        #        break
        # Get the list sockets which are readable
        # print "Listerning"
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [], 1)
        # print "after stop"
        for sock in read_sockets:
            print ("incoming message from remote server")
            if sock == s:
                data = sock.recv(4096)
                print (data)
                if not data:
                    logMe('\nDisconnected from chat server')
                    time.sleep(100)
                    break
                # else:
                #     # print data
                try:
                    root = ET.fromstring(data)
                    for datablock in root.findall('datablock'):
                        lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
                        sessionid = datablock.find('sessionid').text
                        msisdn = datablock.find('msisdn').text
                        rootMsg = datablock.find('svcCode').text
                        requestMsg = datablock.find('message').text.replace('*130*826*', '').replace('#', '')
                        msgType = datablock.find('type').text
                        localtime = time.asctime(time.localtime(time.time()))
                        ranNow = datetime.datetime.now().replace(microsecond=0)
                        saveTime = "timeRec=" + ranNow.strftime("%Y-%m-%d %H:%M:%S")
                        logMe(localtime + " | " + sessionid + " | " + msisdn + " | " + rootMsg + " | " + requestMsg + " | " + msgType + " | " + saveTime)


                        lastTimeCheck = datetime.datetime.now().replace(microsecond=0)

                        responseMeg = "<usareq NODE='" + settingObj['ussd_node'] + "' TRANSFORM='USSD' USERNAME='" + \
                                      settingObj['ussd_username'] + "' PASSWORD='" + settingObj[
                                          'ussd_password'] + "' VERBOSITY='2'><command><ussd_response><sessionid>" + sessionid + "</sessionid><type>" + msgType + "</type><msisdn>" + msisdn + "</msisdn><message>" + requestMsg + "</message></ussd_response></command></usareq>"
                        print (responseMeg)
                        print (settingObj['message_url'])
                        r = requests.post(settingObj['message_url'], data={'command': responseMeg})
                        print (r)
                except:
                    pass
            # user entered a message
            else:
                msg = sys.stdin.readline()
            # prompt()

logMe("Exiting Main Thread")
