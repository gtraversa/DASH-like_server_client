import numpy as np
from noise import pnoise1 as perl
import matplotlib.pyplot as plt
#print(np.random.normal(150*1.2*1.2*1.2,50,size=(1,12)))

# sizes_pixels = [240*325,360*480,480*858,720*1280,1080*1920]
# for i,size in enumerate(sizes_pixels):
#     if i != 0: print(size/sizes_pixels[i-1])

SCALE_FACTOR = 2.25     #Ratio between codec size
NUM_REPRS = 5           #Number of codecs
NUM_CHUNKS = 12         #Number of chunks per media file
MIN_MEAN_SIZE = 25      #Smallest mean chunk size for lowest codec

chunk_arrays = []
def normal_dist_chunks(scale_factor,NUM_CHUNKS,NUM_REPRS,MIN_MEAN_SIZE):
    """Generates arrays of normally distributed chunks"""
    for i in range(NUM_REPRS):
        st_dev = 0.1*MIN_MEAN_SIZE          #Arbitrary standard deviation proportional to mean size
        new_repr = ''
        for j in range(NUM_CHUNKS):
            new_repr+='{:.2f}'.format(np.random.normal(MIN_MEAN_SIZE,st_dev))
            new_repr+=','
        new_repr+=str(-1)                   #Add stop condition for client
        chunk_arrays.append(new_repr)
        MIN_MEAN_SIZE*=scale_factor         #Increase mean for next codec
    print(chunk_arrays)

def perlin_generated_chunks(scale_factor,NUM_CHUNKS,NUM_REPRS,MIN_MEAN_SIZE):
    """Generates arrays of chunks according to 1D perlin noise function adding time correlation"""
    for i in range(NUM_REPRS):
        print(MIN_MEAN_SIZE)
        dev = 0.3*MIN_MEAN_SIZE             #Arbitrary deviation to scale noise (-1,1) proportional to mean size
        new_repr = ''
        noises = []
        for j in range(NUM_CHUNKS):
            noise = perl(x = (j-(NUM_CHUNKS/2))*0.05,octaves = 2)
            noises.append(noise)
            new_size = noise*dev + MIN_MEAN_SIZE
            new_repr+='{:.2f}'.format(new_size)
            new_repr+=','
        new_repr+='-1'                      #Add stop condition for client
        chunk_arrays.append(new_repr)
        MIN_MEAN_SIZE*=scale_factor         #Increase mean for next codec
    print(chunk_arrays)
    return noises                           #Return to plot and tine perlin noise parameters

noises = perlin_generated_chunks(scale_factor = 2.25,NUM_REPRS = 5,NUM_CHUNKS = 200,MIN_MEAN_SIZE = 25)
plt.plot(noises)
plt.show()