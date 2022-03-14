#!/usr/bin/python3

import os
import pathlib
import time
import string
import subprocess
import argparse
import fnmatch
import glob
import pprint
import sys
import json

#########################################
#########################################
#########################################

from pathlib import Path, PurePath
from sys import platform
from simple_term_menu import TerminalMenu
from dotenv import load_dotenv

##########################################
##########################################
##########################################

#region VARIABLES

##############################
############ VARS ############
##############################

######## Default Hou paths #########
# Linux houdini_setup_bash         #
# mac houdini terminal             #
# win houdini command line tools   #
####################################


hou_18_paths = {
    "linux":"/opt/hfs18.5.759",
    "mac":"/Applications/Houdini18.5.759",
    "windows":"C:\Program Files\Side Effects Software\Houdini 18.5.759"
    }

#houdini terminal
HOUDINI_TERM = ''

# config
CONFIG = ''

# Other vars
path_list = []
env_dict = {}

# System Paths
HOU_ROOT = ''

# 3Delight Path
DELIGHT = ''

# ACES path
OCIO = ''

# current shot
SHOT = ''

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

def add_to_dict_and_arr(k,v):
    add_var_to_dict(k,v)
    add_to_arr(v)




#endregion
#region SETUP MAIN


#endregion
#endregion
#region LOGIC

#region HELPER LOGIC METHODS



###################################
####### Dir & Config Stuff ########
###################################

# config stuff
def create_config_dir():
    global CONFIG
    p = Path(Path.cwd())/'.config'
    if not Path.is_dir(p):
        Path.mkdir(p)
        CONFIG = p
    return p

# check OS
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

#region HOUDINI

##############################
####### Houdini Stuff ########
##############################

# def enableHouModule():
#     '''Set up the environment so that "import hou" works.'''
#     import sys, os

#     # Importing hou will load Houdini's libraries and initialize Houdini.
#     # This will cause Houdini to load any HDK extensions written in C++.
#     # These extensions need to link against Houdini's libraries,
#     # so the symbols from Houdini's libraries must be visible to other
#     # libraries that Houdini loads.  To make the symbols visible, we add the
#     # RTLD_GLOBAL dlopen flag.
#     if hasattr(sys, "setdlopenflags"):
#         old_dlopen_flags = sys.getdlopenflags()
#         sys.setdlopenflags(old_dlopen_flags | os.RTLD_GLOBAL)

#     try:
#         import hou
#     except ImportError:
#         # If the hou module could not be imported, then add 
#         # $HFS/houdini/pythonX.Ylibs to sys.path so Python can locate the
#         # hou module.
#         sys.path.append(os.environ['HHP'])
#         import hou
#     finally:
#         # Reset dlopen flags back to their original value.
#         if hasattr(sys, "setdlopenflags"):
#             sys.setdlopenflags(old_dlopen_flags)

# enableHouModule()
# import hou
#region Houdini Terminal
###################################################
############## Get Houdini Terminal ###############
###################################################



def source_houdini():
    platform = check_os()
    path = pathlib.Path(hou_18_paths[platform])
    new_path = ''
    if platform == 'win':
        term = 'bin/hcmd.exe'
        new_path = pathlib.Path(path) / term
    elif platform == 'mac':
        term = 'Utilities/Houdini Terminal 18.5.759'
        new_path = pathlib.Path(path) / term
    elif platform == 'linux':
        term = 'houdini_setup'
        new_path = pathlib.Path(path) / term
    #print(new_path)
    return new_path



# Slurp contents of terminal setup
def slurp_term():
    houdini_setup_file = source_houdini()
    platform = check_os()
    print(houdini_setup_file)
    string = ''
    # Linux
    if platform == 'linux':
        file = open(houdini_setup_file, "r")
        houdini_setup = file.read()
        file.close()
        print(houdini_setup)
        string = []
        string.append("%s\n\n" % PATH)
        if redshift == 1:
            # redshift is available
            string.append("%s\n" % redshift_LICENSE)
        string.append("cd %s\n\n" % HVER)
        string.append(houdini_setup)
        string.append("\n")
        string.append('\necho "Sourced %s"\n' % houdini_setup_file)
        string.append('\necho "hserver -S %s\n"' % HSERVER)
        string.append("hserver -S %s" % HSERVER)
        string.append("\n%s\n" % HVARS)
        string.append("%s\n" % HOUDINI_PATH)
        string.append("%s\n" % HOUDINI_GALLERY_PATH)
        string.append("%s\n" % HNO)
        string.append("%s\n" % HSITE)
        string.append("%s\n" % HPKG)
        string.append("%s\n" % SHORTCUTS)
    # Mac
    elif platform == 'mac':
        pass
    # Windows
    elif platform == 'win':
        pass

#endregion
#region Houdini final
#####################################################
################### Houdini Final ###################
#####################################################

def indie_check():
    user_choice = input(
        "Do you have houdini indie? y/n: ").lower()
    if user_choice == 'y':
        print("Great!")
    if user_choice == 'n':
        print("You will need to convert your hdas and project files to indie using you're project leads account on orbolt before you push changes!")
        print("please check the docs for link to the converter!")
    user_choice = input(
        "Do you have a python 3 version of houdini installed? y/n: ").lower()
    if user_choice == 'y':
        print("great!")
    if user_choice == 'n':
        print("please install a python 3 version of houdini 18.5.759! \n Thanks! ")
        sys.exit()


def load_from_config():
    from dotenv import load_dotenv
    load_dotenv("./.config/config.env")


    #print(os.environ)


def getHouRoot():
    os = check_os()
    #print(os)
    path = hou_18_paths[os]
    #print(path)
    return path


def init_houdini():
    # This variable is necessary on H19.0.455 due to Houdini bug
    #compat = "export LD_PRELOAD=/lib/x86_64-linux-gnu/libc_malloc_debug.so.0 ; "
    cmd = []
    #cmd.append(compat)
    cmd.append("export JOB=\"%s\" ; " % SHOT)
    # Create env vars for project sub-directories
    # for dir in DIRS:
    #     cmd.append("export %s=\"%s/%s\" ; " % (dir,SHOT,dir))
    return cmd


##### HOUDINI MAIN #####
def houdini_main():
    slurp_term()
    # load_from_config()

#endregion
#endregion
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
        add_to_dict_and_arr(pathname,item)




#region config files

def convert_env_dict_to_string():
    # new_d = {str(key):str(value) for key, value in env_dict}
    # return new_d
    new_d = {}
    # for x in env_dict.values():
    #     if x is not isinstance(x, str):
    #         print(x)
    for k, v in env_dict.items():
        # print(k)
        # print(type(v))
        new_d[k]=v
        if v is not isinstance(v, str):
            # print(v)
            new_v = str(v)
            new_d[k]=new_v
    #pprint.pprint(new_d)
    return(new_d)


def convert_env_dict_to_path():
    new_d = {}
    for k, v in env_dict.items():
        #print(type(v))
        #print(isinstance(v,str))
        if isinstance(v, str):
            #print(v)
            new_v = pathlib.Path(v)
            #print(new_v)
            #print(type(new_v))
            new_d[k]=new_v
        else:
            #print(type(v))
            new_d[k]=v
    #pprint.pprint(new_d)
    return new_d

def write_to_env_file():
    new_d = convert_env_dict_to_string()
    path_d = convert_env_dict_to_path()

    fp = Path(path_d["CONFIG"]) / "config.env"

    with fp.open("w",encoding="utf-8") as f:
        for key, value in path_d.items():
            f.write('%s="%s:&"\n' % (key, value))


def write_to_json():
    path_d = convert_env_dict_to_path()
    string_d = convert_env_dict_to_string()
    fp = Path(path_d["CONFIG"]) / "config.json"

    with fp.open("w") as f:
        f.write(json.dump(string_d,fp, indent=4,sort_keys=True))
    
    # with fp.open("w",encoding = "utf-8") as f:
    #     f.write(json.dump(string_d,fp, indent=4,sort_keys=True))

#region Config setup

def create_config_files():
    path = CONFIG
    print(path)
    write_to_env_file()
    #write_to_json()

#endregion

#endregion
#region 3DELIGHT setup

def delight_setup():
    if os.environ.get("DELIGHT") is not None:
        print("Congrats! You have 3Delight installed!")
        DELIGHT = os.environ.get("DELIGHT")
        add_to_dict_and_arr("DELIGHT",DELIGHT)
    else:
        print("You don't have 3Delight installed! \n Please install it, and configure it for ACES.")
        sys.exit("Please isntall 3Delight then try again. Thanks!")


#endregion
#region ACES setup

def aces_check():
    if os.environ.get("OCIO") is not None:
        print("Congrats! You have ACES configured correctly!")
        OCIO = os.environ.get("OCIO")
        add_to_dict_and_arr("OCIO",OCIO)
    else:
        print("You don't have ACES installed or need to fix the installation!")
        sys.exit("Please configure ACES and try again. Thanks!")
        



#endregion
#region SHOTS

############################################
################ Shot Prep #################
############################################

shot_subdir_names = [
    "GEO",
    "HIP",
    "RENDER",
    "TEXTURE",
    "BLEND",
    "ASSETS",
    "HDA"
]

shots_list = []


def create_shot():
    #ensure top-level 'shots' exists
    top_level_shot = Path("./Main_Project/shots")
    if not Path.is_dir(top_level_shot):
        Path.mkdir(top_level_shot)

    #case 1 - creating first shot directory
    first_shot_n = Path("./Main_Project/shots/shot_1")
    if not Path.is_dir(first_shot_n):
        Path.mkdir(first_shot_n)
        create_resource_subdirs(first_shot_n)
        print(f"\'{first_shot_n}\' created along with resource dirs.")
    #case 2 - creating any subsequent shot directory
    else:
        shot_n = first_shot_n
        # print(shot_n)
        # print(shot_n.name)
        # print(shot_n.parts[1])
        #skip existing shot directories...
        while Path.is_dir(shot_n):
            try:
                shot_name = shot_n.name
                #incremented_number = int(shot_n.name.parts[1].split('_')[1])+1
                incremented_number = int(shot_name.split('_')[1])+1
                #print(incremented_number)
                updated_shot_n = shot_n.parts[2].replace(shot_n.parts[2].split('_')[1],str(incremented_number))
                #print(updated_shot_n)
                shot_n = Path.joinpath(Path(shot_n.parts[1]), Path(updated_shot_n))
                shot_n = Path("./Main_Project")/shot_n
                #print(shot_n)
            except:
                raise Exception("couldn't increment appended folder number")

        #make the new shot directory...
        Path.mkdir(shot_n)
        shots_list.append(shot_n)
        #create resources for the new shot directory
        create_resource_subdirs(shot_n)


def create_resource_subdirs(curr_path):
    #create all conventional subdirs for a given (sub)directory
    for item in shot_subdir_names:
        resource_path = Path.joinpath(curr_path,Path(f"{item}"))
        if not Path.is_dir(resource_path):
            os.mkdir(resource_path)

#create_shot()

### Create a new shot folder
### decide whether or not to open newly created folder
### if not, list current shots
### choose one folder to open

def shot_decision():
    shots_dir = Path("./Main_Project/shots")
    shot_dir2 = os.path.join(os.getcwd(),"Main_Project/shots")
    #dirslist = glob.glob("%s/*/" % SHOTS_ROOT)
    #shots_list = os.listdir(path=shot_dir2)
    #shots_list = []
    menu_dict = {}
    for x in shots_dir.iterdir():
        shots_list.append(x)
        #print(x.name())
        menu_dict[x.name] = x
    #print(menu_dict,shots_list)
    user_choice = input(
        "Do you want to create a new shot folder? y/n: ").lower()
    if user_choice == 'y':
        create_shot()
        open_shot_folder(shots_dir,shots_list)
    if user_choice == 'n':
        open_shot_folder(shots_dir,shots_list)

def open_shot_folder(shots_dir,shot_list):
    user_choice = input(
        "Do you want to choose a shot to open? y/n: ").lower()
    if user_choice == 'y':
        choice = shots_term_menu(shot_list)
        #print(choice)
        #print(menu_dict)

        # get path from menu choice with dictionary
        choice_path = pathlib.Path(shots_dir)/choice
        SHOT = choice_path
        add_to_dict_and_arr("SHOT",choice_path)
        #print(choice_path)
        shot_resources = get_resource_paths(choice_path)
        #print(shot_resources)
        # convert to path object
        for i in range(len(shot_resources)):

            pathobj = pathlib.Path(Path.cwd())/shot_resources[i]
            #print(pathobj)
            shot_resources[i] = pathobj
        #print(shot_resources)
        #print(get_resource_paths(choice_path))
        shot_res_paths = get_resource_paths(choice_path)
        for x in shot_res_paths:
            k_path = pathlib.Path(x)
            k = k_path.name
            env_dict[k]=x
    if user_choice == 'n':
        sys.exit()

def shots_term_menu(list):
    #to string
    shots_str = []
    for x in list:
        shots_str.append(x.name)
    #print(shots_str)

    options = shots_str
    term_menu = TerminalMenu(options)
    menu_entry_index = term_menu.show()
    print(f"You have selected {options[menu_entry_index]}")
    return options[menu_entry_index]

def get_resource_paths(curr_path):
    resource_paths = [i[0] for i in os.walk(
        curr_path) if os.path.basename(str(i[0])) in shot_subdir_names]
    return resource_paths

#get_initial_paths()
#createShotDir()
#print(path_list,env_dict)



#endregion
#region path setup

def get_initial_paths():
    # config stuff
    CONFIG = create_config_dir()

    # houdini term
    HOUDINI_TERM = source_houdini()
    add_to_dict_and_arr('HOUDINI_TERM',HOUDINI_TERM)

    #print(CONFIG)
    add_to_dict_and_arr('CONFIG',CONFIG)

    # ACES and 3Delight
    delight_setup()
    aces_check()
    
    # System Pathts
    add_to_dict_and_arr("HOME",HOME)

    # Houdini Root Dir
    hou_root_str = getHouRoot()
    hou_root_path = pathlib.Path(hou_root_str)
    HOU_ROOT = hou_root_path
    add_to_dict_and_arr("HOU_ROOT",HOU_ROOT)
    # Repo Root
    add_to_dict_and_arr("REPO_ROOT",REPO_ROOT)
    # Project Root
    PROJECT_ROOT = pathlib.Path(REPO_ROOT,"Main_Project")
    add_to_dict_and_arr("PROJECT_ROOT",PROJECT_ROOT)
    # Global Assets Root
    ASSETS_GLOBAL_ROOT = pathlib.Path(PROJECT_ROOT,"assets")
    add_to_dict_and_arr("ASSETS_GLOBAL_ROOT",ASSETS_GLOBAL_ROOT)
    ########## GLOB CHILD DIRS #############
    globalAssetDirList = subdirList(ASSETS_GLOBAL_ROOT)
    initDirList(globalAssetDirList)

    # Global HDA
    HDA_GLOBAL = pathlib.Path(PROJECT_ROOT,"HDA")
    add_to_dict_and_arr("HDA_GLOBAL",HDA_GLOBAL)

    # PACKAGES
    PACKAGES = pathlib.Path(PROJECT_ROOT,"PACKAGES")
    add_to_dict_and_arr("HOUDINI_PACKAGE_DIR",PACKAGES)

    # SHOT ROOT
    SHOTS_ROOT = pathlib.Path(PROJECT_ROOT,"shots")
    add_to_dict_and_arr("SHOTS_ROOT",SHOTS_ROOT)
    

    #createShotDir(SHOTS_ROOT)
#endregion


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
    indie_check()
    get_initial_paths()
    print(CONFIG)
    # Shot stuff
    shot_decision()
    #houdini setup
    create_config_files()
    houdini_main()
    # print(str(env_dict))
    #pprint.pprint(env_dict)
    # pprint.pprint(path_list)

if __name__ == "__main__":
    main()

#endregion
