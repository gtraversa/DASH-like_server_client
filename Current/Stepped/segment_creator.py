import numpy as np
from noise import pnoise1 as perl
import matplotlib.pyplot as plt
#print(np.random.normal(150*1.2*1.2*1.2,50,size=(1,12)))

sizes_pixels = [240*325,360*480,480*858,720*1280,1080*1920]
for i,size in enumerate(sizes_pixels):
    if i != 0: print(size/sizes_pixels[i-1])

scale_factor = 2.25
num_reprs = 4
num_chunks = 12
min_mean_size = 50

chunk_arrays = []
def normal_dist_chunks(scale_factor,num_chunks,num_reprs,min_mean_size):
    for i in range(num_reprs):
        st_dev = 0.1*min_mean_size
        new_repr = ''
        for j in range(num_chunks):
            new_repr+='{:.2f}'.format(np.random.normal(min_mean_size,st_dev))
            new_repr+=','
        new_repr+=str(-1)
        chunk_arrays.append(new_repr)
        min_mean_size*=scale_factor
    print(chunk_arrays)

def perlin_generated_chunks(scale_factor,num_chunks,num_reprs,min_mean_size):
    val = 0
    for i in range(num_reprs):
        dev = 0.3*min_mean_size
        new_repr = ''
        noises = []
        for j in range(num_chunks):
            noise = perl(x = (j-(num_chunks/2))*0.3,octaves = 5)
            noises.append(noise)
            new_size = noise*dev + min_mean_size
            new_repr+='{:.2f}'.format(new_size)
            new_repr+=','
        new_repr+='-1'
        chunk_arrays.append(new_repr)
        min_mean_size*=scale_factor
    print(chunk_arrays)
    print(noises)
    return noises

noises = perlin_generated_chunks(scale_factor = 2.25,num_reprs = 4,num_chunks = 12,min_mean_size = 50)
plt.plot(noises)
plt.show()