import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax2 = ax1.twinx() 
graph_data = open('300_0.1_10_buffer.txt','r').read()
lines = graph_data.split('\n')
ts = []
bufs = []
chunks = []

for line in lines:
    if len(line) > 1:
        t, buf,chunk = line.split(',')
        ts.append(float(t))
        bufs.append(float(buf))
        chunks.append(int(chunk))

ax1.plot(ts,bufs,color = 'tab:red')
ax1.set_xlabel('Simulation time (s)')
ax1.set_ylabel('Buffer health (s)')
ax1.tick_params(axis='y', labelcolor= 'tab:red')
ax2.plot(ts,chunks,color = 'tab:blue')
ax2.set_ylabel('Chunk sizes (MBit)')
ax2.tick_params(axis='y', labelcolor= 'tab:blue')
fig.tight_layout()
plt.show()
