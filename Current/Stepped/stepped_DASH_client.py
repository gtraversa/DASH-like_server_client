"""
Basic local client object simulating DASH for algorithm development.
Designed together with a server program, includes some parameter adjustment
using command line arguments for fast testing using multiple dicerse clients.
Data logging is specific to the parameters of the client.
Time dependency removed to work with stable_baselines and train the DQN.

(C)2020 Gianluca Traversa, London, United Kingdom.

email gianlu.traversa@gmail.com

"""



import socket,time,sys,getopt
import matplotlib.pyplot as plt
import numpy as np
import gym
from gym import spaces

class Client(gym.Env):
    """
    'DASH' asynchronous simulated client for training using stable baselines and OpenAI gym

    Paper:
    Default parameters chosen by experimetation

    :param bandwidth: Maximum bandwidth available on the client side in MB
    :param timer: Minimum time in seconds between segment request, necessary to avoid overloading the server
    :param req: Bool to indicate whether the client is currently requesting new data
    :param max_buf: Target maximum buffer health in seconds, used to avoid overloading the server
    :param host_IP: IP of host sending data (IPv4)
    :param host_port: Port the host will be listening on
    :param frame_size: Max frame size the client will accept
    :param quali_req: Start codec requested by client
    :param method: Method to be used by the client for codec selection (None,'MAX', 'rl','heuristic,'naive')
    :param chunk_length: Constant length of chunks sent by the server in seconds
    :param sigma: Standard deviation of normally distributed bandwidth available to the client in simulations
    :param training: If true, bandwidths will be uniformly distributed between specified bounds for more consistent training
    :param min_train: Lower bound of uniform distribution for training
    :param max_train: Upper bound of uniform distribution for training
    :param quali_param: Coefficient of codec reward in the reward function, the higher the more importance the agent will give to selecting higher codecs (typically between 0.7-1.5 experimentally)
    """
    def __init__(self,  bandwidth:  float = 100,
                        timer:      float = 0.3,
                        req:        bool = 1,
                        max_buf:    float = 10,
                        host_IP = '127.0.0.1',
                        host_port:  int = 1234, 
                        frame_size: int = 1024, 
                        quali_req:  str = '_240p',
                        method:     str = None,
                        chunk_length:float = 3,
                        sigma:      float = 10,
                        training:   bool = False,
                        min_train:  float = 1, 
                        max_train:  float = 100,
                        quali_param:float = 1.3):
        self.host_IP = host_IP
        self.host_port = host_port
        Client.connect(self)
        self.sigma = sigma
        self.start_bandwidth = bandwidth
        self.bandwidth = abs(sigma*np.random.randn()+ self.start_bandwidth )            #abs needed in extreme cases to avoid negative bandwidth
        self.timer = timer
        self.req = req
        self.max_buf = max_buf
        self.prev_buf = 0                                                               #Buffer health of the client in seconds
        self.t_last = 0                                                                 #Time last segment was received
        self.frame_size = frame_size
        self.seg_num = 0                                                                #Number of last segment received (used for requesting correct segment in the sequence)
        self.flg_finish_download = 0
        self.connected = False
        self.quali_req = quali_req
        self.stream_data = [[0,0,0,quali_req,self.start_bandwidth, self.bandwidth]]                     #Data for logging,codec seleciton calculations and training
        self.reprs = ['_240p','_360p','_480p','_720p','_1080p']                         #Available codecs
        self.current_repr = quali_req                                                   #Last requested codec
        self.method = method
        self.chunk_length = chunk_length
        self.log_name = self.create_log()
        self.current_time = 0
        self.action_space = spaces.Discrete(len(self.reprs))                            #Action space for DQN 
        self.observation_space = spaces.Box(np.array([0,0,0,0,0]),np.array([self.max_buf+self.chunk_length,1024,20,1024,len(self.reprs)])) #buffer,chunk,max_buf,max_band,prev_quality
        self.training = training
        self.min_train = min_train
        self.max_train = max_train
        self.quali_param = quali_param
         
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
        log_name = str(self.bandwidth)+'_'+str(self.timer)+'_'+str(self.max_buf)+'_'+str(self.method)+'_'+str(self.chunk_length)+'_buffer.txt'
        self.buffer_data = open(log_name,'w+')                                   
        self.buffer_data.truncate(0)
        return log_name
    
    def save_data_point(self,response):
        """Function to process buffer health and log it for analysis"""
        new_chunk = str(response).split(',')
        point = new_chunk[0]
        chunk_size=new_chunk[1]
        _timeToSend = float(new_chunk[2])
        if float(chunk_size) == -1.:                                                        #End contition included in the media files
            self.flg_finish_download = 1
            self.req = 0
        t,buf = self.current_time,(float(point)+self.prev_buf-_timeToSend)                  #Time and buffer health new data points
        if buf > 0:                        #Heathy buffer
            self.stream_data.append([t,buf,float(chunk_size),self.quali_req])
        else:                                                                               #Buffer event for negative buffer health
            buf = 0
            self.stream_data.append([t,buf,float(chunk_size),self.quali_req])
        if buf > self.max_buf:                                                              #Stop requesing media when buffer is saturated
            self.req = 0
        elif float(chunk_size) != -1:
            self.req=1
        self.prev_buf,self.t_last = buf,t

    def connect(self):
        """Connect to media server"""
        self.socket = socket.socket()
        while True:
            try:
                self.socket.connect((self.host_IP, self.host_port))
                self.connected = True
            except socket.error as e:
                break

    def debug_prints(self):
        """Print received data for debugging purposes"""
        new_chunk= str(self.response.decode('utf-8')).split(',')
        _length = str(new_chunk[0])
        _size = str(new_chunk[1])
        _timeToSend = str(new_chunk[2])
        _repr = str(self.quali_req)
        print('_________________________')
        print('Chunk length= '+_length) 
        print('Chunk size= '+_size)
        print('Time to Send= '+_timeToSend)
        print('Chunk quality= '+_repr)                   
        print('PrevBuf= '+ str(self.prev_buf))
        print('Bandwidth requested= '+str(self.bandwidth))
        print('Segment Number= '+ str(self.seg_num))

    def track_media(self):
        """Tracks the current media being streamed and requests the next available chunk"""
        if self.req==1:
            self.seg_num+=1

    def send_request(self,action):
        """Send media request to server"""
        message = str(self.bandwidth)+','+ str(self.req)+','+str(self.timer) +','+str(action)+','+str(self.seg_num)
        try:
            self.socket.send(str.encode(message))
        except socket.error as e:
            print(e)
        self.track_media()
    
    def save_file(self):
        for point in self.stream_data:
            for i in point:
                self.buffer_data.write(str(i)+',')
            self.buffer_data.write('\n')

    def reset(self):
        """Return initial state and change bandwidth for more generalized learning"""
        self.prev_buf = 0
        self.t_last = 0
        self.seg_num = 0
        self.flg_finish_download = 0
        self.quali_req = '_240p'
        self.stream_data = [[0,0,0,self.quali_req,self.start_bandwidth]]
        if not self.training:
            self.bandwidth = abs(self.sigma*np.random.randn()+ self.start_bandwidth )
        else:
            self.bandwidth = np.random.uniform(low = self.min_train, high = self.max_train)
        self.current_time=0
        return np.array([0,0,self.max_buf, self.bandwidth, 0]) 

    def calc_reward(self,action):
        """Calculate the reward for the last time step"""
        if self.prev_buf == 0 and self.seg_num != 0 and self.flg_finish_download != 1:
            return -500
        if not self.req:
            return 1
        return min(0, self.prev_buf-self.max_buf)+((action-len(self.reprs)+1)*self.quali_param)

    def is_done(self):
        """Checks if client is done"""
        if self.flg_finish_download == 1 :
            return True
        else:
            return False
        
    def time_step(self, send_time):
        """Step time forward the correct amount"""
        self.current_time += max(self.timer, send_time)

    def step(self, action):
        """Return step data"""
        self.quali_req = self.reprs[action]
        self.send_request(self.quali_req)
        try:
            self.response = self.socket.recv(self.frame_size)
        except socket.error as e:
            print(e)
        new_chunk= str(self.response.decode('utf-8')).split(',')
        self.time_step(float(new_chunk[2]))
        if self.flg_finish_download == 1:                                                          
            pass
        else:
            self.save_data_point(self.response.decode('utf-8'))
        
        self.calc_bandwidth(float(new_chunk[2]))
        reward = self.calc_reward(action)
        done = self.is_done()
        info = {    'bandwidth': self.bandwidth,
                    'buffer':self.prev_buf,
                    'is_req': self.req
                }
        new_state = np.array([self.prev_buf,float(new_chunk[1]),self.max_buf, self.bandwidth, self.reprs.index(self.quali_req)])
        self.stream_data[-1].append(self.bandwidth)
        return new_state,reward,done,info

    def disconnect_client(self):
        """Disconnect from server"""
        self.socket.close()
        self.connected = False

    def quali_select(self):
        """Basically the whole project: to implement"""
        self.current_repr = self.quali_req
        current_repr_idx = self.reprs.index(self.current_repr)
        if self.method == None:
            return 0
        elif self.method == 'heuristic':
            try:                                               
                if (self.stream_data[-1][4]*self.chunk_length)/self.stream_data[-1][2]> 1.1:     #if chunk could be downloaded 110% estimated bandwidth increase quality
                    if current_repr_idx != len(self.reprs)-1:
                        return current_repr_idx+1 
                    else:
                        return current_repr_idx              
                elif (self.stream_data[-1][4]*self.chunk_length)/self.stream_data[-1][2] < 0.9:   #if chunk could be downloaded 90% estimated bandwidth decrease quality
                    if current_repr_idx != 0:
                        return current_repr_idx -1
                    else:
                        return current_repr_idx
                else:
                    return current_repr_idx
            except ZeroDivisionError:
                return current_repr_idx
        elif self.method == 'MAX':
            return len(self.reprs)-1
        else:
            return 0

    def calc_bandwidth(self, download_time):
        """Approximates bandwidth from chunk size and download time"""
        
        if self.stream_data[-1][2]!= 0:
            estimated_bandwidth = self.stream_data[-1][2]/download_time
            self.stream_data[-1].append(estimated_bandwidth)
        elif self.req==1:
            flg=0
            for i in range(1,len(self.stream_data)):
                if self.stream_data[-i][2] !=0:
                    estimated_bandwidth = self.stream_data[-i][2]/download_time
                    self.stream_data[-1].append(estimated_bandwidth)
                    flg = 1
                    break
            if not flg:
                self.stream_data[-1].append(self.stream_data[-2][4])
        elif self.stream_data[-1][2] == -1:
            self.stream_data[-1].append(-1)
        else:
            self.stream_data[-1].append(self.stream_data[-2][4])