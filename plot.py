import matplotlib.pyplot as plt



def plot():
    fig, (ax1,ax2,ax3) = plt.subplots(3)

    graph_data = open('100_0.3_10_buffer.txt','r').read()
    lines = graph_data.split('\n')
    lines.pop(-1)
    ts = []
    bufs = []
    chunks = []
    estimated_bandwidth = []

    for line in lines:
        if len(line) > 1:
            data_arr = line.split(',')
            t = data_arr[0]
            buf = data_arr[1]
            chunk = data_arr[2]
            est_band= data_arr[3]
            ts.append(float(t))
            bufs.append(float(buf))
            chunks.append(int(chunk))
            estimated_bandwidth.append(float(est_band))
        

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
    fig.tight_layout()
    plt.show()

plot()