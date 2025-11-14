import os
import configparser
from pathlib import Path
import pandas as pd
import tkinter.filedialog as filedialog

import sse_bsa

import config, update

def sanitize_cache():

    cfg = config.require_config()

    cfgparser = configparser.ConfigParser()

    # make sure all our resource files are available
    if (not os.path.exists("src\\resources\\vanilla_projects.txt")):
        print("Error: Source files corrupt! You may need to reinstall SkyCAT SE.")
        os.system('pause')
        return

    # prompt the user to navigate to the Skyrim SE directory
    if not os.path.exists(cfg.skyrim) or not os.path.exists(cfg.skyrim + "\\meshes\\animationdatasinglefile.txt") or not os.path.exists(cfg.skyrim + "\\meshes\\animationdatasinglefile.txt"):
        new_path = filedialog.askdirectory(title="Select Skyrim SE Data folder.", mustexist=True)
        cfg.write_to_config(cfgparser, 'PATHS', 'sPathSSE', new_path)

    # make sure the animation cache is unpacked from the bsa.
    if not os.path.exists(cfg.skyrim + "\\meshes\\animationdatasinglefile.txt") or not os.path.exists(cfg.skyrim + "\\meshes\\animationdatasinglefile.txt"):
        
        # if we are missing the animations bsa entirely, abort.
        if not os.path.exists(cfg.skyrim + "\\Skyrim - Animations.bsa"):
            print("Error: could not find Skyrim - Animations.bsa. Please verify integrity of game files.")
            os.system('pause')
            return


        to_next = False
        while to_next == False:
            print("Animation cache appears to be missing. Unpack? Y/N")
            response = input().lower()
            match response:
                case 'y':
                    # unpack the necessary files
                    unpack_vanilla_cache(cfg)
                    to_next = True
                    
                case 'n':
                    print("Warning: SkyCAT SE cannot operate without a valid cache.")
                    os.system('pause')
                    return
    if not os.path.exists(cfg.cache):
        os.makedirs(cfg.cache)

    return True

# validate entire cache
def validate_cache():
    cfg = config.require_config()
    # check animdata cache:
    # get expected project count from readline()
    # count actual projects in cache
    # if there is an integer too early or late, return false (project count mismatch)
    # for each project in animdata cache
        
        # get expected line count from readline()
        # count hkx files, check if it matches expected count
        # record if creature or not
        
    pass
        
    # check animsetdata cache:
    pass

# validate loose project files
def validate_animdata(creature_folder, project_name):
    cfg = config.require_config()
    # expected structure:
    # 1								  --- Unsure always seems to be 1, skip
    # 3							      --- How many hkx files associated with this project (directly below this line)
    # Behaviors\ChickenBehavior.hkx   --- Behaviour files
    # Characters\ChickenCharater.hkx  --- Character file
    # Character Assets\skeleton.HKX   --- Skeleton
    # 1					              --- 0 = not creature, 1 = creature

    # skip first line, always 1
    # record expected hkx count from second line
    # count actual hkx files listed
    # make sure behavior files are available in creaturefolder ()
    # make sure there's only one characters line and it matches a hkx in creaturefolder
    # make sure there's only one skeleton line and it matches a hkx in creaturefolder
    # record if creature or not from next line

    pass

def validate_boundanims(creature_folder, expected_anims):
    # get expected animation count from creaturefolder/animations
    # count each section and match to expected animation count
    # (each section is separated by an empty newline)
    pass

def validate_animsetdata():
    pass

def is_in_cache(project_name):
    ud = update.require_update()
    
    if project_name in ud.cached_projects:
        return True
    return False

def is_unpacked(project_name):
    cfg = config.require_config()

    has_animdata = False
    has_boundanims = False
    has_animsetdata = False

    # check for animdata file
    if os.path.exists(cfg.skyrim + f"\\meshes\\animationdata\\{project_name}.txt"):
        has_animdata = True
       
    # check for boundanims file if expected
    if os.path.exists(cfg.skyrim + f"\\meshes\\animationdata\\boundanims\\anims_{project_name}.txt"):
        has_boundanims = True

    # check for animsetdata file
    if os.path.exists(cfg.skyrim + f"\\meshes\\animationsetdata\\{project_name}data\\{project_name}.txt"):
       has_animsetdata = True 
    return [has_animdata, has_boundanims, has_animsetdata]

def is_creature(project_name):
    ud = update.require_update()

    animdata_csv = pd.read_csv(ud.animdata_csv)
    creaturelist = animdata_csv[animdata_csv['is_creature'] == 1]['project_name'].tolist()
    if project_name in creaturelist:
        return True
    return False

def can_be_merged(project_name):
    # check if project is in cache
    if is_in_cache(project_name) == True:
        print(f"Warning: {project_name} must be unique.")
        return False
    
    unpacked = is_unpacked(project_name)

    if unpacked[0]:
        # if animdata with boundanims and not animsetdata, or vice versa, return false
        if unpacked[1] and not unpacked[2] or unpacked[2] and not unpacked[1]:
            return False
        
        # if animdata with no boundanims or animsetdata, return true
        if not unpacked[1] and not unpacked[2]:
            return True
        
        # if everything is unpacked, return true
        if unpacked[0] and unpacked[1] and unpacked[2]:
            return True
    # if no animdata, return false
    return False

def unpack_vanilla_cache():
    cfg = config.require_config()

    anims_archive = sse_bsa.BSAArchive(Path(cfg.skyrim + "\\skyrim - animations.bsa"))
    anims_archive.extract_file("meshes\\animationdatasinglefile.txt", Path(cfg.skyrim))
    anims_archive.extract_file("meshes\\animationsetdatasinglefile.txt", Path(cfg.skyrim))
    return 0