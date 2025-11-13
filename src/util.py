import os
from pathlib import Path
import pandas as pd
import tkinter.filedialog as filedialog

import sse_bsa

def sanitize_cache(cfg, cfgparser):

    # make sure all our resource files are available
    if (not os.path.exists("src\\resources\\vanilla_projects.txt")):
        print("Error: Source files corrupt! You may need to reinstall SkyCAT SE.")
        os.system('pause')
        return

    # prompt the user to navigate to the Skyrim SE directory
    if not os.path.exists(cfg.skyrim):
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
                    anims_archive = sse_bsa.BSAArchive(Path(cfg.skyrim + "\\skyrim - animations.bsa"))
                    anims_archive.extract_file("meshes\\animationdatasinglefile.txt", Path(cfg.skyrim))
                    anims_archive.extract_file("meshes\\animationsetdatasinglefile.txt", Path(cfg.skyrim))
                    to_next = True
                    
                case 'n':
                    print("Warning: SkyCAT SE cannot operate without a valid cache.")
                    os.system('pause')
                    return
    if not os.path.exists(cfg.cache):
        os.makedirs(cfg.cache)

    return True

def is_in_cache(ud, project_name):
    if project_name in ud.cached_projects:
        return True
    return False

def is_creature(ud, project_name):
    animdata_csv = pd.read_csv(ud.animdata_csv)
    creaturelist = animdata_csv[animdata_csv['is_creature'] == 1]['project_name'].tolist()
    if project_name in creaturelist:
        return True
    return False

def can_be_merged(ud, cfg, project_name):
    # check if project is in cache
    if is_in_cache(ud, project_name):
        print(f"Warning: {project_name} must be unique.")
        return False
    
    # check for animdata file
    if not os.path.exists(cfg.skyrim + f"\\meshes\\animationdata\\{project_name}.txt"):
        print(f"Warning: Missing animation data file for {project_name}.")
        return False
    
    if is_creature(ud, project_name):

    # check for boundanims file if expected
        if not os.path.exists(cfg.skyrim + f"\\meshes\\animationdata\\boundanims\\anims_{project_name}.txt"):
            print(f"Warning: Missing boundanims file for creature {project_name}.")
            return False
    # check for animsetdata file
        if not os.path.exists(cfg.skyrim + f"\\meshes\\animationsetdata\\{project_name}data\\{project_name}.txt"):
            print(f"Warning: Missing animationset data file for creature {project_name}.")
            return False
    return True