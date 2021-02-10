import DASH_client as client
#import multithread_server as Server
from multiprocessing import Process
from _thread import start_new_thread
from time import sleep
import plot

bands = [200,100,300,500,175]
timers = [0.3,0.3,0.7,0.3,0.3]
max_buffers = [10,10,10,10,10]
clients=[]
client_params = zip(bands,timers,max_buffers)
num_clients = len(clients)
for band, timer, max_buf in client_params:
    clients.append(client.Client(bandwidth = band, timer = timer, max_buf = max_buf))


def start_client_process(client,i):
    """Begin new process for each client so that they can run in parallel"""
    print('Client: {} created'.format(i+1))
    client.toString()
    print('\n')
    client.start_request()
    print('{}_{}_{}_buffer.txt'.format(bands[i],timers[i],max_buffers[i]))
    #plot.plot('{}_{}_{}_buffer.txt'.format(bands[i],timers[i],max_buffers[i]))


for i, client in enumerate(clients):
    start_new_thread(start_client_process,(client,i,))
    sleep(0.5)

while 1: pass