import os
import numpy as np


def load_and_parse_data():
    with open("TTT_NN_FILES\trainData.txt","r") as o:
        data = o.read()

    data = data.replace("\n","|||")
    data = data.split("|||")
    data = data[:-1] # remove last
    inputVector, outputVector = [],[]

    for index, vector in enumerate(data):
        if index%2==0:
            inputVector.append(vector)  
        else:
            outputVector.append(vector)

    def parse(string):
        string= string.replace("(  ","|")
        string= string.replace("  )","")
        string = string[1:]
        string = string.replace(",",".")
        string = string.split("|")

        return string

    inputVector = list(map(changeString_toFloat, inputVector) )
    outputVector = list(map(changeString_toFloat, outputVector) )

    inputVector = list(map(lambda x: [float(e) for e in x] ,inputVector) )
    outputVector = list(map(lambda x: [float(e) for e in x], outputVector) )

    inputVector = np.array(inputVector)
    outputVector = np.array(outputVector)

    inputVector = inputVector.astype(np.float32)
    outputVector = outputVector.astype(np.float32)
    return inputVector,outputVector

   
def write_VectorList_to_file(vectorList,fileName):
    string = ""
    for out in vectorList:
        string = string + str(out)+"\n"  
    with open(fileName,"w") as out:
        out.write(string)