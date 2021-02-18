import os
import math

path = 'full_sweep_results/'
fileList = os.listdir(path)
f = fileList[0]
header = ""
with open(path+f, 'r') as fi:
	header = fi.readline()
all_results = [header]
accs = []
for f in fileList:
	with open(path+f, 'r') as fi:
		info = fi.readlines()[1]
		info = info.split(', ')
		info[7] = info[7].split('\n')[0]
		accs.append(float(info[1]))
		all_results.append(info)
print("Average acc: " + str(sum(accs)/len(accs)))
print("Max acc: " + str(max(accs)))	
