#!/usr/bin/python3
#region HEADER

from importlib.resources import path
#from lzma import _PathOrFile
from operator import add
import os
import pathlib
import string
import subprocess
import argparse
import fnmatch
import glob
import sys
import json
import yaml
import re

#########################################
#########################################
#########################################

from itertools import chain, repeat
from pathlib import Path, PurePath
from sys import platform
#from simple_term_menu import TerminalMenu
from dotenv import load_dotenv

##########################################
##########################################
##########################################
#endregion
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
    "win":"C:\Program Files\Side Effects Software\Houdini 18.5.759"
    }

#inital setup check
INITIALIZED=''

#Team member name
USER: string = ''

#dates
INIT_DATE=''
CURRENT_DATE=''
LAST_OPENED=''
TIME_OPENED=''
TIMES_OPENED = []
DATES_OPENED = []

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
REPO_ROOT = Path(__file__).parents[1]

dirslist = glob.glob("%s/*/" % REPO_ROOT)


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
#region HELPER METHODS
#region Directory Setup helper methods

###############################
####### DIRECTORY PATHS #######
###############################

def get_path(root,target):
    new_path = PurePath(root,target)
    return new_path

def add_var_to_dict(k,v):

    env_dict[k]=v

def add_to_arr(obj):
    path_list.append(obj)

def add_to_dict_and_arr(k,v):
    add_var_to_dict(k,v)
    add_to_arr(v)

def add_dirlist_to_return_dict(list):

    k = ''
    v = ''
    dict = {}
    for i in list:
        #print(f'is {i.name} a dir? :: {i.is_dir()} ')
        #print(i.is_dir())
        if (i.is_dir() == True):
            k = i.name
            v = i
            #print(f'check::  {k}::{v}')
            dict[k]=v
        else:
            continue
    return dict

def create_dir_if_not_present(dirpath):

    print(f'Creating {dirpath.name} Directory...')

    pathlib.Path(dirpath).mkdir(parents=True,exist_ok=True)

def create_dirs_from_list(currpath,dirlist) -> list:
    """
    takes the current path as a path obejct and a list of strings 
    created the child directories based on the list of strings
    returns an array of the paths of the newly created child dirs
    if dirs already exist grap the paths and export them
    """
    newpathlist = []
    for d in dirlist:
        newdirpath = pathlib.Path(currpath)/d
        

        create_dir_if_not_present(newdirpath)
        try:
            if newdirpath.exists():
                newpathlist.append(newdirpath)
        except:
            print('could not add child dir to list!')
    return newpathlist

def add_dirlist_to_dict(dirlist,nameprefix):
    '''Add a list to a dictionary and add a prefix to key'''

    for d in dirlist:
        k = f'{nameprefix}{d.name}'

        add_to_dict_and_arr(k,d)

def is_empty(folder: Path) -> bool:
    return not any(folder.iterdir())

# create empty file in empty dir for git
def add_file_to_empty_folder(path):
    if is_empty(path):
        fp = pathlib.Path(path)/'.gitkeep'
        fp.open("w",encoding="utf-8")

def add_readme_file_to_dir(path):
    #check if git file exists
    # gitfile = pathlib.Path(path)/'.gitkeep'
    # if gitfile.exists():
    #     print('git file exists')
    #     gitfile.unlink()
    print(f'creating README file in {path.name}...')
    fp = pathlib.Path(path)/'README.md'
    fp.open("w",encoding="utf-8")
    





def add_files_to_empty_folders(dirlist):
    for d in dirlist:
        #print(d)
        add_file_to_empty_folder(d)


#endregion
#region Dir and Config helper methods

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

def subdirList(rootDir):
    rootdirlist = glob.glob("%s/*/" % rootDir)
    return rootdirlist

def initDirList(list):
    for item in list:
        pp = pathlib.PurePath(item)
        pathname = "G_" + pp.name
        #print(pathname)
        add_to_dict_and_arr(pathname,item)
#endregion
#region User Input Helper funcs

# question stuff
def y_n_q(q) -> bool:
    '''
    give question
    keep asking question with invalid input
    if the input is yes return true
    if the input is no return false
    '''
    result=''
    while True:
        try:
            user_choice = input(f'{q} y/n: ').lower()
            if(user_choice == 'y'):
                return True
            elif(user_choice == 'n'):
                return False
            else:
                raise ValueError
        except ValueError:
            print('Invalid input. Please try again...')
            continue

#endregion
#endregion
#region HOUDINI 
##############################
####### Houdini Stuff ########
##############################
#region HOUDINI setup



def indie_check():
    '''Check if user has the correct houdini installed'''
    if y_n_q("Do you have houdini indie?"):
        print('Great!')
    else:
        print("You will need to convert your hdas and project files to indie using you're project leads account on orbolt before you push changes!")
        print("please check the docs for link to the converter!")
    if y_n_q("Do you have a python 3 version of houdini installed?"):
        print('Great!')
    else:
        print("please install a python 3 version of houdini 18.5.759 and then run this tool again!")
        print('Thanks!')
        sys.exit()


def load_from_config():
    from dotenv import load_dotenv
    load_dotenv("./.config/config.env")

def getHouRoot():
    os = check_os()
    #print(os)
    path = hou_18_paths[os]
    #print(path)
    return path

#endregion
#region Houdini Terminal

###################################################
############## Get Houdini Terminal ###############
###################################################




# CMD prompt & BASH & CSH

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


#endregion
#region Houdini final
#####################################################
################### Houdini Final ###################
#####################################################

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
    #slurp_term()
    # load_from_config()
    pass

#endregion
#endregion
#region WORK SETUP METHODS
#region config files

def convert_env_dict_to_string():

    new_d = {}

    for k, v in env_dict.items():

        new_d[k]=v
        if v is not isinstance(v, str):

            new_v = str(v)
            new_d[k]=new_v

    return(new_d)


def convert_env_dict_to_path():
    new_d = {}
    for k, v in env_dict.items():

        if isinstance(v, str):

            new_v = pathlib.Path(v)

            new_d[k]=new_v
        else:

            new_d[k]=v

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
    

#region Config setup

def create_config_files():
    path = CONFIG
    print(path)
    write_to_env_file()
    #write_to_json()

#endregion
#region User data

#TODO finish caching user data

def user_info():
    user_choice = input(
        'Please enter your name. '
    ).lower()
    user_confirm = input(
        f'Is {user_choice} correct? y/n: '
    ).lower()
    if user_confirm == 'y':
        return user_choice
    elif user_confirm == 'n':
        user_info()


def project_settings_file(fp):
    # config stuff

    try:
        if is_file_empty(fp):
            #print('file is empty...')
            pass

        else:
            pass


    except FileNotFoundError:
        print('creating project config file...')
        fp.open("w",encoding="utf-8")
        
        project_settings_file(fp)
    # with fp.open("w",encoding="utf-8") as f:
    # for key, value in path_d.items():
    #     f.write('%s="%s:&"\n' % (key, value))

def read_write_project_data(func):
    def inner(fp,dict):
        pass

def user_init(configpath):
    namelist = []
    namedict = []
    user = user_info()
    add_to_dict_and_arr('USER',user)
    fp = pathlib.Path(configpath)/'.projectdata.yaml'
    project_settings_file(fp)

def is_file_empty(file_name) -> bool:
    """ Check if file is empty by reading first character in it"""
    # open ile in read mode
    with open(file_name, 'r') as read_obj:
        # read first character
        one_char = read_obj.read(1)
        # if not fetched then file is empty
        if not one_char:
            return True
    return False
#endregion

#endregion
#region Check 3rd party software
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
#endregion
#region SHOTS
#region Directory Definitions

###########################################
########### folder dir lists ##############
###########################################

#region global dir definitions

###################################################
############# Global resource dirs ################
###################################################



'''project root global asset directories'''
global_asset_child_dir_namelist = [
    'SRC',
    'GEO',
    'BLEND',
    'TEXTURE',
    'HDA',
    'OTHER',
    'PDG',
    'USD',
    'POST_PRODUCTION',
]



###### POST stuff
global_asset_post_dir_namelist = [
    'Audio',
    'Compositing',
    'Reference',
    'Texture',
    'Project_Files',
    'Nuke',
    'Other',
    'Export'

]

post_comp_dir_namelist = [
    'LUTs',
    'Color_Scripts',
    'Project_Files',
    'Other'
    'Export'
]

post_audio_dir_namelist = [
    'SFX',
    'Music',
    'Reference',
    'Project_Files',
    'Other'
]

post_tex_dir_namelist = [
    'Data_Textures',
    'Alphas',
    'Masks',
    'PBR',
    'Grunge',
    'Substance'
    'Project_Files'
    'Other'
]

# Global Post folder

global_post_dir_namelist = [
    'Audio',
    'Compositing',
    'Reference',
    'Texture',
    'Project_Files',
    'Nuke',
    'Render',
    'Shots',
    'Scenes',
    'Other',
    'Export'
]

post_app_list = [
    'Fusion',
    'Nuke',
    'Resolve',
    'Adobe'
]

tex_app_list = [
    'Affinity',
    'Adobe',
    'Krita',
    'Gimp',
    'Other'
]

audio_app_list = [
    'Pro_Tools',
    'Ableton',
    'Bitwig',
    'Reaper',
    'Reason',
    'Other'
]

comp_app_list = [
    'Fusion',
    'Resolve',
    'Nuke',
    'Adobe'
]

######## CG stuff
'''global src subdirectories'''
global_src_dir_namelist = [
    'BLENDER',
    'MAYA',
    'ZBRUSH',
    'SUBSTANCE',
    'OTHER'
]
'''global geo subdirectories'''
global_geo_dir_namelist = [
    'FBX',
    'OBJ',
    'HOUDINI',
    'USD',
    'CACHE',
    'OTHER'
]
'''global texture subdirectories'''
global_tex_dir_namelist = [
    'HDRI',
    'IMPERFECTIONS',
    'PBR',
    'DATASETTEX',
    'DECALS',
    'SUBSTANCE',
    'OTHER'
]



#region Post Production setup

# def init_folders(path,name,subdirs,add_to_dict,pref,key):
#     parent = Path(path)/name
#     create_dir_if_not_present(parent)
#     try:
#         #if subdirs is not None:
#         add_readme_file_to_dir(parent)
        
#         #else:
#         #    pass
#     except ValueError:
#         pass
#     try:
#         if(add_to_dict == True):
#             try:
#                 add_to_dict_and_arr(key,parent)
#             except ValueError:
#                 pass
#     except ValueError:
#         pass
#     try:
#         subdirlist = create_dirs_from_list(parent,subdirs)
#         try:
#             add_dirlist_to_dict(subdirlist,pref)
#         except ValueError:
#             pass
#     except ValueError:
#         pass

#region init folder helper functions

def init_folder(parent_path,name):
    path = pathlib.Path(parent_path)/name
    create_dir_if_not_present(path)
    add_readme_file_to_dir(path)
    return path

def init_nested_folder(parent_path,dirlist):
    return create_dirs_from_list(parent_path,dirlist)

def register_init_folder(path,key):
    add_var_to_dict(key,path)

def register_nested_folders(dirlist,prefix,env=False):
    key = ''
    upper = []
    add_dirlist_to_dict()
    if (env == True):
        for i in dirlist:
            new_name = str(i.name).upper()
            sliced_path = i.parts[:-1]
            new_path = pathlib.Path(sliced_path)/new_name
            upper.append(new_path)
        add_dirlist_to_dict(upper,prefix)
    else:
        add_dirlist_to_dict(dirlist,prefix)

#endregion
###########

def init_post_production():


# post_tex_dir_namelist = [
#     'Data_Textures',
#     'Alphas',
#     'Masks',
#     'PBR',
#     'Grunge',
#     'Substance'
#     'Project_Files'
#     'Other'
# ]

    proj_root = pathlib.Path(REPO_ROOT)/'Main_Project'

    # create post production folder
    post_prod_path = pathlib.Path(proj_root)/'Post_Production'
    create_dir_if_not_present(post_prod_path)
    add_readme_file_to_dir(post_prod_path)
    add_to_dict_and_arr('G_POST_PRODUCTION',post_prod_path)

    # Config Global Post Production subdirs
    g_post_subdirlist = create_dirs_from_list(post_prod_path,global_post_dir_namelist)
    #add_files_to_empty_folders(g_post_subdirlist)

    post_proj = Path(post_prod_path)/'Project_Files'
    create_dir_if_not_present(post_proj)
    add_readme_file_to_dir(post_proj)
    post_proj_dirs = create_dirs_from_list(post_proj,post_app_list)
    add_files_to_empty_folders(post_proj_dirs)

    # child dirs
    # audio
    aud_dir = Path(post_prod_path)/'Audio'
    create_dir_if_not_present(aud_dir)
    add_readme_file_to_dir(aud_dir)
    aud_dirs = create_dirs_from_list(aud_dir,post_audio_dir_namelist)
    add_files_to_empty_folders(aud_dirs)
    #sub
    aud_proj = Path(aud_dir)/'Project_Files'
    create_dir_if_not_present(aud_proj)
    add_readme_file_to_dir(aud_proj)
    aud_proj_dirs = create_dirs_from_list(aud_proj, audio_app_list)
    add_files_to_empty_folders(aud_proj_dirs)

    #comp
    comp_dir = Path(post_prod_path)/'Compositing'
    create_dir_if_not_present(comp_dir)
    add_readme_file_to_dir(comp_dir)
    comp_dirs = create_dirs_from_list(comp_dir,post_comp_dir_namelist)
    add_files_to_empty_folders(comp_dirs)
    #sub
    comp_proj = Path(comp_dir)/'Project_Files'
    create_dir_if_not_present(comp_proj)
    add_readme_file_to_dir(comp_proj)
    comp_proj_dirs = create_dirs_from_list(comp_proj,comp_app_list)
    add_files_to_empty_folders(comp_proj_dirs)

    #tex
    tex_dir = Path(post_prod_path)/'Texture'
    create_dir_if_not_present(tex_dir)
    add_readme_file_to_dir(tex_dir)
    tex_dirs = create_dirs_from_list(tex_dir,post_tex_dir_namelist)
    add_files_to_empty_folders(tex_dirs)

    #sub
    

    #proj
    tex_proj = Path(tex_dir)/'Project_Files'
    create_dir_if_not_present(tex_proj)
    add_readme_file_to_dir(tex_proj)
    tex_proj_dirs = create_dirs_from_list(tex_proj,tex_app_list)
    add_files_to_empty_folders(tex_proj_dirs)

    full_dirlist = dir
    add_files_to_empty_folders(g_post_subdirlist)




def init_asset_post_production():
    assets_dir = pathlib.Path(REPO_ROOT)/'Main_Project/Assets'
    post_dir = pathlib.Path(assets_dir)/'POST_PRODUCTION'
    create_dir_if_not_present(post_dir)
    add_readme_file_to_dir(post_dir)
    
    # ++++++++++

    g_asset_post_subdir_list = create_dirs_from_list(post_dir,global_asset_post_dir_namelist)
    
    add_files_to_empty_folders(g_asset_post_subdir_list)
    #add_dirlist_to_dict()

    #
    


#endregion
#endregion
#region shot subdir definition

#TODO change this to json
#TODO add R&D to shots

###########################################
##############               ##############
############     Shot Prep     ############
##############               ##############
###########################################

'''shot subdirectories'''
shot_subdir_names = [
    "GEO",
    "SRC",
    "HIP",
    "RENDER",
    "TEXTURE",
    "BLEND",
    "ASSETS",
    "HDA",
    "PDG",
    "USD",
    "REFERENCE",
    "RESEARCH_AND_DEVELOPMENT",
    "LOOKDEV"
    "POST_PRODUCTION",
    "FINAL",
    "OTHER"
]

# Post fx shot stuff
shot_post_dirnames = [
    'Audio',
    'Compositing',
    'Editing',
    'Texture',
    'Project_Files'
    'Export'
]

shot_audio_dirnames = [
    'SFX',
    'Music',
    'Reference',
    'Project_Files',
]

shot_comp_dirnames = [
    'LUTs',
    'Color_Scripts',
    'Project_Files',
    'Fusion',
    'Nuke',
    'Adobe',
    'Other',
    'Export'
]


shot_tex_post_dirnames = [
    'Data_Textures',
    'Alphas',
    'Masks',
    'PBR',
    'Grunge',
    'Substance'
    'Project_Files'
    'Other'
]



####
shots_list = []
shot_env_dict = {}
#endregion
#endregion

def create_shot():
    '''
    Check if first shot folder exists, if not, create it. If folders exists count them and create a new one incremented
    '''
    #ensure top-level 'shots' exists
    #top_level_shot = Path(Path(Path.cwd().parent)) / "Main_Project/shots"
    top_level_shot = Path(PROJECT_ROOT) / "Main_Project/Shots"
    if not Path.is_dir(top_level_shot):
        Path.mkdir(top_level_shot)

    #case 1 - creating first shot directory
    first_shot_n = Path("./Main_Project/Shots/shot_1")
    if not Path.is_dir(first_shot_n):
        Path.mkdir(first_shot_n)
        shot_subfolders = create_shot_subfolders(first_shot_n)


        print(f'{first_shot_n.name} created...')
        
        add_to_dict_and_arr('SHOT_ROOT',first_shot_n)
        
        shot_env_var_init(first_shot_n)
        print(f"\'{first_shot_n}\' created along with resource dirs.")
        return shot_subfolders
    #case 2 - creating any subsequent shot directory
    else:
        shot_n = first_shot_n
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
                raise Exception("!! couldn't increment appended folder number")

        #make the new shot directory...
        Path.mkdir(shot_n)
        shots_list.append(shot_n)
        #create resources for the new shot directory
        shot_subfolders = create_shot_subfolders(shot_n)
        
        add_to_dict_and_arr('SHOT_ROOT',shot_n)
        
        shot_env_var_init(shot_n)
        
        
        print(f"\'{shot_n}\' created along with resource dirs.")
        return shot_subfolders

def create_shot_subfolders(rootdir):
        dirlist = create_dirs_from_list(rootdir,shot_subdir_names)
        add_readme_file_to_dir(rootdir)

        subsubresdict = {
            'SRC':global_src_dir_namelist,
            'GEO':global_geo_dir_namelist,
            'TEXTURE':global_tex_dir_namelist
        }

        specresdict={}

        for a in dirlist:
            specresdict[a.name]=a
        for d in dirlist:
            for k, v in subsubresdict.items():
                if d.name == k:
                    curr_dir = specresdict[k]
                    print(f'creating subresource folders in {k}...')
                    subsubdirlist = create_dirs_from_list(specresdict[k],v)
                    add_readme_file_to_dir(specresdict[k])
                    add_files_to_empty_folders(subsubdirlist)

        add_files_to_empty_folders(dirlist)
        
        return dirlist



def shot_env_var_init(shot_root):
    add_readme_file_to_dir(shot_root)
    shot_resource_list = get_resource_paths(shot_root)
    
    shot_dict = add_dirlist_to_return_dict(shot_resource_list)
    print(shot_dict)




def subdir_list(shotroot):

    shots_only=[]
    sorted_shots=[]
    sorted_shot_names=[]
    shot_name_list=[]
    if any(Path(shotroot).iterdir()):

        for p in Path(shotroot).iterdir():
            if p.is_dir():
                shot_name_list.append(p.name)
        shots_only = [x for x in shot_name_list if re.match(r"^shot_\d+$", x)]
        sorted_shot_names = sorted(shots_only,key=lambda x: x.split('_')[1])
        #print(f'sorted shots::: {sorted_shot_names}')
        for p in sorted_shot_names:
            np = pathlib.Path(shotroot)/p
            sorted_shots.append(np)
    return sorted_shots


def no_subdirs(rootdir) -> bool:
    checklist=[]
    for p in pathlib.Path(rootdir).iterdir():
        checklist.append(p.is_dir())
    if True in checklist:
        return False
    else:
        return True


def open_shot():
    
    #case 1 - creating first shot directory
    shot_root = Path(PROJECT_ROOT)/"Main_Project/Shots"
    if not any(Path(shot_root).iterdir()):
        first_shot_n = Path(shot_root)/"shot_1"
        if not Path.is_dir(first_shot_n):
            Path.mkdir(first_shot_n)
            create_dirs_from_list(first_shot_n)
            print(f"\'{first_shot_n}\' created along with resource dirs.")
    #case 2 - select shot
    #count_subdirs(shot_root)

def choose_shot(pathlist):
    choices = []
    choice = ''
    for i in range(len(pathlist)):
        print(f'{i+1} = {pathlist[i].name}')
        choices.append(i+1)
    print(f'Choices:: {choices}')
    user_choose_shot(choices)

def user_choose_shot(list):
    # returns
    choice = 0
    confirm = False
    # other
    inner_confirm = True
    #result = ''
    while True:
        try:
            choice = int(input('Please type the corresponding number of the shot you wish to open: '))
            result = check_if_num_in_list(choice,list)
            if (result == True):
                print(f'You chose shot_{choice}')
                while inner_confirm:
                    try:
                        #accepted_input = ['y','n']
                        user_confirm = input(
                            'Is this correct? y/n: '
                        ).lower()
                        if (user_confirm == 'y' or 'n'):
                            if(user_confirm == 'y'):
                                confirm = True
                                inner_confirm = False
                            elif(user_confirm == 'n'):
                                confirm = False
                                inner_confirm = False
                            else:
                                print('Invalid response, try again...')
                                continue                           
                            
                        else:
                            print('Invalid response, try again...')
                            continue
                    except ValueError:
                        print('Invalid response, try again...')
                        continue
                print(f'you said {confirm}')
                if(confirm == True):
                    break
                elif(confirm == False):
                    break
            else:
                print('Invalid response, try again...')
                continue
        except ValueError:
            print('Invalid response, try again...')
            continue
    return choice, confirm

        
def check_if_num_in_list(num,list) -> bool:
    result = False
    total = len(list)
    if (num > 0) and (num < len(list)+1):
        result = True
    else:
        result = False
    return result


def shot_decision():
    shots_root = pathlib.Path(pathlib.Path.cwd())/'Main_Project/Shots'
    shot_root_empty = no_subdirs(shots_root)
    shot_root = ''
    user_choice = input(
        '1 - Create a new shot \n2 - Open existing shot \n'
    ).lower()
    # Case 1 
    if user_choice == '1':
        print('creating new shot....')

        shot_folders = create_shot()
        shotlist = subdir_list(shots_root)
        choose_shot(shotlist)
        # select shot
        # then houdini stuff
    # case 2
    elif user_choice == '2':
        print('please choose which shot to open...')
        if no_subdirs(shots_root):
            shot_folders = create_shot()
        else:
            shotlist = subdir_list(shots_root)
            choose_shot(shotlist)

        # if no shot exists create it
        # since there would only be one select that folder
        # then go to houdini stuff
    else:
        print('please type 1 or 2 and hit enter....')
        shot_decision()


def count_subdirs(rootdir):
    total = ''
    subdirlist = []
    total = len(os.walk(rootdir).next()[1])
    #print(total)
    return total



def shot_print():
    pass





def get_resource_paths(curr_path):
    path = curr_path
    path_list = []
    for p in Path(path).iterdir():
        if(p.is_dir()==True):
            #print(f'creating {p.name} directory...')
            path_list.append(p)
        else:
            #print('file')
            continue
    print(path_list)
    return path_list

    # resource_paths = [i[0] for i in os.walk(
    #     curr_path) if pathlib.Path.name(str(i[0])) in shot_subdir_names]
    # return resource_paths



#endregion
#region path setup
#region Post Production Setup




#endregion
##############################################
############## Get Initialized ###############
##############################################



def get_initial_paths():
    new_folders = []
    # config stuff
    CONFIG = create_config_dir()

    # TODO: research and development init

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
    create_dir_if_not_present(pathlib.Path(REPO_ROOT,"Main_Project"))
    PROJECT_ROOT = pathlib.Path(REPO_ROOT,"Main_Project")
    add_to_dict_and_arr("PROJECT_ROOT",PROJECT_ROOT)

    #persistent config
    pers_config_dir = pathlib.Path(PROJECT_ROOT)/'.config'
    PROJECT_CONFIG = create_dir_if_not_present(pers_config_dir)
    add_to_dict_and_arr('PROJECT_CONFIG',pers_config_dir)


    # User stuff
    user_init(pers_config_dir)


    # Global Assets Root
    create_dir_if_not_present(pathlib.Path(PROJECT_ROOT,"assets"))
    ASSETS_GLOBAL_ROOT = pathlib.Path(PROJECT_ROOT,"assets")
    add_readme_file_to_dir(ASSETS_GLOBAL_ROOT)
    add_to_dict_and_arr("ASSETS_GLOBAL_ROOT",ASSETS_GLOBAL_ROOT)
    ########## GLOB CHILD DIRS #############


    global_asset_child_dir_list = create_dirs_from_list(ASSETS_GLOBAL_ROOT,global_asset_child_dir_namelist)
    #print(global_asset_child_dir_list)
    #
    add_dirlist_to_dict(global_asset_child_dir_list,"G_")
    #print(env_dict)


    srcrootpath = pathlib.Path(ASSETS_GLOBAL_ROOT)/'SRC'
    global_src_dir_list = create_dirs_from_list(srcrootpath,global_src_dir_namelist)
    add_readme_file_to_dir(srcrootpath)
    add_files_to_empty_folders(global_src_dir_list)
    add_dirlist_to_dict(global_src_dir_list,'G_SRC_')

    georootpath = pathlib.Path(ASSETS_GLOBAL_ROOT)/'GEO'
    global_geo_dir_list = create_dirs_from_list(georootpath,global_geo_dir_namelist)
    add_readme_file_to_dir(georootpath)
    add_files_to_empty_folders(global_geo_dir_list)
    add_dirlist_to_dict(global_geo_dir_list,'G_GEO_')


    texrootpath = pathlib.Path(ASSETS_GLOBAL_ROOT)/'TEXTURE'
    global_tex_dir_list = create_dirs_from_list(texrootpath,global_tex_dir_namelist)
    add_readme_file_to_dir(texrootpath)
    add_files_to_empty_folders(global_tex_dir_list)

    add_dirlist_to_dict(global_tex_dir_list,'G_TEX_')

    #Post Production stuff
    postrootpath = pathlib.Path(ASSETS_GLOBAL_ROOT)/'POST_PRODUCTION'
    global_post_asset_dir_list = create_dirs_from_list(postrootpath,global_post_asset_dir_list)
    add_readme_file_to_dir(postrootpath)

    #add setup here

    #empty files to empty folders global assets
    add_files_to_empty_folders(global_asset_child_dir_list)

    # PACKAGES
    PACKAGES = pathlib.Path(PROJECT_ROOT,"packages")
    create_dir_if_not_present(PACKAGES)
    add_readme_file_to_dir(PACKAGES)
    add_to_dict_and_arr("HOUDINI_PACKAGE_DIR",PACKAGES)

    # SHOT ROOT
    SHOTS_ROOT = pathlib.Path(PROJECT_ROOT,"Shots")
    create_dir_if_not_present(SHOTS_ROOT)
    add_readme_file_to_dir(SHOTS_ROOT)
    add_to_dict_and_arr("SHOTS_ROOT",SHOTS_ROOT)
    
    init_post_production()
    #createShotDir(SHOTS_ROOT)

    add_to_dict_and_arr('INITIALIZED','TRUE')
#endregion
#endregion
#region EXECUTE

def main():
    indie_check()
    get_initial_paths()
    #print(CONFIG)
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
