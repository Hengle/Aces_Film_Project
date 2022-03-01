#!/usr/bin/python3


import os
import pathlib
import time
import string
import subprocess
import argparse
import fnmatch
import glob
###
from pathlib import Path, PurePath
from sys import platform

from rdflib import SH


#region VARIABLES

##############################
############ VARS ############
##############################

##### Default Hou paths ######
# Linux houdini_setup_bash
# mac houdini terminal
# win houdini command line tools

hou_18_paths = {
    "linux":"/opt/hfs18.5.759",
    "mac":"/Applications/Houdini18.5.759",
    "windows":"C:\Program Files\Side Effects Software\Houdini 18.5.759"
    }




# Other vars
path_list = []
env_dict = {}

# System Paths
HOU_ROOT = ''


# preset paths
HOME = Path.home() # gets path for HOME variable
REPO_ROOT = Path.cwd()
#print(REPO_ROOT)
dirslist = glob.glob("%s/*/" % REPO_ROOT)
#print(dirslist)

# paths to set

PROJECT_ROOT = ''
SHOTS_ROOT = ''
ASSETS_GLOBAL_ROOT = ''

PACKAGES = ''
HDA_GLOBAL = ''

# PER SHOT VARS
BLEND = ''
GEO = ''
HIP = ''
RENDER = ''
REF = ''
TEXTURE = ''

#endregion
#region SETUP
##############################
###### SET UP FOR LATER ######
##############################

#region HELPER SETUP METHODS
###############################
####### DIRECTORY PATHS #######
###############################

def get_path(root,target):
    new_path = PurePath(root,target)
    return new_path


def add_var_to_dict(k,v):
    #k = [ i for i, a in locals().items() if a == v][0]
    #print(k)
    env_dict[k]=v

def add_to_arr(obj):
    path_list.append(obj)

def addToDictAndArr(k,v):
    add_var_to_dict(k,v)
    add_to_arr(v)

def check_if_path_obj(path):
    result=''
    # checks if the variable is any instance of pathlib
    if isinstance(path, pathlib.PurePath):
        print("It's pathlib!")
        result=True
        # No PurePath
        if isinstance(path, pathlib.Path):
            print("No Pure path found here")
            if isinstance(path, pathlib.WindowsPath):
                print("We're on Windows")
            elif isinstance(path, pathlib.PosixPath):
                print("We're on Linux / Mac")
        # PurePath
        else:
            print("We're a Pure path")
            result=False

# def Check_OS_Pathtype(path):
#     result=''
#     # checks if the variable is any instance of pathlib
#     if isinstance(path, pathlib.PurePath):
#         print("It's pathlib!")
#         result=True
#         # No PurePath
#         if isinstance(path, pathlib.Path):
#             print("No Pure path found here")
#             if isinstance(path, pathlib.WindowsPath):
#                 print("We're on Windows")
#             elif isinstance(path, pathlib.PosixPath):
#                 print("We're on Linux / Mac")
#         # PurePath
#         else:
#             print("We're a Pure path")
#             result=False



###############################
######## ENV VAR STUFF ########
###############################

def check_if_var_exists():
    pass

def check_value_of_env_var():
    pass

def compare_env_value():
    pass

def unset_env_var():
    pass

def set_env_var():
    pass

#endregion

#region SETUP MAIN


#endregion
#endregion
#region LOGIC

#region HELPER LOGIC METHODS

###########################
####### User Input ########
###########################

def question_pred():
    pass

# OS Stuff

def check_os():
    platform = ''
    from sys import platform
    if platform == "linux" or platform == "linux2":
        # linux
        print("Congrats! You are on linux!")
        platform = "linux"
        #return
        pass
    elif platform == "darwin":
        # OS X
        print("You are on OSX")
        platform = "mac"
        #return
        pass
    elif platform == "win32":
        # Windows...
        print("You are, unfortunately on Windows...")
        platform = "win"
        #return
        pass
    else:
        print("I don't know what system you're on...")
        pass
    return platform


###################################
####### Dir & Config Stuff ########
###################################

# directory stuff
def create_dir_list():
    pass

def create_dirs():
    pass

def project_list():
    pass

# config stuff
def create_config_dir():
    p = pathlib.Path(REPO_ROOT,".config")
    #print(p)
    p.mkdir(parents=True,exist_ok=True)


def terminal_config_file():
    pass

##############################
####### Houdini Stuff ########
##############################

def get_houdini_version():
    pass

def get_houdini_hython_path():
    pass



def getHouRoot():
    os = check_os()
    #print(os)
    path = hou_18_paths[os]
    #print(path)
    return path

def get_hip_file_path():
    pass

def set_hip_file_paths():
    pass

def init_houdini():
    pass

def launch_houdini():
    pass


#endregion
#region WORK SETUP METHODS

def subdirList(rootDir):
    rootdirlist = glob.glob("%s/*/" % rootDir)
    return rootdirlist

def initDirList(list):
    for item in list:
        pp = pathlib.PurePath(item)
        pathname = "G_" + pp.name
        #print(pathname)
        addToDictAndArr(pathname,item)

# Shot Pretp

def createShotDir(rootdir):
    path = rootdir
    print(path)
    dirlist = subdirList(path)
    print(dirlist)
    namelist = []
    newshotdir = ''
    if dirlist:
        for item in dirlist:
            pp = pathlib.PurePath(item)
            pathname = pp.name
            namelist.append(pathname)
            print(pathname)
        #print(namelist.count('i'))
        newdirnum = namelist.count('i') + 1
        print(newdirnum)
        newdirname = "Shot_" + str(newdirnum + 1)
        print(newdirname)
        newshotdir = os.mkdir(os.path.join(path,newdirname))
    else:
        newshotdir = os.mkdir(os.path.join(path,"Shot_1"))

def createShotSubDirs(shotroot):
    pass

def get_initial_paths():
    # System Pathts
    addToDictAndArr("HOME",HOME)
    # Houdini Root Dir
    hou_root_str = getHouRoot()
    hou_root_path = pathlib.Path(hou_root_str)
    HOU_ROOT = hou_root_path
    addToDictAndArr("HOU_ROOT",HOU_ROOT)
    # Repo Root
    addToDictAndArr("REPO_ROOT",REPO_ROOT)
    # Project Root
    PROJECT_ROOT = pathlib.Path(REPO_ROOT,"Main_Project")
    addToDictAndArr("PROJECT_ROOT",PROJECT_ROOT)
    # Global Assets Root
    ASSETS_GLOBAL_ROOT = pathlib.Path(PROJECT_ROOT,"assets")
    addToDictAndArr("ASSETS_GLOBAL_ROOT",ASSETS_GLOBAL_ROOT)
    ########## GLOB CHILD DIRS #############
    globalAssetDirList = subdirList(ASSETS_GLOBAL_ROOT)
    initDirList(globalAssetDirList)

    
    # Global HDA
    HDA_GLOBAL = pathlib.Path(PROJECT_ROOT,"HDA")
    addToDictAndArr("HDA_GLOBAL",HDA_GLOBAL)

    # PACKAGES
    PACKAGES = pathlib.Path(PROJECT_ROOT,"packages")
    addToDictAndArr("packages",PACKAGES)

    # SHOT ROOT
    SHOTS_ROOT = pathlib.Path(PROJECT_ROOT,"shots")
    addToDictAndArr("SHOTS_ROOT",SHOTS_ROOT)
    
    createShotDir(SHOTS_ROOT)


get_initial_paths()
#createShotDir()
#print(path_list,env_dict)


#endregion
#region WORK LOGIC METHODS

###############################
####### User Interface ########
###############################



#endregion
#region LOGIC FINAL

#endregion
#region EXECUTE
def main():
    pass

#endregion
