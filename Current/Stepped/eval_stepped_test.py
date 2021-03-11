import stepped_DASH_client as client
from stable_baselines3 import DQN
import numpy as np
import matplotlib.pyplot as plt
import time
from os import listdir


runs = 1000

def setup_method_eval():
    start_time = time.time()
    bands = [x for x in range(1,400,2)]
    methods = ['rl','heuristic']
    results = []
    model = DQN.load('/Users/gianlucatraversa/Desktop/UNI Y3/Dissertation/Server-client/models/uniform_training_new_reward_slow1/best_model')
    for i,method in enumerate(methods):
        rewards,actions=evaluate(bands,method,method_n = i, tot_methods = len(methods),start_time=start_time,model = model)
        results.append((rewards,actions))
    plot_results_methods(bands,results = results,methods = methods)

def setup_parameter_eval(models):
    start_time = time.time()
    
    bands = [x for x in range(1,400,2)]
    results = []
    for i,model in enumerate(models):
        loaded_model =  DQN.load("/Users/gianlucatraversa/Desktop/UNI Y3/Dissertation/Server-client/models/{}/best_model".format(model))
        rewards,actions=evaluate(bands,method='rl',method_n = i, tot_methods = len(models),start_time=start_time,model = loaded_model)
        results.append((rewards,actions))
    plot_results_params(bands,results = results,params = models)

def evaluate(bands,method,method_n,tot_methods,start_time,model):
    mean_rewards = []
    mean_actions = []
    for i,band in enumerate(bands):
        #TODO: print progress
        print('{0:.0f}/{1:.0f} methods, Method: {2} {3:.2%} done, Time elapsed: {4:.2f}s'.format(method_n+1,tot_methods,method,(i+1)/len(bands),time.time()-start_time))
        env = client.Client(bandwidth = band,sigma = 0,method = method)
        obs = env.reset()
        rewards = []
        actions = []
        observations = []

        for i in range(runs):
            action= predict_action(method = method,obs=obs,env = env,model=model)
            obs, reward, done, info = env.step(action)
            observations.append(obs)
            rewards.append(reward)
            actions.append(action)
            if done:
                env.reset()
        env.disconnect_client()
        mean_rewards.append(np.mean(rewards))
        mean_actions.append(np.mean(actions))
    return mean_rewards, mean_actions

def plot_results_methods(bands,results, methods):
    fig, (ax1,ax2) = plt.subplots(2)
    fig.suptitle('Runs: {}, Methods: {}'.format(runs, methods))
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
    fig.suptitle('Runs: {}'.format(runs))
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
    
    if method == 'rl':
        action, _states = model.predict(obs, deterministic = True)
        return action
    else:
        action = env.quali_select()
        return int(action)


def get_models(dir_name):
    return [f for f in listdir(dir_name) if f.startswith('uniform_training')]


models = get_models('/Users/gianlucatraversa/Desktop/UNI Y3/Dissertation/Server-client/models')
#models = ['uniform_training_200_chunks_fast1','uniform_training_added_reprs1','uniform_training_200_chunks_ltd_range1','uniform_training_200_chunks_slow_train1']
setup_parameter_eval(models)
#setup_method_eval()