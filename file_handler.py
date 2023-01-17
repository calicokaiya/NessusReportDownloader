import os
import shutil
import pathlib
import sys
import datetime


# Deletes all files from the output folder
def cleanOutputFolder():
    outputFiles = os.listdir(r"./output")
    for file in outputFiles:
        print("Deleting ./output/" + file)
        os.unlink("./output/" + file)


# Will get the names of all files in the output list and return them
def getOutputFileList():
    outputPath = os.getcwd() + ("/output/")
    files = os.listdir(outputPath)
    return files
