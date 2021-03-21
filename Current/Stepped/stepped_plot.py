import matplotlib.pyplot as plt
from os import listdir
import pandas as pd



def list_of_files(dir_name):
    return (f for f in listdir(dir_name) if f.endswith('.' + "txt"))

def plot(f_name,i):
    fig, (ax1,ax2,ax4,ax5) = plt.subplots(4,num=i)
    graph_data = open(f_name,'r').read()
    lines = graph_data.split('\n')
    ts = []
    bufs = []
    chunks = []
    qualis = []
    bands = []
    quali_vals = {
        '_240p': 240,
        '_360p': 360,
        '_480p': 480,
        '_720p': 720,
        '_1080p': 1080,
    }

    for line in lines:
        data_arr = line.split(',')
        if len(data_arr) > 4:
            t = data_arr[0]
            buf = data_arr[1]
            chunk = data_arr[2]
            quali = data_arr[3]
            band = data_arr[5]
            ts.append(float(t))
            bufs.append(float(buf))
            chunks.append(float(chunk))
            qualis.append(quali_vals[quali])
            bands.append(float(band))

    params = f_name.split('_')
    fig.suptitle('Bandwidth: {}, Req timer: {}, Max buffer: {}, Optimization: {}, Episodes: {}'.format(params[0],params[1],params[2],params[3],params[4]))


    quali_series = pd.Series(qualis)
    rolling_window_obj = quali_series.rolling(20)
    rolling_average = rolling_window_obj.mean()

    ax1.plot(ts,bufs,color = (0.169,0.627,0.176))
    ax1.set_ylabel('Buffer health (s)',fontsize = 10)
    ax1.tick_params(axis='y', labelcolor= (0.169,0.627,0.176))
    ax1.grid(color = 'gray', linestyle = ':',which= 'both')

    ax2.plot(ts,chunks,color = (0.125,0.537,0.619))
    ax2.set_ylabel('Chunk sizes (MB)',fontsize = 10)
    ax2.tick_params(axis='y', labelcolor= (0.125,0.537,0.619))
    ax2.grid(color = 'gray', linestyle = ':',which= 'both')

    ax4.plot(ts,rolling_average,color = (0.906,0.463,0.))
    ax4.set_ylabel('Quality requested',fontsize = 10)
    ax4.tick_params(axis='y', labelcolor= (0.906,0.463,0.))
    ax4.set_xlabel('Simulation time (s)')
    ax4.grid(color = 'gray', linestyle = ':',which= 'both')

    ax5.plot(ts,bands,color = (0.384,0.125,0.522))
    ax5.set_ylabel('Client bandwidth (MB)',fontsize = 10)
    ax5.tick_params(axis='y', labelcolor= (0.384,0.125,0.522))
    ax5.set_xlabel('Simulation time (s)')
    ax5.grid(color = 'gray', linestyle = ':',which= 'both')

    fig.tight_layout()


logs = list_of_files('/Users/gianlucatraversa/Desktop/UNI Y3/Dissertation/Server-client')
for i,log in enumerate(logs):
    plot(log,i)
plt.show()
