import DASH_client as client
from _thread import start_new_thread
from time import sleep


global num_clients
bands = [100,100,100,100,100]
timers = [0.3,0.3,0.3,0.3,0.3]
max_buffers = [10,10,10,10,10]
method = ['rl','heuristic', 'MAX','naive',None ]
clients=[]
client_params = zip(bands,timers,max_buffers,method)

for band, timer, max_buf,method in client_params:
    clients.append(client.Client(bandwidth = band, timer = timer, max_buf = max_buf, method = method))
num_clients = len(clients)

def start_client_process(client,i):
    """Begin new process for each client so that they can run in parallel"""
    global num_clients
    print('Client: {} created'.format(i+1))
    client.toString()
    print('\n')
    client.start_request()
    num_clients-=1

for i, client in enumerate(clients):
    start_new_thread(start_client_process,(client,i,))
    sleep(1)

while 1:
    if not num_clients:
        break


