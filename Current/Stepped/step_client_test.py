import stepped_DASH_client as client
from _thread import start_new_thread
from time import sleep
#import stepped_plot as plot_data
from stable_baselines3 import DQN
import numpy as np


global num_clients
num_clients = 0
model = DQN.load('/Users/gianlucatraversa/Desktop/UNI Y3/Dissertation/Server-client/models/uniform_training_gamma_expl_0.25/best_model')

def make_clients(bands,methods):
    """Create array of clients with specified methods"""
    client_params = zip(bands,methods)
    clients=[]
    for band,method in client_params:
        clients.append(client.Client(method = method, bandwidth = band, sigma = 0.1*band))
    
    num_clients=len(clients)
    return clients

def operate_client(client):
    """Given a client will step through an episode and log data from client cache when episode terminates"""
    global num_clients
    done = False
    obs = client.reset()
    method = client.method
    while not done:
        action= predict_action(method = method,obs=obs,cli = client)
        obs, reward, done, info = client.step(action)
        if client.seg_num%20 == 0:
            client.bandwidth = np.random.choice([20,50,75,100,12,150])
    print('saving client')
    client.save_file()
    client.disconnect_client()
    num_clients-=1


def start_simulation():
    #bands = [100,100,100,100,100]
    bands = [100]
    methods = ['rl','heuristic', 'MAX','naive',None ]
    methods = ['rl']
    clients = make_clients(bands = bands, methods = methods)
    for client in clients:
        start_new_thread(operate_client,(client,))
        sleep(0.1)

def predict_action(method,obs,cli):
    """Predicts the next action for the agent given a method and/or a model"""
    if method == 'rl':
        action, _states = model.predict(obs, deterministic = True)
        return action
    else:
        action = cli.quali_select()
        return int(action)


start_simulation()

while 1:                    #Keeps program running until all threaded clients are done
    if not num_clients:
        sleep(3)
        break
