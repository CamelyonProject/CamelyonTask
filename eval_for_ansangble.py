from __future__ import print_function

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.backends.cudnn as cudnn

import torchvision
import torchvision.transforms as transforms
import torchvision.datasets as datasets
import os
import argparse

from models import *
from utils import progress_bar
from torch.autograd import Variable

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import pylab

from load_dataset import get_test_dataset
from load_dataset import get_val_dataset

import csv
from user_define import Config as cp

use_cuda = torch.cuda.is_available()

threshold = 0.1
batch_size = 100
tumor_list = []
labeling = []


f = open(cp.path_for_generated_image + "/result.csv",
         'w', encoding='utf-8', newline='')
wr = csv.writer(f)


def makecsv(output, label, size):
    for i in range(size):
        # if output[i] == 1 :
        #    print(label[i])
        wr.writerow([label[i], output[i]])


print('==> Preparing data..')
transform_test = transforms.Compose([
    transforms.ToTensor(),
])

testset = get_test_dataset(transform_test, transform_test)
testloader = torch.utils.data.DataLoader(
    testset, batch_size, shuffle=False, num_workers=16)

print('==>Resuming from checkpoint..')
checkpoint = torch.load('./checkpoint/ckpt.pth.tar')
# print(checkpoint)
net1 = checkpoint['net1']
net2 = checkpoint['net2']
net3 = checkpoint['net3']

if use_cuda:
    net1.cuda()
    net2.cuda()
    net3.cuda()
    net1 = torch.nn.DataParallel(
        net1, device_ids=range(torch.cuda.device_count()))
    net2 = torch.nn.DataParallel(
        net2, device_ids=range(torch.cuda.device_count()))
    net3 = torch.nn.DataParallel(
        net3, device_ids=range(torch.cuda.device_count()))
    cudnn.benchmark = True


net1.eval()
net2.eval()
net3.eval()

for batch_idx, (inputs, label) in enumerate(testloader):
    # print(label)
    # print(label.shape)

    if use_cuda:
        inputs = inputs.type(torch.cuda.FloatTensor)
        inputs = inputs.cuda()
    inputs = Variable(inputs, volatile=True)
    outputs1 = net1(inputs)
    outputs1 = net2(inputs)
    outputs1 = net3(inputs)
    outputs = 0.33 * outputs1 + 0.33 * outputs2 + 0.34 * outputs3
    outputs = torch.squeeze(outputs)
    thresholding = torch.ones(inputs.size(0)) * (1 - threshold)
    # print(outputs)
    outputs = outputs + Variable(thresholding.cuda())
    outputs = torch.floor(outputs)
    outputs_cpu = outputs.data.cpu()

    makecsv(outputs_cpu, label, inputs.size(0))

f.close()
print("end")