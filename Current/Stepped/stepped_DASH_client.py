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
import gym
from gym import spaces

class Client(gym.Env):
    def __init__(self,bandwidth=100,timer=0.3,req=1,max_buf=10,host_IP = '127.0.0.1', host_port = 1234, frame_size = 1024, connected = False, quali_req = '_240p',method = None, episode_num=1,chunk_length = 3, time_scale = 1,sigma = 10):
        self.time_scale = time_scale
        self.host_IP = host_IP
        self.host_port = host_port
        Client.connect(self)
        self.sigma = sigma
        self.start_bandwidth = bandwidth
        self.bandwidth = sigma*np.random.randn()+ self.start_bandwidth * self.time_scale
        self.timer = timer/self.time_scale
        self.req = req
        self.max_buf = max_buf
        self.prev_buf = 0
        self.t_last = 0
        self.frame_size = frame_size
        self.seg_num = 0
        self.flg_finish_download = 0
        self.connected = connected
        self.quali_req = quali_req
        self.stream_data = [[0,0,0,quali_req]]
        self.reprs = ['_240p','_480p','_720p','_1080p']
        self.current_repr = quali_req
        self.method = method
        self.episode_num = episode_num
        self.chunk_length = chunk_length
        self.log_name = self.create_log()
        self.current_time = 0
        self.action_space = spaces.Discrete(len(self.reprs))
        self.observation_space = spaces.Box(np.array([0,0,0,0,0]),np.array([self.max_buf+self.chunk_length,1024,20,1024,len(self.reprs)])) #buffer,chunk,max_buf,max_band,prev_quality
        
    
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
        log_name = str(self.bandwidth)+'_'+str(self.timer)+'_'+str(self.max_buf)+'_'+str(self.method)+'_'+str(self.chunk_length)+'_'+str(self.episode_num)+'_buffer.txt'
        self.buffer_data = open(log_name,'w+')                                   
        self.buffer_data.truncate(0)
        return log_name
    
    def save_data_point(self,response):
        """Function to process buffer health and log it for analysis"""
        new_chunk = str(response).split(',')
        point = new_chunk[0]
        chunk_size=new_chunk[1]
        _timeToSend = new_chunk[2]
        if float(chunk_size) == -1.:                                           #End contition included in the media files
            print('Media finished.')
            self.flg_finish_download = 1
            self.req = 0
        t_diff = (self.current_time-self.t_last)*self.time_scale                                         #Time decrease as media plays
        t,buf = self.current_time,(float(point)+self.prev_buf-t_diff)               #Time and buffer health new data points

        if buf > 0:                        #Heathy buffer
            self.stream_data.append([t,buf,float(chunk_size),self.quali_req])
        else:                                                                                             #Buffer event for negative buffer health
            buf = 0
            self.stream_data.append([t,buf,float(chunk_size),self.quali_req])
        if buf > self.max_buf:                                                  #Stop requesing media when buffer is saturated
            self.req = 0
        elif float(chunk_size) != -1:
            self.req=1
        self.prev_buf,self.t_last = buf,t

    def connect(self):
        """Connect to media server"""
        print('Waiting for connection')
        self.socket = socket.socket()
        while True:
            try:
                self.socket.connect((self.host_IP, self.host_port))
                self.connected = True
                time.sleep(1/self.time_scale)
            except socket.error as e:
                print(str(e))
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
            print('send')
        self.track_media()
    
    def save_file(self):
        for point in self.stream_data:
            for i in point:
                self.buffer_data.write(str(i)+',')
            self.buffer_data.write('\n')

    def reset(self):
        """Return initial state"""
        self.prev_buf = 0
        self.t_last = 0
        self.seg_num = 0
        self.flg_finish_download = 0
        self.quali_req = '_240p'
        self.stream_data = [[0,0,0,self.bandwidth,self.quali_req]]
        self.bandwidth = self.sigma*np.random.randn()+ self.start_bandwidth * self.time_scale
        return np.array([0,0,self.max_buf, self.bandwidth, 0])
        

    def calc_reward(self,action):
        """Calculate the reward for the last time step"""
        if self.prev_buf == 0 and self.seg_num != 0 and self.flg_finish_download != 1:
            return -50.0
        return min(0, self.prev_buf-self.max_buf)+(action-len(self.reprs)+1)

    def is_done(self):
        """Checks if client is done"""
        if self.flg_finish_download == 1 and self.prev_buf == 0:
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
            print('step')
        new_chunk= str(self.response.decode('utf-8')).split(',')
        self.debug_prints()
        if self.flg_finish_download == 1:                                                          
            self.save_data_point('-1,-1,-1')
        else:
            self.save_data_point(self.response.decode('utf-8'))
        if self.flg_finish_download == 1 and self.prev_buf == 0:
            print('Disconnecting from server...')
            #self.disconnect_client()
        self.time_step(float(new_chunk[2]))
        reward = self.calc_reward(action)
        done = self.is_done()
        info = {}
        new_state = np.array([self.prev_buf,float(new_chunk[1]),self.max_buf, self.bandwidth, self.reprs.index(self.quali_req)])
        return new_state,reward,done,info

    def disconnect_client(self):
        """Disconnect from server"""
        self.socket.close()
        self.connected = False

    def reset_client(self):
        """Reset client when reconnecting"""
        self.prev_buf = 0
        self.t_last = 0
        self.seg_num = 0
        self.flg_finish_download = 0
        self.quali_req = '_240p'
        
