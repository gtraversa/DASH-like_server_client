from stable_baselines3.common.env_checker import check_env
import stepped_DASH_client as client

env = client.Client()

check_env(env)

