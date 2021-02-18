import stepped_DASH_client as client
from _thread import start_new_thread
from time import sleep
cli = client.Client(bandwidth = 30, time_scale = 1,quali_req = '_1080p')

try:
    cli.connect()
except Exception as e:
    print(e)
done = False
qualis = cli.reprs

action = '_480p'
while not done:
    new_state,reward,done,info = cli.step(action)
cli.save_file()
cli.disconnect_client()
