import sys 
import os
import codecs

from LTspiceToTexConverter import *

if os.name == 'nt':
    print("OS: is Windows")
    path_ltspice = r'C:\Program Files\LTC\LTspiceXVII\lib\sym' #path to LTSpice libs
    path_input = r'C:\Users\Micha\OneDrive\Project\robco\MasterThesis\Simulation\SpiceSimulation' #path to source folder
    path_output = r'C:\Users\Micha\OneDrive\Project\robco\MasterThesis\converter'
    fileName_input = '\Draft24.asc'
    fileName_output = '\Draft24.tex'
else:
    print("OS: is NOT Windows")
    path_ltspice = r'/mnt/c/Program Files/LTC/LTspiceXVII/lib/sym/' #path to LTSpice libs
    
    path_input = r'/mnt/c/Users/Micha/OneDrive/Project/robco/MasterThesis/Simulation/SpiceSimulation/' #path to source folder
    path_output = r'/mnt/c/Users/Micha/OneDrive/Project/robco/MasterThesis/converter/'

    fileName_input = 'Draft25.asc'
    fileName_output = 'Draft25.tex'


path_inputFile = path_input + fileName_input
path_outputFile = path_output + fileName_output


print("input:  " , path_inputFile)
print("output: " , path_outputFile)

LtSpiceToLatex(saveFile = path_outputFile, filenameLTspice = path_inputFile, lt_spice_directory = path_ltspice, fullExample=0)

#with open("umlautTest.txt", "r", encoding='utf-16-le') as f:
#with open(path_inputFile, "r", encoding='utf-16') as f:
#    data = f.readlines()
#    print(data)

