import os
from pathlib import Path
import pandas as pd
import tkinter.filedialog as filedialog

import sse_bsa

import config, update

def sanitize_cache():

    cfg = config.require_config()

    # make sure all our resource files are available
    if (not os.path.exists(Path("src") / "resources" / "vanilla_projects.txt")):
        print("Error: Source files corrupt! You may need to reinstall SkyCAT SE.")
        os.system('pause')
        return

    # prompt the user to navigate to the Skyrim SE directory
    if not os.path.exists(cfg.skyrim) or not os.path.exists(cfg.skyrim / "meshes" / "animationdatasinglefile.txt") or not os.path.exists(cfg.skyrim / "meshes" / "animationdatasinglefile.txt"):
        new_path = filedialog.askdirectory(title="Select Skyrim SE Data folder.", mustexist=True)
        cfg.write_to_config('PATHS', 'sPathSSE', new_path)

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
    if os.path.exists(cfg.skyrim / "meshes" / "animationdata" / f"{project_name}.txt"):
        has_animdata = True
       
    # check for boundanims file if expected
    if os.path.exists(cfg.skyrim / "meshes" / "animationdata" / "boundanims" / f"anims_{project_name}.txt"):
        has_boundanims = True

    # check for animsetdata file
    if os.path.exists(cfg.skyrim / "meshes" / "animationsetdata" / f"{project_name}data" / f"{project_name}.txt"):
       has_animsetdata = True 
    return [has_animdata, has_boundanims, has_animsetdata]

def is_creature(project_name):
    cfg = config.require_config()
    ud = update.require_update()

    animdata_csv = pd.read_csv(cfg.cache / config.animdata_csv_path)
    creaturelist = animdata_csv[animdata_csv['project_type'] == "creature"]['project_name'].tolist()
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
    cfg = config.require_config()

    anims_archive = sse_bsa.BSAArchive(Path(cfg.skyrim / "Skyrim - Animations.bsa"))
    anims_archive.extract_file(Path("meshes") / "animationdatasinglefile.txt", Path(cfg.skyrim))
    anims_archive.extract_file(Path("meshes") / "animationsetdatasinglefile.txt", Path(cfg.skyrim))
    return 0

def clean_temp():
    cfg = config.require_config()
    temp_path = cfg.cache / "temp"
    if os.path.exists(temp_path):
        for root, dirs, files in os.walk(temp_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_path)
    else:
        return None
    return 0

def get_path_case_insensitive(source: Path):
    parent = source.parent
    target_name = source.name.casefold()
    try:
        for child in parent.iterdir():
            if child.name.casefold() == target_name:
                return child
    except FileNotFoundError:
        return None

def count_lines_and_strip(file):

    with open(file, 'r', encoding="utf-8") as rfile:
        line_count = 0

        # count total lines in file
        for count, line in enumerate(rfile):
            line_count = count

        rfile.seek(0)

        # count lines in file up to our recorded line count
        for _ in range(line_count):
            
            line = rfile.readline()

            # check if we're at the end of the file and the last line is blank
            if rfile.tell() == os.fstat(rfile.fileno()).st_size and line.strip() == "\n":
                line_count -= 1

                # return to the top
                rfile.seek(0)

    return line_count


def helper_function():
    unpack_vanilla_cache()
    ud = update.require_update()
    ud.update_all()
    import append
    append.append_projects(['shalkproject'])
    return 0