"""
Basic local client object simulating DASH for algorithm development.
Designed together with a server program, includes some parameter adjustment
using command line arguments for fast testing using multiple dicerse clients.
Data logging is specific to the parameters of the client.

(C)2020 Gianluca Traversa, London, United Kingdom.

email gianlu.traversa@gmail.com

"""



import socket,time,sys,getopt
import matplotlib.pyplot as plt

class Client:
    def __init__(self,bandwidth=100,timer=1,req=1,maxBuf=10,hostIP = '127.0.0.1', hostPort = 1233, frameSize = 1024, connected = False, qualiReq = '_240p'):
        self.socket = socket.socket()
        self.host_IP = hostIP
        self.host_port = hostPort
        self.bandwidth = bandwidth
        self.timer = timer
        self.req = req
        self.max_buf = maxBuf
        self.prev_buf = 0
        self.t_last = 0
        self.frame_size = frameSize
        self.start = time.time()
        self.seg_num = 0
        self.flg_finish_download = 0
        self.connected = connected
        self.quali_req = qualiReq
        self.log_name = Client.create_log(self)
    
    def toString(self):
        """Print Attributes"""
        print('Host IP: '+ self.host_IP)
        print('Host port: '+ str(self.host_port))
        print('Maximum bandwidth: '+ str(self.bandwidth))
        print('Request minimum timer: '+str(self.timer))
        print('Request: '+str(bool(self.req)))
        print('Maximum buffer: '+str(self.max_buf))
        print('Connected: '+str(self.connected))
    
    def create_log(self):
        """Creates .txt file for logging buffer health with parameters in the name"""
        log_name = str(self.bandwidth)+'_'+str(self.timer)+'_'+str(self.max_buf)+'_buffer.txt'
        self.buffer_data = open(log_name,'w+')                                   
        self.buffer_data.truncate(0)
        self.buffer_data.write('0,0,0\n')
        return log_name
    
    def save_data_point(self,response):
        """Function to process buffer health and log it to a file for analysis"""
        now = time.time()
        new_chunk = str(response).split(',')
        point = new_chunk[0]
        chunk_size=new_chunk[1]
        if int(chunk_size) == -1:                                           #End contition included in the media files
            print('Media finished.')
            self.flg_finish_download = 1
            self.req = 0
        t_diff = now-self.start-self.t_last                                         #Time decrease as media plays
        t,buf = now-self.start,(float(point)+self.prev_buf-t_diff)               #Time and buffer health new data points

        if buf > 0:
            self.buffer_data.write(str(t)+','+str(buf)+','+str(chunk_size)+'\n')                          #Heathy bffer
        else:                                                               #Buffer event for negative buffer health
            buf = 0
            self.buffer_data.write(str(t)+','+str(buf)+','+str(chunk_size)+'\n')
        if buf > self.max_buf:                                                  #Stop requesing media when buffer is saturated
            self.req = 0
        elif int(chunk_size) != -1:
            self.req=1
        self.prev_buf,self.t_last = buf,t

    def quali_select(self):
        """Basically the whole project: to implement"""
        pass

    def connect(self, host_IP = None, host_port = None):
        """Connect to media server"""
        if host_IP==None:
            host_IP = self.host_IP
        if host_port == None:
            host_port = self.host_port
        print('Waiting for connection')
        while True:
            try:
                self.socket.connect((host_IP, host_port))
                self.connected = True
                break
            except socket.error as e:
                print(str(e))
                break

    def debug_prints(self):
        """Print received data for debugging purposes"""
        new_chunk= str(self.response.decode('utf-8')).split(',')
        _length = str(new_chunk[0])
        _size = str(new_chunk[1])
        _repr = str(self.quali_req)
        print('_________________________')
        print('Chunk length= '+_length) 
        print('Chunk size= '+_size)
        print('Chunk quality= '+_repr)                   
        print('PrevBuf= '+ str(self.prev_buf))
        print('Segment Number= '+ str(self.seg_num))

    def track_media(self):
        """Tracks the current media being streamed and requests the next available chunk"""
        pass

    def send_request(self):
        """Send media request to server"""
        message = str(self.bandwidth)+','+ str(self.req)+','+str(self.timer) +','+str(self.quali_req)+','+str(self.seg_num)
        self.socket.send(str.encode(message))

    def print_data_graph(self):
        """Prints buffer and chunk data graph updated"""
        fig = plt.figure()
        ax1 = fig.add_subplot(1,1,1)
        ax2 = ax1.twinx() 
        graph_data = open(self.log_name,'r').read()
        lines = graph_data.split('\n')
        ts = []
        bufs = []
        chunks = []
        for line in lines:
            if len(line) > 1:
                t, buf,chunk = line.split(',')
                ts.append(float(t))
                bufs.append(float(buf))
                chunks.append(int(chunk))

        ax1.plot(ts,bufs,color = 'tab:red')
        ax1.set_xlabel('Simulation time (s)')
        ax1.set_ylabel('Buffer health (s)')
        ax1.tick_params(axis='y', labelcolor= 'tab:red')
        ax2.plot(ts,chunks,color = 'tab:blue')
        ax2.set_ylabel('Chunk sizes (MBit)')
        ax2.tick_params(axis='y', labelcolor= 'tab:blue')
        fig.tight_layout()
        plt.show()

    def start_request(self):
        """Begin media requests"""
        while not self.connected:
            self.connect()
            time.sleep(1)
        while True:
            self.send_request()
            self.response = self.socket.recv(self.frame_size)
            self.debug_prints()
            if self.flg_finish_download == 1:                                                          
                self.save_data_point('-1,-1')
            else:
                self.save_data_point(self.response.decode('utf-8'))
            #self.print_data_graph()
        self.socket.close()

    

c = Client()
c.start_request()
