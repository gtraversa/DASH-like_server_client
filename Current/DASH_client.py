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
import matplotlib.animation as animation
import numpy as np

class Client:
    def __init__(self,bandwidth=100,timer=0.3,req=1,max_buf=10,host_IP = '127.0.0.1', host_port = 1233, frame_size = 1024, connected = False, quali_req = '_240p',method = None, episodes = 1,gamma = 1, epsilon = 0.1,chunk_length = 3,Q = None):
        self.host_IP = host_IP
        self.host_port = host_port
        self.bandwidth = bandwidth
        self.timer = timer
        self.req = req
        self.max_buf = max_buf
        self.prev_buf = 0
        self.t_last = 0
        self.frame_size = frame_size
        self.start = time.time()
        self.seg_num = 0
        self.flg_finish_download = 0
        self.connected = connected
        self.quali_req = quali_req
        self.stream_data = [[0,0,0,bandwidth,quali_req]]
        self.reprs = ['_240p','_480p','_720p','_1080p']
        self.current_repr = quali_req
        self.method = method
        self.episodes = episodes
        self.gamma = gamma
        self.epsilon = epsilon
        self.chunk_length = chunk_length
        self.log_name = self.create_log()
        self.Q = Q
        self.alpha = 1/(1+self.seg_num)
    
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
        log_name = str(self.bandwidth)+'_'+str(self.timer)+'_'+str(self.max_buf)+'_'+str(self.method)+'_'+str(self.chunk_length)+'_'+str(self.episodes)+'_buffer.txt'
        self.buffer_data = open(log_name,'w+')                                   
        self.buffer_data.truncate(0)
        return log_name
    
    def save_data_point(self,response):
        """Function to process buffer health and log it for analysis"""
        now = time.time()
        new_chunk = str(response).split(',')
        point = new_chunk[0]
        chunk_size=new_chunk[1]
        if float(chunk_size) == -1.:                                           #End contition included in the media files
            print('Media finished.')
            self.flg_finish_download = 1
            self.req = 0
        t_diff = now-self.start-self.t_last                                         #Time decrease as media plays
        t,buf = now-self.start,(float(point)+self.prev_buf-t_diff)               #Time and buffer health new data points

        if buf > 0:                        #Heathy buffer
            self.stream_data.append([t,buf,float(chunk_size)])
        else:                                                                                             #Buffer event for negative buffer health
            buf = 0
            self.stream_data.append([t,buf,float(chunk_size)])
        if buf > self.max_buf:                                                  #Stop requesing media when buffer is saturated
            self.req = 0
        elif float(chunk_size) != -1:
            self.req=1
        self.prev_buf,self.t_last = buf,t

    def quali_select(self):
        """Basically the whole project: to implement"""
        self.current_repr = self.quali_req
        current_repr_idx = self.reprs.index(self.current_repr)
        if self.method == None:
            pass
        elif self.method == 'heuristic':
            try:                                               
                if (self.stream_data[-1][3]*self.chunk_length)/self.stream_data[-1][2]> 1.1:     #if chunk could be downloaded 110% estimated bandwidth increase quality
                    if current_repr_idx != len(self.reprs)-1:
                        self.quali_req = self.reprs[current_repr_idx+1]               
                elif (self.stream_data[-1][3]*self.chunk_length)/self.stream_data[-1][2] < 0.9:   #if chunk could be downloaded 90% estimated bandwidth decrease quality
                    if current_repr_idx != 0:
                        self.quali_req = self.reprs[current_repr_idx-1]
            except ZeroDivisionError:
                pass
        elif self.method == 'rl':
            pass
        elif self.method == 'MAX':
            self.quali_req = self.reprs[-1]
        elif self.method == 'naive':
            try:                                               
                if (self.bandwidth*self.chunk_length)/self.stream_data[-1][2]> 1.1:     #if chunk could be downloaded 110% ideal bandwidth increase quality
                    if current_repr_idx != len(self.reprs)-1:
                        self.quali_req = self.reprs[current_repr_idx+1]               
                elif (self.bandwidth*self.chunk_length)/self.stream_data[-1][2] < 0.9:   #if chunk could be downloaded 90% ideal bandwidth decrease quality
                    if current_repr_idx != 0:
                        self.quali_req = self.reprs[current_repr_idx-1]
            except ZeroDivisionError:
                pass
        else:
            self.quali_req = '_240p'     


    def connect(self):
        """Connect to media server"""
        print('Waiting for connection')
        self.socket = socket.socket()
        while True:
            try:
                self.socket.connect((self.host_IP, self.host_port))
                self.connected = True
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
        if self.req==1:
            self.seg_num+=1

    def send_request(self):
        """Send media request to server"""
        message = str(self.bandwidth)+','+ str(self.req)+','+str(self.timer) +','+str(self.quali_req)+','+str(self.seg_num)
        self.socket.send(str.encode(message))
        self.track_media()
    
    def save_file(self):
        for point in self.stream_data:
            for i in point:
                self.buffer_data.write(str(i)+',')
            self.buffer_data.write('\n')

    def calc_bandwidth(self):
        """Approximates bandwidth from chunk size and download time"""
        
        if self.stream_data[-1][2]!= 0:
            download_time = self.stream_data[-1][0]-self.stream_data[-2][0]
            estimated_bandwidth = self.stream_data[-1][2]/download_time
            self.stream_data[-1].append(estimated_bandwidth)
        elif self.req==1:
            for i in range(1,len(self.stream_data)):
                if self.stream_data[-i][2] !=0:
                    download_time = self.stream_data[-i][0]-self.stream_data[-i-1][0]
                    estimated_bandwidth = self.stream_data[-i][2]/download_time
                    self.stream_data[-1].append(estimated_bandwidth)
                    break
        elif self.stream_data[-1][2] == -1:
            print('pepe')
            self.stream_data[-1].append(-1)
        else:
            self.stream_data[-1].append(self.stream_data[-2][3])
        self.stream_data[-1].append(self.quali_req)

    def avg_chunk(self):
        """Calculate average chunk size"""
        pass

    def calculate_reward(self):
        """Calculate reward for value function"""
        pass

    def update_value_function(self):
        """Update the value function according ot Sarsa update"""
        pass

    def Q_value_function(self,s,a):
        """Returns value of state-action pair"""
        pass

    def disconnect_client(self):
        """Disconnect from server"""
        self.socket.close()
        self.connected = False

    def reset_client(self):
        """Reset client when reconnecting"""
        self.prev_buf = 0
        self.t_last = 0
        #self.start = time.time()
        self.seg_num = 0
        self.flg_finish_download = 0
        self.quali_req = '_240p'

    def start_request(self):
        """Begin media requests"""
        while True:
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
                if self.flg_finish_download == 1 and self.prev_buf == 0:
                    print('Disconnecting from server...')
                    break
                self.calc_bandwidth()
                self.quali_select()
                print(self.stream_data[-1])
            if self.connected:
                self.disconnect_client()
                self.episodes -=1
                #TODO figure out wtf to do with Q probably n-step semigratdient SARSA for q(w,s,a)
                self.reset_client()
            print(self.episodes)
            if not self.episodes:
                self.save_file()
                self.disconnect_client()
                break

c = Client(episodes = 3, method = 'heuristic', bandwidth = 500)
c.start_request()