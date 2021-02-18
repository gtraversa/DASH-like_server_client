from stable_baselines3.common.env_checker import check_env
import stepped_DASH_client as client
from stable_baselines3 import DQN
from stable_baselines3.common.evaluation import evaluate_policy

env = client.Client()
#check_env(env)

# Instantiate the agent
# model = DQN('MlpPolicy', env, learning_rate=1e-3)
# # Train the agent
# model.learn(total_timesteps=int(1e4))
# # Save the agent
# model.save("test_1_1e-3_1e4")

# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)
# print(mean_reward)
model = DQN.load("test_1_1e-3_1e5")
# Enjoy trained agent
obs = env.reset()
for i in range(100):
    action, _states = model.predict(obs, deterministic = True)
    obs, rewards, dones, info = env.step(action)
    