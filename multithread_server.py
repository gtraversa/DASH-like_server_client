"""
Basic server simulating DASH for algorithm development.
Very simple first implementation with little adjustment serving as a starting point.

(C)2020 Gianluca Traversa, London, United Kingdom.

email gianlu.traversa@gmail.com

"""

import socket,os,sys,random,time
from _thread import *

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233

_threadCount = 0
_clients = []
_frameSize = 2048
_setup = []
_totalBandwidth=0

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
    while True:
        _data = connection.recv(_frameSize)                                     #Initial conditions set by the client 
        if not _data:
            break
        _bandwidth,_req,_timer,_qualiReq,_segNum,_currentClient = data_parse(_data,_address)            #Return of initial conditions to pass to bandwidth limiter simulation
        if _req:
            _chunkSize = chunk_quality(_qualiReq,_segNum)                       #If client is requesting data
            send_chunk(connection,_bandwidth,_bytesSent=_chunkSize,_timer=_timer,_chunkLength=_chunkLength)
            print("Message sent to: "+ _address[0]+':'+str(_address[1]))
        elif not _req:                                                          #Client buffer is full, send 0 length segment to ACK conneciton
            send_chunk(connection,_bandwidth,_bytesSent=0,_timer=_timer,_chunkLength=0)
    conncection_closed(_currentClient)
    print(_clients)
    connection.close()

def data_parse(_data,_address):
    """Receives encoded setup data, decodes it and separated the varaibles"""
    _setup = _data.decode('utf-8').split(',')                                   #Data received as encoded CSV
    _currentClient = 0
    for client in _clients:
        if client['Port']==_address[1]:
            _currentClient = client
            break
    _bandwidth = int(_setup[0])
    _currentClient['Bandwidth'] = _bandwidth
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
    _address = str(_address).strip("()").replace("'","").split(', ')
    for info in _address:
        if info.__contains__("."):
            _clientDict['IP']=info
        else:
            _clientDict['Port']=int(info)
    _clients.append(_clientDict)
    print('Connected to: ' + _clientDict['IP'] + ':' + str(_clientDict['Port']))

def start_client(_client,_address):
    """Start new thread for new connection"""
    start_new_thread(threaded_client, (_client, _address))
    
def conncection_closed(_currentClient):
    """Eliminte client from list of clients when the connection is closed"""
    print('Connection closed with: ' +_address[0]+':'+str(_address[1]))
    _clients.remove(_currentClient)
    pass

def chunk_quality(_qualiReq,_segNum):
    """Find chunk size for desired quality and send it to the client"""
    _chosenQuali=[]
    _240p = [50,100,150,200]
    _480p=[]
    _720p=[]
    _1080p=[]
    _reprs = {'_240p': _240p,'_480p':_480p,'_720p':_720p,'_1080p':_1080p}
    _chosenQuali = _reprs[str(_qualiReq)]
    return _chosenQuali[random.randint(0,3)]


while True:
    _client, _address = ServerSocket.accept()
    save_client(_address)
    start_client(_client,_address)
    _threadCount += 1
    print(_clients) 
ServerSocket.close()
