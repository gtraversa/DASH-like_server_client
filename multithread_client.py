"""
Basic local client simulating DASH for algorithm development.
Very simple first implementation with little adjustment serving as a starting point.

(C)2020 Gianluca Traversa, London, United Kingdom.

email gianlu.traversa@gmail.com

"""


import socket,time,sys,getopt

ClientSocket = socket.socket()
host = '127.0.0.1'
port = 1233






_prevBuf=0
_tLast=0
_frameSize = 1024
_start = time.time()                                                            
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
        _log.write(str(_t)+','+str(_buf)+'\n')                   #Heathy bffer
    else:                                                               #Buffer event for negative buffer health
        _buf = 0
        _log.write(str(_t)+','+str(_buf)+'\n') 
    if _buf > _maxBuf:                                                  #Stop requesing media when buffer is saturated
        _req = 0
    else:
        _req=1 
    return _buf,_t,_req,_chunkSize


def create_setup(_bandwidth,_timer,_req):
    """Takes command line arguments for initial setup of client"""
    _qualiReq = quali_select()
    _segNum = 1 #implement segment tracking
    _setup = str(_bandwidth)+','+ str(_req)+','+str(_timer) +','+str(_qualiReq)+','+str(_segNum)
    return _setup

def initial_setup(opts):
    """Parse initial setup arguments """
    _bandwidth,_timer,_req = 100,1,1
    for o, a in opts:
        if o in ('-h','--help'):
           print("You're on your own")
           print('-h,--help')
           print('-b,--bandwidth: Set the client maximum bandwidth')
           print('-r,--request: Use if you desire client NOT to request data')
           print('-t,--timer: Set client minimum time between requests')
           sys.exit()
        elif o in ('-b','--bandwidth'):
            _bandwidth = int(a)
        elif o in ('-t','--timer'):
            _timer = float(a)
        elif o in ('-r','--request'):
            _req = 0
    connect()
    _bufferData=create_log(_bandwidth,_timer)
    return _bandwidth,_timer,_req,_bufferData

def create_log(_bandwidth,_timer):
    """Creates .txt file for logging buffer health with parameters in the name"""
    _logName = str(_bandwidth)+'_'+str(_timer)+'_'+'_buffer.txt'
    _bufferData = open(_logName,'w+')                                   #Logging file created for buffer health
    _bufferData.truncate(0)
    return _bufferData

def quali_select():
    """Basically the whole project: to implement"""
    return '_240p'

def connect():
    print('Waiting for connection')
    try:
        ClientSocket.connect((host, port))
    except socket.error as e:
        print(str(e))

def main(argv):
    global _prevBuf,_tLast
    try:
        opts, args = getopt.getopt(argv,"hb:t:r",["help","bandwidth=","timer=","request"])
    except getopt.GetoptError:
        print('Wrong inputs retardo')
        sys.exit(2)
    _bandwidth,_timer,_req,_bufferData = initial_setup(opts)
    while True:
        _setup = create_setup(_bandwidth,_timer,_req)            #Pass setup to server,will be implemented with command line args for simplicity
        ClientSocket.send(str.encode(_setup))
        _response = ClientSocket.recv(_frameSize)
        if _response.decode('utf-8')=='End':                                #End of media stream condition
            break
        _prevBuf,_tLast,_req,_chunkSize = save_data_point(_response.decode('utf-8'),_prevBuf,_tLast,_bufferData)
        print('_________________________')
        print('Response = '+_response.decode('utf-8'))                      #Print response from server for debugging
        print('PrevBuf= '+ str(_prevBuf))
        print('ChunkSize= '+ str(_chunkSize))

    ClientSocket.close()

if __name__ == "__main__":
    main(sys.argv[1:])