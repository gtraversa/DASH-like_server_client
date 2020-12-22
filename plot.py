import matplotlib.pyplot as plt
import matplotlib.style as style
style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
graph_data = open('1_buffer.txt','r').read()
lines = graph_data.split('\n')
ts = []
bufs = []

for line in lines:
    if len(line) > 1:
        t, buf = line.split(',')
        ts.append(float(t))
        bufs.append(float(buf))

ax1.plot(ts,bufs)
ax1.set_xlabel('Simulation time')
ax1.set_ylabel('Buffer health')
plt.show()
