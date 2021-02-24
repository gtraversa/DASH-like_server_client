import matplotlib.pyplot as plt
from os import listdir



def list_of_files(dir_name):
    return (f for f in listdir(dir_name) if f.endswith('.' + "txt"))

def plot(f_name,i):
    fig, (ax1,ax2,ax3,ax4) = plt.subplots(4,num=i)
    graph_data = open(f_name,'r').read()
    lines = graph_data.split('\n')
    ts = []
    bufs = []
    chunks = []
    estimated_bandwidth = []
    qualis = []
    quali_vals = {
        '_240p': 240,
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
            est_band= data_arr[3]
            quali = data_arr[4]
            ts.append(float(t))
            bufs.append(float(buf))
            chunks.append(float(chunk))
            estimated_bandwidth.append(float(est_band))
            qualis.append(quali_vals[quali])

    params = f_name.split('_')
    fig.suptitle('Bandwidth: {}, Req timer: {}, Max buffer: {}, Optimization: {}, Episodes: {}'.format(params[0],params[1],params[2],params[3],params[5]))

    ax1.plot(ts,bufs,color = 'tab:red')
    ax1.set_ylabel('Buffer health (s)',fontsize = 10)
    ax1.tick_params(axis='y', labelcolor= 'tab:red')
    ax1.grid(color = 'gray', linestyle = ':',which= 'both')

    ax2.plot(ts,chunks,color = 'tab:blue')
    ax2.set_ylabel('Chunk sizes (MBit)',fontsize = 10)
    ax2.tick_params(axis='y', labelcolor= 'tab:blue')
    ax2.grid(color = 'gray', linestyle = ':',which= 'both')

    ax3.plot(ts,estimated_bandwidth,color = 'tab:green')
    ax3.set_ylabel('Est. Bandwidth (MBit/s)',fontsize = 10)
    ax3.tick_params(axis='y', labelcolor= 'tab:green')
    ax3.set_xlabel('Simulation time (s)')
    ax3.grid(color = 'gray', linestyle = ':',which= 'both')

    ax4.plot(ts,qualis,color = 'tab:purple')
    ax4.set_ylabel('Quality requested',fontsize = 10)
    ax4.tick_params(axis='y', labelcolor= 'tab:purple')
    ax4.set_xlabel('Simulation time (s)')
    ax4.grid(color = 'gray', linestyle = ':',which= 'both')
    fig.tight_layout()

logs = list_of_files('/Users/gianlucatraversa/Desktop/UNI Y3/Dissertation/Server-client')
for i,log in enumerate(logs):
    plot(log,i)
plt.show()
