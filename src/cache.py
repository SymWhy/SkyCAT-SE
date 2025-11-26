from datetime import datetime
import os
from pathlib import Path
from tkinter import filedialog
import logging
import shutil

import config, errors, system, util

def sanitize_cache():

    import config

    cfg = config.get_global('config')

    yes_im_sure = config.get_global('yesimsure')

    # make sure temp folder is empty
    system.clean_temp()

    vanilla_projects_path = util.resource_path(Path("resources") / "vanilla_projects.txt")
    # make sure all our resource files are available
    if not vanilla_projects_path.exists():
        raise FileNotFoundError("Failed to find vanilla_projects.txt")

    # prompt the user to navigate to the Skyrim SE directory if configured path
    # does not exist. (Fix previous double-negative logic.)
    if not cfg.skyrim.exists() or not util.check_valid_directory(cfg.skyrim):
        cfg.setup_config()

    try:      
        os.makedirs(cfg.cache, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise OSError(f"Could not make cache directory: {e}") from e
    return True

def is_in_cache(project_name: str):
    ud = config.get_global('update')
    
    if project_name.casefold() in ud.cached_projects:
        return True
    return False

def is_unpacked(project_name: str):
    cfg = config.get_global('config')

    has_animdata = False
    has_boundanims = False
    has_animsetdata = False

    # check for animdata file
    if (cfg.skyrim / "meshes" / "animationdata" / f"{project_name}.txt").exists():
        has_animdata = True
       
    # check for boundanims file if expected
    if (cfg.skyrim / "meshes" / "animationdata" / "boundanims" / f"anims_{project_name}.txt").exists():
        has_boundanims = True

    # check for animsetdata file
    if (cfg.skyrim / "meshes" / "animationsetdata" / f"{project_name}data" / f"{project_name}.txt").exists():
       has_animsetdata = True 
    return [has_animdata, has_boundanims, has_animsetdata]

def is_creature(project_name: str):
    cfg = config.get_global('config')
    ud = config.get_global('update')

    animdata_list = ud.animdata_list

    creaturelist = []
    for entry in animdata_list:
        if entry['project_type'] == "creature":
            creaturelist.append(entry['project_name'])

    if project_name in creaturelist:
        return True
    return False

def can_be_merged(project_name: str):
    # check if project is in cache
    if is_in_cache(project_name) == True:
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
    logging.warning(f"Warning: {project_name} does not exist.")
    return False



def restore_vanilla_cache():
    cfg = config.get_global('config')
    ud = config.get_global('update')    
    yes_im_sure = config.get_global('yesimsure')

    if not yes_im_sure:
        if util.prompt_yes_no("This will overwrite your current animation cache with the vanilla cache. Continue?",
                              message_y="Restoring vanilla cache.",
                              message_n="Cancelling operation.") or yes_im_sure:
            util.unpack_vanilla_cache(cfg.skyrim)
    else:
        util.unpack_vanilla_cache(cfg.skyrim)

    if ud.update_cache() != 0:
        raise errors.CacheError(message="Failed to update after restoring vanilla cache.")

    logging.info("Vanilla cache restored.")
    return

def get_creature_projects(list_projects: list[str]):
    cfg = config.get_global('config')
    project_dict = {}

    for project in list_projects:

        # presumably has animdata if it's in the list
        has_boundanims = False
        has_animsetdata = False
    
        # check for boundanims file if expected
        if (cfg.skyrim / "meshes" / "animationdata" / "boundanims" / f"anims_{project}.txt").exists():
            has_boundanims = True

        # check for animsetdata file
        if (cfg.skyrim / "meshes" / "animationsetdata" / f"{project}data" / f"{project}.txt").exists():
            has_animsetdata = True 

        if (has_boundanims and not has_animsetdata) or (has_animsetdata and not has_boundanims):
            # broken project, return error
            raise FileNotFoundError(f"{project} is missing files!")

        project_dict[project] = True if has_boundanims and has_animsetdata else False
        
    return project_dict

def count_mergeable_projects():
    
    cfg = config.get_global('config')
    
    animdata_dir = cfg.skyrim / config.animdata_dir

    mergeable_projects = []

    for file in os.listdir(animdata_dir):
        # note, assuming all txt files in animationdata are projects, save for dirlist.txt
        # in the future we will have a validation check here
        if file.endswith(".txt") and not file == "dirlist.txt":
            project_name = file[:-4]  # remove .txt extension
            if can_be_merged(project_name):
                mergeable_projects.append(project_name)


def dump_cache():
    cfg = config.get_global('config')
    ud = config.get_global('update')
    dump_dir = cfg.cache / "dump"
    util.dump_json(ud.animdata_list, cfg.cache, dump_dir / f"animdata_cache_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    util.dump_json(ud.animsetdata_list, cfg.cache, dump_dir / f"animsetdata_cache_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    logging.info("Dumped animdata and animsetdata to JSON.")
    return 0

def copy_cache(dst_path: Path):
    cfg = config.get_global('config')
    
    try:
        os.makedirs(dst_path, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise errors.WriteError(path=str(dst_path), message=f"Could not create destination directory: {e}") from e
    
    try:
        shutil.copy2(cfg.skyrim / "meshes" / "animationdatasinglefile.txt", dst_path / "animationdatasinglefile.txt")
        shutil.copy2(cfg.skyrim / "meshes" / "animationsetdatasinglefile.txt", dst_path / "animationsetdatasinglefile.txt")
    except (OSError, PermissionError) as e:
        raise errors.WriteError(path=str(dst_path), message=f"Could not copy cache files: {e}") from e
    logging.info("Copied cache files to temp directory.")
    return 0
    