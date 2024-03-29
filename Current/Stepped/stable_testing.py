from stable_baselines3.common.env_checker import check_env
import stepped_DASH_client as client
from stable_baselines3 import DQN
from stable_baselines3.common.evaluation import evaluate_policy

env = client.Client()
#check_env(env)


# model = DQN('MlpPolicy', env, learning_rate=1e-3)
# # Train the agent
# model.learn(total_timesteps=int(1e4))
# # Save the agent
# env.save_file()
# model.save("test_1_1e-3_1e4_buf_reward")

# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)
# print(mean_reward)
model = DQN.load("plotting_test-1/best_model")
# Enjoy trained agent
obs = env.reset()
for i in range(100):
    action, _states = model.predict(obs, deterministic = True)
    obs, rewards, dones, info = env.step(action)
