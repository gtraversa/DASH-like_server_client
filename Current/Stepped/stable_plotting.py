import os

import gym
import numpy as np
import matplotlib.pyplot as plt
import time

import stepped_DASH_client as client

from stable_baselines3 import DQN
from stable_baselines3.common import results_plotter
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import load_results, ts2xy,plot_results
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.callbacks import BaseCallback


class SaveOnBestTrainingRewardCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every ``check_freq`` steps)
    based on the training reward (in practice, we recommend using ``EvalCallback``).

    :param check_freq: (int)
    :param log_dir: (str) Path to the folder where the model will be saved.
      It must contains the file created by the ``Monitor`` wrapper.
    :param verbose: (int)
    """
    def __init__(self, check_freq: int, log_dir: str, verbose=1, total_time_steps = 1):
        super(SaveOnBestTrainingRewardCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.log_dir = log_dir
        self.save_path = os.path.join(log_dir, 'best_model')
        self.best_mean_reward = -np.inf
        self.total_time_steps = total_time_steps
        self.start_time = time.time()

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.num_timesteps % (self.check_freq*10) == 0:
          if self.verbose >0:
              print('{0:.0f}/{1:.0f} training steps, {2:.2%} done, Time elapsed: {3:.2f}s'.format(self.num_timesteps,self.total_time_steps,self.num_timesteps/self.total_time_steps,time.time()-self.start_time))
        if self.n_calls % self.check_freq == 0:
          # Retrieve training reward
          x, y = ts2xy(load_results(self.log_dir), 'timesteps')
          if len(x) > 0:
              # Mean training reward over the last 100 episodes
              mean_reward = np.mean(y[-100:])
              if self.verbose > 1:
                print("Num timesteps: {}".format(self.num_timesteps))
                print("Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(self.best_mean_reward, mean_reward))

              # New best model, you could save the agent here
              if mean_reward > self.best_mean_reward:
                  self.best_mean_reward = mean_reward
                  # Example for saving best model
                  if self.verbose > 2:
                    print("Saving new best model to {}".format(self.save_path))
                  self.model.save(self.save_path)

        return True

# Create log dir
quali_params = [0,0.3,0.5,0.7,1,1.3,1.5]
#rates = [1e-5,1e-4,5e-4,1e-3,5e-3,1e-2]
for param in quali_params:
  log_dir = "models/uniform_training_new_reward_positive_{}".format(param)
  os.makedirs(log_dir, exist_ok=True)

  # Create and wrap the environment
  env = client.Client(training = True, min_train = 1, max_train = 400, quali_param = param)
  env = Monitor(env, log_dir)
  model = DQN('MlpPolicy', env, verbose=0,learning_rate = 1e-4)
  #model = DQN.load('/Users/gianlucatraversa/Desktop/UNI Y3/Dissertation/Server-client/models/uniform_training_200_chunks_ltd_range1/best_model',env = env)
  # Create the callback: check every 1000 steps
  # Train the agent
  time_steps = 5e5
  callback = SaveOnBestTrainingRewardCallback(check_freq=1000, log_dir=log_dir,verbose = 2, total_time_steps=int(time_steps))

  model.learn(total_timesteps=int(time_steps), callback=callback)
  #model.save("bandwidth = uniform(30,200)_learning_rate = 2.5e-3_time_steps = 2e5")
  plot_results([log_dir], time_steps, results_plotter.X_TIMESTEPS, "Learning rate study",label = str(param))
  plt.legend()
  plt.savefig('learning_curve.png')
  env.disconnect_client()
plt.show()