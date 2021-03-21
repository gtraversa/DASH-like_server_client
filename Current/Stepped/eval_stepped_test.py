import stepped_DASH_client as client
from stable_baselines3 import DQN
import numpy as np
import matplotlib.pyplot as plt
import time
from os import listdir


RUNS = 1000                                 #Steps for each tested bandwidth

def setup_method_eval():
    """Evaluate different methods with a constant RL model"""
    start_time = time.time()
    bands = [x for x in range(1,400,2)]
    methods = ['rl','heuristic','MAX']
    results = []
    model = DQN.load('/Users/gianlucatraversa/Desktop/UNI Y3/Dissertation/Server-client/models/uniform_training_gamma_expl_0.25/best_model')
    for i,method in enumerate(methods):
        rewards,actions=evaluate(bands,method,method_n = i, tot_methods = len(methods),start_time=start_time,model = model)
        results.append((rewards,actions))
    plot_results_methods(bands,results = results,methods = methods)

def setup_parameter_eval(models):
    """Evaluate different RL models against each other"""
    start_time = time.time()                    #For progress logging
    bands = [x for x in range(1,400,20)]         #Generate array of bandwidths to test
    results = []
    for i,model in enumerate(models):
        loaded_model =  DQN.load("/Users/gianlucatraversa/Desktop/UNI Y3/Dissertation/Server-client/models/{}/best_model".format(model))    #Load model to be tested
        rewards,actions=evaluate(bands,method='rl',method_n = i, tot_methods = len(models),start_time=start_time,model = loaded_model)
        results.append((rewards,actions))
    plot_results_params(bands,results = results,params = models)

def evaluate(bands,method,method_n,tot_methods,start_time,model):
    """Evaluate agent on given range of bandwidths"""
    mean_rewards = []
    mean_actions = []
    for i,band in enumerate(bands):
        print('{0:.0f}/{1:.0f} methods, Method: {2} {3:.2%} done, Time elapsed: {4:.2f}s'.format(method_n+1,tot_methods,method,(i+1)/len(bands),time.time()-start_time)) #Print progress
        env = client.Client(bandwidth = band,sigma = 0,method = method)         #Create environment to be tested
        obs = env.reset()
        rewards = []
        actions = []
        observations = []

        for i in range(RUNS):               #Simulate RUNS steps of the given client and log data for analysis
            action= predict_action(method = method,obs=obs,env = env,model=model)   #Get the next action the agent should take
            obs, reward, done, info = env.step(action)
            observations.append(obs)
            rewards.append(reward)
            actions.append(action)
            if done:
                env.reset()
        env.disconnect_client()             #Client disconnects to not overload server with limited bandwidth
        mean_rewards.append(np.mean(rewards))
        mean_actions.append(np.mean(actions))
    return mean_rewards, mean_actions

def plot_results_methods(bands,results, methods):
    fig, (ax1,ax2) = plt.subplots(2)
    fig.suptitle('Runs: {}, Methods: {}'.format(RUNS, methods))
    i=0
    for mean_rewards,mean_actions in results:
        ax1.plot(bands,mean_rewards,label = methods[i])
        ax2.plot(bands,mean_actions,label = methods[i])
        i+=1

    ax1.set_ylabel('Mean reward',fontsize = 10)
    ax1.set_xlabel('Mean bandwidth (MB)',fontsize = 10)
    ax1.tick_params(axis='y', labelcolor= 'tab:red')
    ax1.grid(color = 'gray', linestyle = ':',which= 'both')

    
    ax2.set_ylabel('Mean action',fontsize = 10)
    ax2.set_xlabel('Mean bandwidth (MB)',fontsize = 10)
    ax2.tick_params(axis='y', labelcolor= 'tab:blue')
    ax2.grid(color = 'gray', linestyle = ':',which= 'both')

    fig.tight_layout()
    plt.legend()
    plt.show()
    
def plot_results_params(bands,results, params):
    fig, (ax1,ax2) = plt.subplots(2)
    fig.suptitle('Runs: {}'.format(RUNS))
    i=0
    for mean_rewards,mean_actions in results:
        ax1.plot(bands,mean_rewards,label = str(params[i]))
        ax2.plot(bands,mean_actions,label = str(params[i]))
        i+=1

    ax1.set_ylabel('Mean reward',fontsize = 10)
    ax1.set_xlabel('Mean bandwidth (MB)',fontsize = 10)
    ax1.tick_params(axis='y', labelcolor= 'tab:red')
    ax1.grid(color = 'gray', linestyle = ':',which= 'both')

    
    ax2.set_ylabel('Mean action',fontsize = 10)
    ax2.set_xlabel('Mean bandwidth (MB)',fontsize = 10)
    ax2.tick_params(axis='y', labelcolor= 'tab:blue')
    ax2.grid(color = 'gray', linestyle = ':',which= 'both')

    fig.tight_layout()
    plt.legend()
    plt.show()


def predict_action(method,obs,env,model):
    """Returns next actin for the agent given a method and/or a model"""
    if method == 'rl':
        action, _states = model.predict(obs, deterministic = True)
        return action
    else:
        action = env.quali_select()             #Predicts the action with the internal methods of the client
        return int(action)


def get_models(dir_name):
    """Gets all model directories in the specified directory"""
    return [f for f in listdir(dir_name) if f.startswith('uniform_training')]


models = get_models('/Users/gianlucatraversa/Desktop/UNI Y3/Dissertation/Server-client/models')
#models = ['uniform_training_200_chunks_fast1','uniform_training_added_reprs1','uniform_training_200_chunks_ltd_range1','uniform_training_200_chunks_slow_train1']
setup_parameter_eval(models)
#setup_method_eval()