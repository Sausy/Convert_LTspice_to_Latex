from ast import If, expr_context
from glob import glob
import numpy as np
import os
import sys 


defaultComponents = {
			'bi': 'controlled current source,i=\ ',
			'bi2': 'controlled current source,i_=\ ',
			'bv': 'controlled voltage source,v_=\ ',
			'cap': 'C',
			'csw': 'switch',
			'current': 'current source,i=\ ',
			'diode': 'D',
			'f': 'controlled current source,i=\ ',
			#'FerriteBead': 'twoport',
			'h': 'voltage source,v_=\ ',
			'ind': 'L',
			#'ind2': 'L',
			'LED': 'led',
			'load': 'vR',
			'load2': 'controlled current source,i=\ ',
			'polcap': 'eC',
			'res': 'R',
			'res2': 'R',
			'schottky': 'sDo',
			'TVSdiode': 'zDo',
			'varactor': 'VCo',
			'voltage': 'voltage source,v_=\ ',
			'zener': 'zDo',}

rotation = {
			'R0': [[1,0],[0,1]],
			'R90': [[0,-1],[1,0]],
			'R180': [[-1,0],[0,-1]],
			'R270': [[0,1],[-1,0]],
            'R360': [[1,0],[0,1]],
			'M0': [[-1,0],[0,1]],
			'M90': [[0,-1],[-1,0]],
			'M180': [[1,0],[0,-1]],
			'M270': [[0,1],[1,0]],}

rotation_hotfix = {
			'R0': [[1,0],[0,1]],
			'R90': [[0,-1],[1,0]],
			'R180': [[-1,0],[0,-1]],
			'R270': [[0,1],[1,0]],
            'R360': [[1,0],[0,1]],
			'M0': [[-1,0],[0,1]],
			'M90': [[0,-1],[-1,0]],
			'M180': [[1,0],[0,-1]],
			'M270': [[0,1],[1,0]],}

'''
rotation = {
			'R0': [[1,0],[0,1]],
			'R90': [[0,-1],[1,0]],
			'R180': [[-1,0],[0,-1]],
			'R270': [[0,1],[-1,0]],
			'M0': [[-1,0],[0,1]],
			'M90': [[0,-1],[-1,0]],
			'M180': [[1,0],[0,-1]],
			'M270': [[0,1],[1,0]],}
'''

path_ltspice = ""

#pars path and file name 
def parsPathStr(path_, fileName_):
    ret_ = ''
    #check if last char of path is / or \ depending on the operating system
    if os.name == 'nt':
        if not path_[-1] == '\\':
            path_ = path_ + '\\'
        if fileName_[0] == '\\':
            fileName_ = fileName_[1:]
    else:
        if not path_[-1] == '/':
            path_ = path_ + '/'
        if fileName_[0] == '/':
            fileName_ = fileName_[1:]

    ret_ = path_ + fileName_

    if os.name == 'nt':
        print("")
    else:
        ret_ = ret_.replace("\\","/")

    return ret_


#load data from asc file
def getData(path_):
    ret_ = list()

    if path_[-3:] == "asc":
        #with open(path_, "r") as f:
        #    ret_ = f.readlines()
        #    print(ret_)
        
        #requires utf-16-le to ensure we don't run into german umlaut issues
        try:
            with open(path_, "r", encoding='utf-16-le') as f:
                ret_ = f.readlines()
                print(ret_)
        except:
            print("[WARNING] wasnot able to decode")
            with open(path_, "r") as f:
                ret_ = f.readlines()
                print(ret_)
        
            
    elif path_[-3:] == "asy":
        with open(path_, "r") as f:
            ret_ = f.readlines()
    else:
        print("[Error] please select an asc file")
        sys.exit()

    return ret_

def saveData(path_, data_):
    f  = open(path_, "w")
    f.write(data_)
    f.close()

def cleanUpName(name):
    ones = ["", "one","two","three","four", "five", "six","seven","eight","nine","ten"]
    result = ''.join(ones[int(i)] if i.isdigit() else str(i) for i in name)

    result = result.replace("-", "")
    result = result.replace("\\", "")
    result = result.replace("/", "")

    return result


def genLUT(data_):
    wire = list() #[x0,y0], [x1,y1]
    symbol = list() #[x0,y0], path, tag ,rot
    buffer = []
    flag = list() #style_path, [x0,y0]

    #since the raw data is quite big a scaling factor of 
    #1/64 was found to work quite nicly 
    scaler = 64.0

    FLAG_foundTag = False
    for row in data_: 

        instance = row.split(" ") #data is split via white space
        offset_ = 0.0

        #if the amount of data in a row is less then two 
        #we can ignore it, its likly a comment or info tag         
        if len(instance) < 2: 
            continue
        
        #the first value of the data identifies what kind of row data there is present
        if instance[0] == "WIRE": #wire
            wire.append([[float(instance[1])/scaler, float(instance[2])/scaler],[float(instance[3])/scaler, float(instance[4])/scaler]])
        elif instance[0] == "FLAG": #FLAG
            flag.append([[float(instance[1])/scaler, float(instance[2])/scaler], instance[3].replace("\n", "")]) 
            
        elif instance[0] == "SYMBOL": #SYMBOL
            buffer = instance
            FLAG_foundTag = False
        
        elif instance[0] == "WINDOW": #SYMBOL
            pass

        elif instance[0] == "SYMATTR": #SYMBOL 
            #find the first attribute for the Symbol and push the Symbol with path and tag name to its list
            if instance[1] == "InstName":
                if FLAG_foundTag == False: 
                    FLAG_foundTag = True
                    symbol.append([[float(buffer[-3])/scaler, float(buffer[-2])/scaler], buffer[1].replace("\n",""), instance[-1].replace("\n","") ,buffer[-1].replace("\n","")]) 
                    print("Added Component: ", symbol)
        
        else:
            continue


    return wire, symbol, flag

def checkIfDeafaultComp(data_):
    try:
        ret_ = defaultComponents[data_[1]]
    except:
        ret_ = "" 
    return ret_ 


#This function is basicly 1:1 copy from the project 
#[Steffen-W]:https://github.com/Steffen-W/Convert_LTspice_to_Latex
def printXY(xy,offset =[0 , 0]):
    return '(' + str(xy[0]-offset[0]) + ',' + str(xy[1]-offset[1]) + ')'

#This function is basicly 1:1 copy from the project 
#[Steffen-W]:https://github.com/Steffen-W/Convert_LTspice_to_Latex
def drawNewComp(s_):
    global path_ltspice
    global rotation
    global rotation_hotfix

    print("\n==========\nStart drawing new component")

    #symbol ..[[x0,y0], path, tag ,rot]
    path_ = s_[1]
    name = cleanUpName(s_[1])
    tag_ = s_[2]
    #there can be an M or an R tag as first char
    # hence we leave away the first char
    rot_ = float(s_[3][1:]) 
    x_ = s_[0][0]
    y_ = s_[0][1]

    scaler = 64.0

    path_ = parsPathStr(path_ltspice, path_ + ".asy")
    print("path: ", path_)
    data_ = getData(path_)

    
    print("name: ", name)

    pin = []
    pinName = []
    line = []
    rect = []
    circ = []
    arc = []
    text = []
    window = []

    for l in data_:
        words = l.split()
        if words[0] == 'PIN':      # Das wird nicht gezeichnet
            pin.append([int(words[1])/scaler,-int(words[2])/scaler])
        if words[0] == 'LINE':     #\draw (-1.5,0) -- (1.5,0);
            line.append([int(words[2])/scaler,-int(words[3])/scaler,int(words[4])/scaler,-int(words[5])/scaler])
        if words[0] == 'RECTANGLE': #\draw (0,0) rectangle (1,1)
            rect.append([int(words[2])/scaler,-int(words[3])/scaler,int(words[4])/scaler,-int(words[5])/scaler])
        if words[0] == 'CIRCLE':   #\draw[x radius=2, y radius=1] (0,0) ellipse [];
            circ.append([int(words[2])/scaler,-int(words[3])/scaler,int(words[4])/scaler,-int(words[5])/scaler])
        if words[0] == 'ARC':      #\draw (3mm,0mm) arc (0:30:3mm);
            arc.append([int(words[2])/scaler,-int(words[3])/scaler,int(words[4])/scaler,-int(words[5])/scaler,int(words[6])/scaler,-int(words[7])/scaler,int(words[8])/scaler,-int(words[9])/scaler])
        if words[0] == 'TEXT':     #\node[right] at (0,1) {bla} ;
            text.append([int(words[1])/scaler,-int(words[2])/scaler ,words[3],' '.join(words[5:])])
        if words[0] == 'WINDOW':      # Das wird nicht gezeichnet
            window.append([int(words[2])/scaler,-int(words[3])/scaler])


    newLib = '\\def\\' + name + r'(#1)#2#3{%' + '\n' +  r'  \begin{scope}[#1,transform canvas={scale=1.0}]' + '\n'
    offset = pin[0] if pin else [0, 0] 

    

		
    for t in line:
        newLib = newLib + r'  \draw ' + printXY(t[0:],offset) + ' -- ' + printXY(t[2:],offset) + ';' + '\n'
    if window:#\draw  (2,0.5) node[left] {$x$};
        t = window[0]
        newLib = newLib + r'  \draw ' + printXY(t[0:],offset) + ' coordinate (#2 text);'+'\n'
        #newLib = newLib + r'  \draw ' + printXY(t[0:],offset) + ' node[right] {#3};\n'
    for t in circ:
        newLib = newLib + r'  \draw[x radius=' + str((t[2]-t[0])/2) + ', y radius=' + str((t[3]-t[1])/2) + ']'
        newLib = newLib + printXY([(t[0]+t[2])/2,(t[1]+t[3])/2],offset) + ' ellipse [];' + '\n'
    for t in arc: #\draw (0,4)++(49: 1 and 2)  arc (49:360: 1 and 2);
        center = [(t[0]+t[2])/2,(t[1]+t[3])/2]
        Rx = (t[2]-t[0])/2
        Ry = (t[3]-t[1])/2
        StartWinkel = np.angle((t[4]-center[0])+1j*(t[5]-center[1]))*180/np.pi
        EndWinkel = np.angle((t[6]-center[0])+1j*(t[7]-center[1]))*180/np.pi
        #if Rx < 0 or Ry < 0:
        #    t = StartWinkel
        #    StartWinkel = EndWinkel
        #    EndWinkel = t
        strR = str(abs(Rx)) + ' and ' + str(abs(Ry))
        newLib = newLib + r'  \draw ' + printXY(center,offset) + '++( ' + str(StartWinkel) +  ': ' + strR
        newLib = newLib + ')  arc ('+ str(StartWinkel) +':'+ str(EndWinkel) +': ' + strR + ');' + '\n'
    for t in rect:
        newLib = newLib + r'  \draw ' + printXY(t[0:],offset) + ' rectangle ' + printXY(t[2:],offset) + ';' + '\n'
    for t in text:
        newLib = newLib + r'  \node[right] at ' + printXY(t[0:],offset) + r'{' + t[3] + r'};' + '\n'
    for ind,t in enumerate(pin):
        newLib = newLib + r'  \draw ' + printXY(t[0:],offset) + ' coordinate (#2 X' + str(ind) + ');' + '\n'
        pinName.append('  X' + str(ind))


    newLib = newLib + r'  \end{scope}' + '\n'

		
    if window:
        newLib = newLib + r'  \draw (#2 text) node[right] {#3};'+'\n'
        
    newLib = newLib + r'}' + '\n'

    #acually place the component
    print("offset: ", offset)
    #print("x: ", x_)
    #print("y: ", y_)
    #print("rot: ", rot_)
    #print("tag: ", tag_)
    #off_x_ = float(offset[0]) * float(rotation_hotfix[s_[3]][0][0]) + float(offset[1]) * float(rotation_hotfix[s_[3]][0][1])
    #off_y_ = float(offset[0]) * float(rotation_hotfix[s_[3]][1][0]) + float(offset[1]) * float(rotation_hotfix[s_[3]][1][1])
    #print("off_x_: ", off_x_)
    #print("off_y_: ", off_y_)

    pins = getPinPos(s_)
    #print("[INFO]: pins " + str(pins[0][0][0]) + "," + str(-pins[0][0][1]) ) 
           
    #x0_ = x_ + off_x_#+ offset[0]
    #y0_ = -(y_ + off_y_) #+ offset[1]

    x0_  = pins[0][0][0]
    y0_ = -pins[0][0][1]
    #since the whole coord system is negative Y
    #y0_ = -y0_
    if s_[3][0] == "M":
        place_comp = "\\" + name + r" (shift={(" + str(x0_) +  r"," + str(y0_) +  r")},rotate= " + str(rot_)  + r"0  , xscale=-1) {B0} {" + tag_ + r"};" + "\n"
    else:
        place_comp = "\\" + name + r" (shift={(" + str(x0_) +  r"," + str(y0_) +  r")},rotate= " + str(360.0 - rot_)  + r"0  ) {B0} {" + tag_ + r"};" + "\n"
    print(place_comp)

    newLib = newLib + place_comp

    #print(newLib) 

    return newLib



def getPinPos(s_):
    #offset calculation of the pin 
    global path_ltspice
    global rotation
    pins = list()
    buffer = []

    #symbol ..[[x0,y0], path, tag ,rot]
    path_ = s_[1]
    tag_ = s_[2]
    rot_ = s_[3]
    
    x0,y0 = s_[0]
    off_x_ = 0.0
    off_y_ = 0.0

    scaler = 64.0

    if tag_ == "M2":
        print("!!!!! hier")

    path_ = parsPathStr(path_ltspice, path_ + ".asy")
    data_ = getData(path_)
    flag_foundNew = False
    for row in data_: 
        instance = row.split(" ") #data is split via white space
        if instance[0] == "PIN":
            buffer = instance
            #since the object can be rotated we simlpy multiply it with its rotation matrix
            #simple scalar product buf @ RotMatrix = buf_new
            print("TAG: ", tag_)
            print("Rotation: ", rot_)
            print("buffer: ", buffer)
            off_x_ = float(buffer[1]) * float(rotation[rot_][0][0]) + float(buffer[2]) * float(rotation[rot_][0][1])
            off_y_ = float(buffer[1]) * float(rotation[rot_][1][0]) + float(buffer[2]) * float(rotation[rot_][1][1])
            off_ = [off_x_, off_y_]
            print("ofset: ", off_)
            print("s[0]: ", s_[0])
            flag_foundNew = False
        elif instance[0] == "PINATTR":
            if flag_foundNew == False: 
                x_new = float(off_x_)/scaler + s_[0][0] 
                y_new = float(off_y_)/scaler + s_[0][1] 
                pins.append([[x_new, y_new], instance[-1].replace("\n","")]) 
                flag_foundNew = True
            else:
                buffer = []

    print(pins)

    return pins



def genTexBody(wire, symbol, flag):
    data_ = ""


    #loop through all saved wires
    for w in wire:
        data_ = data_ + "\\draw (" + str(w[0][0]) + "," + str(-w[0][1]) + ") -- (" + str(w[1][0]) + "," + str(-w[1][1]) + ");\n"

    #loop through all saved symbols
    for s in symbol:
        #symbol ..[[x0,y0], path, tag ,rot]
        tag_ = s[2]

        #check if its default comp
        symb_str_ = checkIfDeafaultComp(s)

        #if not a default component draw it from scratch
        if symb_str_ == "":
            new_data = drawNewComp(s)
            data_ = data_ + new_data
        else:
            #first we need to know where the pins of each component are 
            pins = getPinPos(s)

            data_ = data_ + "\\draw (" + str(pins[0][0][0]) + "," + str(-pins[0][0][1]) + ")  to[" + symb_str_ + ", l=" + tag_ + "] (" + str(pins[1][0][0]) + "," + str(-pins[1][0][1]) + ") ;\n"
            if tag_ == "C2":
                print("[INFO] s: ", s)
                print("[INFO] pins: ", pins)
                print("[INFO] data: ")
                print("\\draw (" + str(pins[0][0][0]) + "," + str(-pins[0][0][1]) + ")  to[" + symb_str_ + ", l=" + tag_ + "] (" + str(pins[1][0][0]) + "," + str(-pins[1][0][1]) + ") ;\n")

        '''
        symb_str_, tag_str_ = checkIfDeafaultComp(s)

        #check if its a default component 
        if symb_str_ == "" :
            #Not default 
            print("need to generate Symbol in Latex")
        else: 
            #\draw (-8.75,11.0) node[nigfete,anchor=D,rotate=-0](B0){\} ;
            #data_ = data_ + "\\draw (" + str(s[1][0]) + "," + str(s[1][1]) + ")  node[" + symb_str_ + "] (foo{})".format(knot_cnt) + " {\rotatebox{0}{" + tag_str_ + "}};\n"
            print(s)
            data_ = data_ + "\\draw (" + str(s[0][0]) + "," + str(s[0][1]) + ")  node[" + symb_str_ + "] (foo{})".format(knot_cnt) + " {}};\n"
        '''

    #loop through all saved flags e.g.: GND
    for f in flag:
        if f[-1] == "COM":
            type_ = "cground" #earth symbol
        elif f[-1] == "0":
            type_ = "ground" #common gnd symbol
        else:
            type_ = "ocirc , label={}".format(f[-1])
            
        data_ = data_ + "\\draw (" + str(f[0][0]) + "," + str(-f[0][1])+ ") node[" + type_ + "] {};\n"
    
    return data_


def main():
    global path_ltspice 

    args = sys.argv
    if len(args) < 3:
        print("usage py3 <program> [input File] [output Path]")
        sys.exit()

    if_path = args[1]
    of_path = args[2]

    #test if Input file exist
    print(if_path)
    try:
        f = open(if_path)
    except IOError:
        print("Input File doesn't exist")
        sys.exit()
    f.close()

    if os.name == 'nt':
        print("OS: is Windows")
        path_ltspice = r'C:\Program Files\LTC\LTspiceXVII\lib\sym' #path to LTSpice libs
        file_name = if_path.split("\\")[-1]
        #path_input = r'C:\Users\Micha\OneDrive\Project\robco\MasterThesis\Simulation\SpiceSimulation' #path to source folder
        #path_output = r'C:\Users\Micha\OneDrive\Project\robco\MasterThesis\converter'
        #fileName_input = '\Draft24.asc'
        #fileName_output = '\Draft24.tex'
    else:
        print("OS: is NOT Windows")
        path_ltspice = r'/mnt/c/Program Files/LTC/LTspiceXVII/lib/sym/' #path to LTSpice libs

        file_name = if_path.split("/")[-1]

        #path_input = r'/mnt/c/Users/Micha/OneDrive/Project/robco/MasterThesis/Simulation/SpiceSimulation/' #path to source folder
        #path_output = r'/mnt/c/Users/Micha/OneDrive/Project/robco/MasterThesis/converter/'

        #fileName_input = 'Draft25.asc'
        #fileName_output = 'Draft25.tex'
    
    #path_input = parsPathStr(path_input, fileName_input)
    #path_output = parsPathStr(path_output, fileName_output)

    data = getData(if_path)
    wire,symbol,flag = genLUT(data) 
    #wire ... [[x0,y0], [x1,y1]]
    #symbol ..[[x0,y0], path, tag ,rot]
    #flag  .. [style_path, [x0,y0], rot]


    #define tex data 
    tex_data_header = """
    \\ctikzset{tripoles/mos style/arrows}  
    \\begin{circuitikz}[transform shape,scale=0.8] 
    """ 

    tex_body = genTexBody(wire,symbol,flag)

    tex_data_bottom = "\end{circuitikz}"


    #save dat to tex file 
    tex_data = tex_data_header + tex_body + tex_data_bottom
    saveData(of_path, tex_data)

    #print(tex_data)




if __name__ == "__main__":
    sys.exit(main())