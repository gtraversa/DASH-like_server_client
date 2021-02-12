"""
Basic server simulating media transmission similar to DASH.
Some parameters are provided for adjusting the maximum bandwidth,
the representations available for transmission, the size and length of media chunks,
and the rime between requests.  Developed in conjunction with a client script.


(C)2020 Gianluca Traversa, London, United Kingdom.

email gianlu.traversa@gmail.com

"""

import socket,os,sys,random,time
from _thread import *

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233

_clients = []
_frameSize = 2048
_initBandwith = 700
_totalBandwidth = 700

try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waiting for a Connection..')
ServerSocket.listen(5)


def threaded_client(connection,_address):
    """Create a client connection on a new thread for simple DASH simulation"""
    _timeCreated = time.time()
    _chunkLength = 3                                                            #Length of segment request in seconds
    _flgFirst = 1
    _maxClientBandwidth = 0
    global _totalBandwidth
    try:
        while True:
            _data = connection.recv(_frameSize)                                     #Initial conditions set by the client 
            if not _data:
                break
            _bandwidth,_req,_timer,_qualiReq,_segNum,_currentClient = data_parse(_data,_address)            #Return of initial conditions to pass to bandwidth limiter simulation
            if _flgFirst:                                                           #On fisrst connection with a client
                _currentClient['Bandwidth'] = _bandwidth
                _currentClient['Max Bandwidth']= _bandwidth
                _totalBandwidth = _totalBandwidth-_bandwidth                        #Allcoate desired bandwidth to client
                _flgFirst=0
                print('First connection for: ' +_address[0]+':'+str(_address[1]))
            if _totalBandwidth<0:                                                   #Requested bandwidth > available bandwidth
                bandwidth_sharing()
                _totalBandwidth = 0

            if _req:
                _chunkSize = chunk_quality(_qualiReq,_segNum)                       #If client is requesting data
                send_chunk(connection,_bandwidth=_currentClient['Bandwidth'],_bytesSent=_chunkSize,_timer=_timer,_chunkLength=_chunkLength)
                print('_________________________')
                print("Chunk sent to: "+ _address[0]+':'+str(_address[1]))
            elif not _req:                                                          #Client buffer is full, send 0 length segment to ACK conneciton
                send_chunk(connection,_bandwidth=_currentClient['Bandwidth'],_bytesSent=0,_timer=_timer,_chunkLength=0)
        conncection_closed(_currentClient)
        connection.close()
    except socket.error as e:
        conncection_closed(_currentClient)
        connection.close()
        print(str(e))

def data_parse(_data,_address):
    """Parse client setup data, updates client and returns setup variables"""
    _setup = _data.decode('utf-8').split(',')                                   #Data received as encoded CSV
    _currentClient = 0
    for client in _clients:
        if client['Port']==_address[1]:
            _currentClient = client                                             #Select current client based on port number
            break
    _bandwidth = int(_setup[0])
    _req = bool(int(_setup[1]))
    _currentClient['Request']=_req
    _timer = float(_setup[2])
    _currentClient['Timer']=_timer
    _qualiReq = str(_setup[3])
    _segNum = int(_setup[4])
    return  _bandwidth,_req,_timer,_qualiReq,_segNum,_currentClient

def send_chunk(connection,_bandwidth,_bytesSent,_timer,_chunkLength):
    """Simulation of limted bandwidth channel"""
    _sendTime = _bytesSent / _bandwidth                                         #Equivalent download time of chunk with given size (MBit) and bandwidth (MBit/s)
    time.sleep(max(_sendTime,_timer))                                           #Local transfer de layed by equivalent 'download' time OR minimum request time '_timer'
    reply = str(_chunkLength) + ',' + str(_bytesSent)                           #Length of chunk in seconds sent back to client
    connection.sendall(str.encode(reply))   

def save_client(_address):
    """Taskes connection information and stores as a dict in list of clients"""
    _clientDict = {}
    _address = str(_address).strip("()").replace("'","").split(', ')            #Some parsing to get IP and port  of client socket
    for info in _address:
        if info.__contains__("."):
            _clientDict['IP']=info
        else:
            _clientDict['Port']=int(info)
    _clientDict['Bandwidth'] = 0                                                #Default parameters for every client
    _clientDict['Request']= 1
    _clientDict['Timer']= 0
    _clients.append(_clientDict)
    print('Connected to: ' + _clientDict['IP'] + ':' + str(_clientDict['Port']))

def start_client(_client,_address):
    """Start new thread for new connection"""
    start_new_thread(threaded_client, (_client, _address))
    
def conncection_closed(_currentClient):
    """Eliminte client from list of clients when the connection is closed"""
    global _totalBandwidth
    print('Connection closed with: ' +_currentClient['IP']+':'+str(_currentClient['Port']))
    _totalBandwidth+= _currentClient['Bandwidth']                               #Free ALLOCATED bandwidth, not maximum given by client
    _clients.remove(_currentClient)
    bandwidth_sharing()                                                         #Reallocate increased bandwidth to other clients

def chunk_quality(_qualiReq,_segNum):
    """Find chunk size for desired quality and send it to the client, factor of 1.3 between quality sizes"""
    _chosenQuali=[]
    _240p = [50,100,150,200,50,100,150,200,50,100,150,200,-1]                                                    #Chunk sizes for each segment for each representation in MBit
    _480p=  [65,130,195,260,65,130,195,260,65,130,195,260,-1]
    _720p=  [84.5,169,253.5,338,84.5,169,253.5,338,84.5,169,253.5,338,-1]
    _1080p= [109.85,219.7,329.55,439.4,109.85,219.7,329.55,439.4,109.85,219.7,329.55,439.4,-1]
    _reprs = {'_240p': _240p,'_480p':_480p,'_720p':_720p,'_1080p':_1080p}
    _chosenQuali = _reprs[str(_qualiReq)]
    return _chosenQuali[_segNum]

def bandwidth_sharing(): 
    """Allocate bandwidth to clients proportionally"""
    global _initBandwith
    _totalBandwidthReq = 0
    for client in _clients:
        _totalBandwidthReq+= client['Max Bandwidth']                            #Find the total of the max bandwidth the clients request
    print('Total Requested Bandwidth: '+ str(_totalBandwidthReq))

    if not _totalBandwidthReq:                                                  #In case of no requests
        _totalBandwidthReq = _initBandwith
    _scaleFactor = _initBandwith/_totalBandwidthReq                             #Ratio of available to requested bandwidth
    for client in _clients:
        client['Bandwidth']=client['Max Bandwidth']*min(_scaleFactor,1)         #Scaling of each max bandwidth ans setting allocated bandwidth

def main():
    while True:
        _client, _address = ServerSocket.accept()
        save_client(_address)
        start_client(_client,_address)
    ServerSocket.close()

if __name__ == '__main__':
    main()
    
