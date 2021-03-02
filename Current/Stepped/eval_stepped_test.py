import stepped_DASH_client as client
from stable_baselines3 import DQN
import numpy as np
import matplotlib.pyplot as plt

model = DQN.load("/Users/gianlucatraversa/Desktop/UNI Y3/Dissertation/Server-client/plotting_test-1/new_reward/best_model.zip")
runs = 100





def setup():
    bands = [x for x in range(1,50,10)]
    methods = ['rl', 'MAX','naive','heuristic']
    for method in methods:
        rewards,actions=evaluate(bands,method)
        plot_results(bands, mean_rewards=rewards, mean_actions = actions,method = method)
    plt.show()

def evaluate(bands,method):
    mean_rewards = []
    mean_actions = []
    for band in bands:
        env = client.Client(bandwidth = band,sigma = 0,method = method)
        obs = env.reset()
        rewards = []
        actions = []
        observations = []

        for i in range(runs):
            action= predict_action(method = method,obs=obs,env=env)
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

def plot_results(bands,mean_rewards,mean_actions, method):
    fig, (ax1,ax2) = plt.subplots(2)
    fig.suptitle('Runs: {}, Method: {}'.format(runs, method))

    ax1.plot(bands,mean_rewards,color = 'tab:red')
    ax1.set_ylabel('Mean reward',fontsize = 10)
    ax1.set_xlabel('Mean bandwidth (MB)',fontsize = 10)
    ax1.tick_params(axis='y', labelcolor= 'tab:red')
    ax1.grid(color = 'gray', linestyle = ':',which= 'both')

    ax2.plot(bands,mean_actions,color = 'tab:blue')
    ax2.set_ylabel('Mean action',fontsize = 10)
    ax2.set_xlabel('Mean bandwidth (MB)',fontsize = 10)
    ax2.tick_params(axis='y', labelcolor= 'tab:blue')
    ax2.grid(color = 'gray', linestyle = ':',which= 'both')

    fig.tight_layout()
    

def predict_action(method,obs,env):
    if method == 'rl':
        action, _states = model.predict(obs, deterministic = True)
        return action
    else:
        action = env.quali_select()
        return int(action)-1

setup()
#TODO: error is in naive and heuristic functions when they throw exception