from ast import If, expr_context
from email import header
from glob import glob
import numpy as np
import os
import sys 
import pandas as pd


def readDataIn(inPath):
    #with open(inPath, 'r', encoding='utf-16-le') as f:
    #    df = pd.read_csv(f, delimiter=" ", header=1)
    #df = pd.read_csv(inPath, delimiter=" ", header=1)

    with open(inPath, 'r') as f:
        data = f.readlines()
    
    header = [data[0]]
    data = data[1:]
    
    return header, data

def reduceData(data, N):
    data_buff = []
    real_len = len(data)
    iter_step = int(real_len/N)
    cnt = 0

    for d in data:
        if cnt < iter_step:
            cnt = cnt + 1
        else:
            data_buff.append(d)
            cnt = 1        
    
    return data_buff

def saveData(path_, data_):
    f  = open(path_, "w")
    f.write(data_)
    f.close()

def main():

    args = sys.argv
    if len(args) < 2:
        print("usage py3 <program> [input File].txt [output Path]")
        sys.exit()
    elif len(args) == 2:
        if_path = args[1]
        of_path = args[1]

        of_path = " ".join(if_path.split(".txt")[0:-1]) + "_red.txt"
    else:
        if_path = args[1]
        of_path = args[2]

    N = 1000 #amount of datapoints

    header, data = readDataIn(if_path)
    data = reduceData(data, N)

    
    #create a string to write to a file
    header.extend(data)
    final_data = " ".join(header)
    #remove unnecesary spaces
    final_data = final_data.replace(" ", "")

    saveData(of_path, final_data)
    
    print("DONE")
    print("data was written to: ", of_path)



if __name__ == "__main__":
    sys.exit(main())