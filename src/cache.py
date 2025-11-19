import os
from pathlib import Path
from tkinter import filedialog

import sse_bsa

import config

def sanitize_cache():

    import config

    cfg = config.get_global('config')

    # make sure all our resource files are available
    if (not os.path.exists(Path("src") / "resources" / "vanilla_projects.txt")):
        print("Error: Source files corrupt! You may need to reinstall SkyCAT SE.")
        os.system('pause')
        return

    # prompt the user to navigate to the Skyrim SE directory
    if not os.path.exists(cfg.skyrim) or not os.path.exists(cfg.skyrim / "meshes" / "animationdatasinglefile.txt") or not os.path.exists(cfg.skyrim / "meshes" / "animationdatasinglefile.txt"):
        new_path = filedialog.askdirectory(title="Select Skyrim SE Data folder.", mustexist=True)
        cfg.write_to_config('PATHS', 'sPathSSE', str(new_path))

    # make sure the animation cache is unpacked from the bsa.
    if not os.path.exists(cfg.skyrim / "meshes" / "animationdatasinglefile.txt") or not os.path.exists(cfg.skyrim / "meshes" / "animationdatasinglefile.txt"):
        
        # if we are missing the animations bsa entirely, abort.
        if not os.path.exists(cfg.skyrim / "Skyrim - Animations.bsa"):
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
                    unpack_vanilla_cache()
                    to_next = True
                    
                case 'n':
                    print("Warning: SkyCAT SE cannot operate without a valid cache.")
                    os.system('pause')
                    return
    if not os.path.exists(cfg.cache):
        os.makedirs(cfg.cache)

    return True

def is_in_cache(project_name: str):
    ud = config.get_global('update')
    
    if project_name in ud.cached_projects:
        return True
    return False

def is_unpacked(project_name: str):
    cfg = config.get_global('config')

    has_animdata = False
    has_boundanims = False
    has_animsetdata = False

    # check for animdata file
    if os.path.exists(cfg.skyrim / "meshes" / "animationdata" / f"{project_name}.txt"):
        has_animdata = True
       
    # check for boundanims file if expected
    if os.path.exists(cfg.skyrim / "meshes" / "animationdata" / "boundanims" / f"anims_{project_name}.txt"):
        has_boundanims = True

    # check for animsetdata file
    if os.path.exists(cfg.skyrim / "meshes" / "animationsetdata" / f"{project_name}data" / f"{project_name}.txt"):
       has_animsetdata = True 
    return [has_animdata, has_boundanims, has_animsetdata]

def is_creature(project_name: str):
    cfg = config.get_global('config')
    ud = config.get_global('update')

    animdata_df = ud.animdata_df
    creaturelist = animdata_df[animdata_df['project_type'] == "creature"]['project_name'].tolist()
    if project_name in creaturelist:
        return True
    return False

def can_be_merged(project_name: str):
    # check if project is in cache
    if is_in_cache(project_name) == True:
        print(f"Warning: {project_name} must be unique.")
        return False
    
    unpacked = is_unpacked(project_name)

    if unpacked[0]:
        # if animdata with boundanims and not animsetdata, or vice versa, return false
        if unpacked[1] and not unpacked[2] or unpacked[2] and not unpacked[1]:
            print(f"Warning: {project_name} is missing files.")
            return False
        
        # if animdata with no boundanims or animsetdata, return true
        if not unpacked[1] and not unpacked[2]:
            return True
        
        # if everything is unpacked, return true
        if unpacked[0] and unpacked[1] and unpacked[2]:
            return True
    # if no animdata, return false
    print(f"Warning: {project_name} does not exist.")
    return False

def unpack_vanilla_cache():
    cfg = config.get_global('config')

    anims_archive = sse_bsa.BSAArchive(Path(cfg.skyrim / "Skyrim - Animations.bsa"))
    anims_archive.extract_file(Path("meshes") / "animationdatasinglefile.txt", Path(cfg.skyrim))
    anims_archive.extract_file(Path("meshes") / "animationsetdatasinglefile.txt", Path(cfg.skyrim))
    return 0

def get_creature_projects(list_projects: list[str]):
    cfg = config.get_global('config')
    project_dict = {}

    for project in list_projects:

        # presumably has animdata if it's in the list
        has_boundanims = False
        has_animsetdata = False
    
        # check for boundanims file if expected
        if os.path.exists(cfg.skyrim / "meshes" / "animationdata" / "boundanims" / f"anims_{project}.txt"):
            has_boundanims = True

        # check for animsetdata file
        if os.path.exists(cfg.skyrim / "meshes" / "animationsetdata" / f"{project}data" / f"{project}.txt"):
            has_animsetdata = True 

        if has_boundanims and not has_animsetdata or has_animsetdata and not has_boundanims:
            # broken project, return error
            print(f"Error: {project} is missing files!")
            return None

        project_dict[project] = has_boundanims and has_animsetdata
        
    return project_dict

def count_mergeable_projects():
    
    cfg = config.get_global('config')
    
    animdata_dir = cfg.skyrim + config.animdata_dir

    mergeable_projects = []
    for file in os.listdir(animdata_dir):
        # note, assuming all txt files in animationdata are projects, save for dirlist.txt
        # in the future we will have a validation check here
        if file.endswith(".txt") and not file == "dirlist.txt":
            project_name = file[:-4]  # remove .txt extension
            if can_be_merged(project_name):
                mergeable_projects.append(project_name)