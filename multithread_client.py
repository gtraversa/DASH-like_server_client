"""
Basic local client simulating DASH for algorithm development.
Very simple first implementation with little adjustment serving as a starting point.

(C)2020 Gianluca Traversa, London, United Kingdom.

email gianlu.traversa@gmail.com

"""


import socket,time,sys

ClientSocket = socket.socket()
host = '127.0.0.1'
port = 1233

print('Waiting for connection')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))




_prevBuf=0
_tLast=0
_frameSize = 1024
_start = time.time()
_bandwidth = 100
_req = 1                                                                #Initial request set to True
_timer = 1                                                              #Minimum time in seconds between each request
_maxBuf = 15                                                            #Maximum desired buffer in seconds (to avoid  unnecessary server load)
_qualiReq = '_240p'
_segNum=1


def save_data_point(_point,_prevBuf,_tLast,_log):
    """Function to process buffer health and log it to a file for analysis"""
    _now = time.time()
    _chunkInfo= str(_point).split(',')
    _point = _chunkInfo[0]
    _chunkSize=_chunkInfo[1]
    _tDiff = _now-_start-_tLast                                         #Time decrease as media plays
    _t,_buf = _now-_start,(float(_point)+_prevBuf-_tDiff)               #Time and buffer health new data points
    if _buf > 0:
        _bufferData.write(str(_t)+','+str(_buf)+'\n')                   #Heathy bffer
    else:                                                               #Buffer event for negative buffer health
        _buf = 0
        _bufferData.write(str(_t)+','+str(_buf)+'\n') 
    if _buf > _maxBuf:                                                  #Stop requesing media when buffer is saturated
        _req = 0
    else:
        _req=1 
    return _buf,_t,_req,_chunkSize


# def main(num):
num=1
_logName = str(num)+'_buffer.txt'
_bufferData = open(_logName,'w+')                                   #Logging file created for buffer health
_bufferData.truncate(0)                                                 #cleared each time a client is initiated (if multiple clients rename file)
while True:
    _setup = str(_bandwidth)+','+ str(_req)+','+str(_timer) +','+str(_qualiReq)+','+str(_segNum)            #Pass setup to server,will be implemented with command line args for simplicity
    ClientSocket.send(str.encode(_setup))
    _response = ClientSocket.recv(_frameSize)
    if _response.decode('utf-8')=='End':                                #End of media stream condition
        break
    _prevBuf,_tLast,_req,_chunkSize = save_data_point(_response.decode('utf-8'),_prevBuf,_tLast,_bufferData)
    print('Response = '+_response.decode('utf-8'))                      #Print response from server for debugging
    print('PrevBuf= '+ str(_prevBuf))
    print('ChunkSize= '+ str(_chunkSize))

ClientSocket.close()

# if __name__ == "__main__":
#     num = int(sys.argv[1])
#     main(num)
