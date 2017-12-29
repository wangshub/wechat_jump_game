#encoding:utf-8
#黄色检测
import numpy as np
import argparse
import cv2
import scipy.misc
import matplotlib.pyplot as plt
from PIL import Image

raw = np.array(Image.open('1.png'))
raw_r = np.mat(raw[:, :, 0])

print raw_r.shape


# plt.imshow(raw_r)

label1=0
label1val=0
label1num=0
label1min=0
label1max=0
currentPIXval=0

for i in range(720, 1000):
    label1=0 
    label2=0 
    label3=0 
    label4=0 

    label1val=0 
    label2val=0 
    label3val=0 
    label4val=0 
    
    label1min=0 
    label1max=0 
    
    findmaxflag=1 

    for j in range(1080):
        cur = raw_r[i,j]
        if cur>(label1val-15) and cur<(label1val+15):
            label1=label1+1
            if(findmaxflag):
                if(j-label1min>10):
                    label1max=j
                    findmaxflag=0;
                else:
                    label1min=j
        if(label1val==0):
            label1val=cur
            continue;
        continue;

    if (abs(label1max-label1min)<1080):
        if( label1max-label1min <= label1num and label1max-label1min>20 ):

            print 'cor = ', (label1max+label1min)/2, i
            
            break
        label1num=label1max-label1min;




