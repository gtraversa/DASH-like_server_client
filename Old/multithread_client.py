"""
Basic local client simulating DASH for algorithm development.
Designed together with a server program, includes some parameter adjustment
using command line arguments for fast testing using multiple dicerse clients.
Data logging is specific to the parameters of the client.

(C)2020 Gianluca Traversa, London, United Kingdom.

email gianlu.traversa@gmail.com

"""


import socket,time,sys,getopt

_clientSocket = socket.socket()
_host = '127.0.0.1'
_port = 1233

_prevBuf=0
_tLast=0
_frameSize = 1024
_start = time.time()                                                            

def save_data_point(_response,_prevBuf,_tLast,_log,_segNum,_maxBuf):
    """Function to process buffer health and log it to a file for analysis"""
    _flgFinishDownload = 0
    _now = time.time()
    _chunkInfo= str(_response).split(',')
    _point = _chunkInfo[0]
    _chunkSize=_chunkInfo[1]
    if int(_chunkSize) == -1:                                           #End contition included in the media files
        print('Media finished.')
        _flgFinishDownload = 1
        _req = 0
    _tDiff = _now-_start-_tLast                                         #Time decrease as media plays
    _t,_buf = _now-_start,(float(_point)+_prevBuf-_tDiff)               #Time and buffer health new data points

    if _buf > 0:
        _log.write(str(_t)+','+str(_buf)+','+str(_chunkSize)+'\n')                          #Heathy bffer
    else:                                                               #Buffer event for negative buffer health
        _buf = 0
        _log.write(str(_t)+','+str(_buf)+','+str(_chunkSize)+'\n')
    if _buf > _maxBuf:                                                  #Stop requesing media when buffer is saturated
        _req = 0
    elif int(_chunkSize) != -1:
        _req=1 
    return _buf,_t,_req,_chunkSize,_flgFinishDownload,_segNum


def create_setup(_bandwidth,_timer,_req,_segNum):
    """Takes command line arguments for initial setup of client"""
    _qualiReq = quali_select()
    if _req:
        _segNum=track_media(_segNum)
    _setup = str(_bandwidth)+','+ str(_req)+','+str(_timer) +','+str(_qualiReq)+','+str(_segNum)
    return _setup,_qualiReq,_segNum

def initial_setup(opts):
    """Parse initial setup arguments from command line"""
    _bandwidth,_timer,_req,_maxBuf = 100,1,1,10                         #Default settings
    for o, a in opts:
        if o in ('-h','--help'):
           print("You're on your own")
           print('-h,--help')
           print('-b,--bandwidth: Set the client maximum bandwidth (default:100Mbit)')
           print('-r,--request: Use if you desire client NOT to request data')
           print('-t,--timer: Set client minimum time between requests(default:1s)')
           print('-m,--max_buffer: Set the maximum buffer desired for the client(default:10s)')
           sys.exit()
        elif o in ('-b','--bandwidth'):
            _bandwidth = int(a)
        elif o in ('-t','--timer'):
            _timer = float(a)
        elif o in ('-r','--request'):
            _req = 0
        elif o in ('-m','--maxbuffer'):
            _maxBuf = int(a)
    connect()                                                           #Create connection to server if parameters initialized properly
    _bufferData=create_log(_bandwidth,_timer,_maxBuf)                   #Create logging file
    return _bandwidth,_timer,_req,_bufferData,_maxBuf

def create_log(_bandwidth,_timer,_maxBuf):
    """Creates .txt file for logging buffer health with parameters in the name"""
    _logName = str(_bandwidth)+'_'+str(_timer)+'_'+str(_maxBuf)+'_buffer.txt'
    _bufferData = open(_logName,'w+')                                   #Logging file created for buffer health
    _bufferData.truncate(0)
    _bufferData.write('0,0,0\n')
    return _bufferData

def quali_select():
    """Basically the whole project: to implement"""
    return '_240p'

def connect():
    print('Waiting for connection')
    while True:
        try:
            _clientSocket.connect((_host, _port))
            break
        except socket.error as e:
            print(str(e))

def send_request(_clientSocket, _setup):
    """Send media request to server"""
    _clientSocket.send(str.encode(_setup))
    

def debug_prints(_response,_qualiReq,_segNum):
    """Print received data for debugging purposes"""
    _chunkInfo= str(_response.decode('utf-8')).split(',')
    _length = str(_chunkInfo[0])
    _size = str(_chunkInfo[1])
    _repr = str(_qualiReq)
    print('_________________________')
    print('Chunk length= '+_length) 
    print('Chunk size= '+_size)
    print('Chunk quality= '+_repr)                   
    print('PrevBuf= '+ str(_prevBuf))
    print('Segment Number= '+ str(_segNum))

def track_media(_segNum):
    """Tracks the current media being streamed and requests the next available chunk"""
    _segNum+=1
    return _segNum

def main(argv):
    global _prevBuf,_tLast
    _flgFinishDownload = 0
    _segNum=0
    try:
        opts, args = getopt.getopt(argv,"hb:t:rm:",["help","bandwidth=","timer=","request","max_buffer="])
    except getopt.GetoptError:
        print('Wrong inputs')
        sys.exit(2)
    _bandwidth,_timer,_req,_bufferData,_maxBuf = initial_setup(opts)
    while True:
        _setup,_qualiReq,_segNum = create_setup(_bandwidth,_timer,_req,_segNum)                         #Create setup to send to server
        send_request(_clientSocket,_setup)
        _response = _clientSocket.recv(_frameSize)
        if _flgFinishDownload == 1:                                                          #End of media stream condition (not implemented yet on server side)
            _prevBuf,_tLast,_req,_chunkSize,_flgFinishDownload,_segNum = save_data_point('-1,-1',_prevBuf,_tLast,_bufferData,_segNum,_maxBuf)
        else:
            _prevBuf,_tLast,_req,_chunkSize,_flgFinishDownload,_segNum = save_data_point(_response.decode('utf-8'),_prevBuf,_tLast,_bufferData,_segNum,_maxBuf)
        debug_prints(_response,_qualiReq,_segNum)

    _clientSocket.close()

if __name__ == "__main__":
    main(sys.argv[1:])