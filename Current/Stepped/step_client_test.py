import stepped_DASH_client as client
from _thread import start_new_thread
from time import sleep
cli = client.Client(bandwidth = 10, time_scale = 1,quali_req = '_240p',sigma = 3)

done = False
qualis = cli.reprs

action = 1
while not done:
    new_state,reward,done,info = cli.step(action)
    print(reward)
cli.save_file()
cli.disconnect_client()
