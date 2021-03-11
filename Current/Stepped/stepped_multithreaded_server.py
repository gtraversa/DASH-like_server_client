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
port = 1234

_clients = []
_frameSize = 2048
_initBandwith = 1000000
_totalBandwidth = 1000000

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
    _bandwidth = float(_setup[0])
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
    _timeToSend=max(_sendTime,_timer)                                           #Local transfer de layed by equivalent 'download' time OR minimum request time '_timer'
    reply = str(_chunkLength) + ',' + str(_bytesSent) + ',' + str(_timeToSend)  #Length of chunk in seconds sent back to client
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
    """Find chunk size for desired quality and send it to the client"""
    _chosenQuali=[]
    _240p = [25.00,25.69,26.27,26.63,26.67,26.35,25.71,24.87,23.96,23.15,22.50,21.97,21.54,21.27,21.20,21.38,21.80,22.43,23.23,24.10,25.00,25.87,26.60,27.18,27.62,27.99,28.34,28.70,29.04,29.33,29.50,29.52,29.39,29.10,28.61,27.94,27.15,26.36,25.70,25.25,25.00,24.78,24.49,24.16,23.87,23.71,23.72,23.90,24.22,24.61,25.00,25.32,25.36,25.07,24.57,24.04,23.67,23.58,23.81,24.33,25.00,25.69,26.28,26.60,26.53,26.03,25.15,24.10,23.11,22.39,22.00,21.79,21.75,21.88,22.18,22.60,23.11,23.63,24.14,24.59,25.00,25.34,25.45,25.28,24.92,24.50,24.13,23.86,23.69,23.59,23.50,23.40,23.11,22.59,21.97,21.44,21.22,21.45,22.22,23.46,25.00,26.58,28.03,29.19,29.92,30.18,30.04,29.64,29.17,28.79,28.50,28.15,27.74,27.28,26.79,26.29,25.83,25.44,25.16,25.02,25.00,25.01,25.07,25.20,25.39,25.60,25.81,25.98,26.07,26.07,26.00,25.89,25.78,25.70,25.65,25.60,25.55,25.47,25.36,25.19,25.00,24.81,24.68,24.62,24.63,24.71,24.81,24.91,24.98,25.01,25.00,24.96,24.79,24.52,24.24,24.04,24.00,24.13,24.38,24.69,25.00,25.31,25.62,25.87,26.00,25.96,25.76,25.48,25.21,25.04,25.00,24.99,25.02,25.09,25.19,25.29,25.37,25.38,25.32,25.19,25.00,24.81,24.68,24.62,24.63,24.71,24.81,24.91,24.98,25.01,25.00,24.98,24.93,24.86,24.81,24.79,24.82,24.88,24.95,24.99,-1]                                                 
    _360p = [56.25,57.79,59.11,59.92,60.01,59.29,57.86,55.95,53.92,52.09,50.62,49.42,48.46,47.85,47.71,48.10,49.05,50.48,52.26,54.23,56.25,58.21,59.86,61.15,62.14,62.98,63.77,64.57,65.34,65.99,66.38,66.42,66.14,65.47,64.38,62.87,61.09,59.31,57.81,56.81,56.25,55.76,55.10,54.36,53.71,53.34,53.36,53.78,54.50,55.37,56.25,56.97,57.06,56.41,55.28,54.10,53.26,53.06,53.58,54.74,56.25,57.80,59.13,59.86,59.70,58.56,56.59,54.23,51.99,50.38,49.50,49.03,48.93,49.23,49.90,50.86,51.99,53.17,54.30,55.33,56.25,57.02,57.26,56.87,56.06,55.12,54.29,53.69,53.31,53.07,52.87,52.65,51.99,50.82,49.42,48.24,47.74,48.27,49.98,52.78,56.25,59.81,63.07,65.67,67.31,67.91,67.59,66.69,65.63,64.77,64.13,63.35,62.41,61.37,60.27,59.16,58.11,57.23,56.61,56.31,56.25,56.27,56.41,56.70,57.12,57.61,58.08,58.45,58.66,58.66,58.50,58.25,58.02,57.83,57.71,57.61,57.49,57.32,57.05,56.69,56.25,55.82,55.52,55.39,55.42,55.59,55.82,56.04,56.20,56.26,56.25,56.15,55.78,55.17,54.54,54.10,54.00,54.29,54.86,55.56,56.25,56.94,57.64,58.21,58.50,58.40,57.96,57.33,56.72,56.35,56.25,56.24,56.30,56.46,56.68,56.91,57.08,57.11,56.98,56.68,56.25,55.82,55.52,55.39,55.42,55.59,55.82,56.04,56.20,56.26,56.25,56.20,56.09,55.94,55.82,55.78,55.85,55.98,56.13,56.23,-1]
    _480p=  [126.56,130.04,133.00,134.83,135.03,133.41,130.18,125.89,121.32,117.20,113.91,111.20,109.04,107.67,107.35,108.24,110.36,113.57,117.58,122.01,126.56,130.96,134.69,137.58,139.82,141.71,143.49,145.29,147.03,148.48,149.34,149.44,148.80,147.32,144.84,141.45,137.46,133.46,130.08,127.82,126.56,125.45,123.98,122.31,120.85,120.02,120.07,121.01,122.63,124.58,126.56,128.19,128.38,126.92,124.38,121.72,119.84,119.38,120.56,123.16,126.56,130.06,133.03,134.69,134.33,131.75,127.34,122.01,116.99,113.35,111.37,110.32,110.09,110.77,112.28,114.43,116.97,119.63,122.18,124.49,126.56,128.30,128.83,127.96,126.14,124.03,122.15,120.80,119.95,119.40,118.97,118.47,116.98,114.35,111.20,108.54,107.41,108.60,112.46,118.75,126.56,134.57,141.91,147.75,151.45,152.79,152.08,150.05,147.67,145.73,144.28,142.53,140.41,138.08,135.61,133.11,130.75,128.77,127.37,126.69,126.56,126.62,126.93,127.58,128.52,129.62,130.68,131.51,131.97,131.99,131.63,131.07,130.54,130.13,129.84,129.62,129.36,128.96,128.36,127.54,126.56,125.61,124.92,124.62,124.71,125.08,125.59,126.09,126.45,126.59,126.56,126.34,125.51,124.14,122.71,121.72,121.51,122.15,123.44,125.01,126.56,128.11,129.69,130.98,131.62,131.41,130.42,128.98,127.62,126.78,126.56,126.54,126.68,127.03,127.53,128.05,128.42,128.50,128.21,127.52,126.56,125.61,124.92,124.62,124.71,125.08,125.59,126.09,126.45,126.59,126.56,126.46,126.21,125.88,125.60,125.51,125.65,125.96,126.30,126.52,-1]
    _720p=  [284.77,292.58,299.25,303.36,303.81,300.17,292.91,283.26,272.97,263.70,256.29,250.20,245.35,242.27,241.53,243.53,248.31,255.54,264.55,274.52,284.77,294.67,303.05,309.55,314.59,318.84,322.85,326.90,330.81,334.08,336.02,336.24,334.81,331.46,325.90,318.26,309.29,300.28,292.69,287.58,284.77,282.26,278.95,275.19,271.91,270.04,270.15,272.27,275.92,280.31,284.77,288.43,288.86,285.56,279.86,273.86,269.63,268.60,271.26,277.11,284.77,292.62,299.33,303.04,302.24,296.45,286.51,274.52,263.22,255.03,250.59,248.22,247.71,249.23,252.63,257.47,263.19,269.18,274.92,280.09,284.77,288.69,289.87,287.91,283.83,279.06,274.84,271.80,269.89,268.65,267.68,266.56,263.21,257.29,250.20,244.22,241.67,244.35,253.04,267.19,284.77,302.79,319.30,332.44,340.76,343.78,342.17,337.61,332.26,327.88,324.63,320.69,315.93,310.69,305.13,299.50,294.20,289.72,286.59,285.05,284.77,284.89,285.58,287.05,289.17,291.64,294.03,295.91,296.94,296.99,296.16,294.90,293.71,292.79,292.15,291.64,291.05,290.17,288.82,286.97,284.77,282.61,281.06,280.40,280.59,281.43,282.59,283.71,284.50,284.82,284.77,284.27,282.39,279.32,276.10,273.86,273.39,274.84,277.74,281.27,284.77,288.26,291.80,294.69,296.14,295.67,293.43,290.21,287.14,285.26,284.77,284.71,285.03,285.82,286.94,288.10,288.94,289.14,288.47,286.92,284.77,282.61,281.06,280.40,280.59,281.43,282.59,283.71,284.50,284.82,284.77,284.53,283.97,283.22,282.61,282.41,282.72,283.42,284.17,284.66,-1]
    _1080p= [640.72,658.31,673.31,682.56,683.57,675.39,659.04,637.34,614.18,593.33,576.65,562.95,552.04,545.10,543.44,547.94,558.71,574.97,595.24,617.67,640.72,663.01,681.85,696.49,707.83,717.38,726.42,735.51,744.31,751.68,756.05,756.53,753.32,745.79,733.27,716.08,695.90,675.62,658.54,647.06,640.72,635.09,627.64,619.19,611.80,607.59,607.83,612.61,620.82,630.69,640.72,648.98,649.94,642.51,629.68,616.19,606.67,604.35,610.34,623.49,640.72,658.41,673.49,681.85,680.05,667.00,644.64,617.67,592.24,573.81,563.84,558.50,557.35,560.77,568.41,579.30,592.17,605.65,618.56,630.21,640.72,649.54,652.21,647.80,638.61,627.88,618.39,611.55,607.26,604.46,602.28,599.75,592.22,578.90,562.96,549.49,543.76,549.80,569.35,601.18,640.72,681.28,718.43,747.99,766.71,773.50,769.88,759.63,747.59,737.74,730.42,721.54,710.85,699.04,686.54,673.89,661.94,651.87,644.82,641.35,640.72,641.00,642.56,645.86,650.64,656.19,661.56,665.79,668.12,668.22,666.35,663.53,660.84,658.77,657.33,656.19,654.87,652.88,649.84,645.68,640.72,635.88,632.39,630.89,631.32,633.21,635.82,638.35,640.13,640.86,640.72,639.60,635.38,628.47,621.22,616.19,615.13,618.38,624.91,632.86,640.72,648.58,656.54,663.06,666.31,665.25,660.23,652.97,646.07,641.84,640.72,640.59,641.31,643.10,645.62,648.23,650.12,650.56,649.05,645.57,640.72,635.88,632.39,630.89,631.32,633.21,635.82,638.35,640.13,640.86,640.72,640.19,638.94,637.25,635.86,635.42,636.13,637.69,639.39,640.49,-1]
    _reprs = {'_240p': _240p,'_360p':_360p,'_480p':_480p,'_720p':_720p,'_1080p':_1080p}
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
    
