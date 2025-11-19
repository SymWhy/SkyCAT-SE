import os
from pathlib import Path
from shutil import copy2
import pandas as pd

import config, cache, system, util

def append_projects(project_list: list[str]):
    cfg = config.get_global('config')
    ud = config.get_global('update')
    dryrun = config.get_global('dryrun')

    # ensure cache is up to date
    ud.update_cache()

    had_a_creature = False

    # //// PREPROCESSING ////

    # check if the project is available to be merged
    for project_name in project_list:
        if not cache.can_be_merged(project_name):
            print(f"Warning: {project_name} cannot be merged.")
            return
        
    # prompt user for confirmation of overwrite:
    print(f"Warning: This process will overwrite existing cache files. Is this okay? Y/N")
    while True:
        match input().lower():
            case 'y':
                extract_ok = True
                break
            case 'n':
                print(f"Cancelling operation.")
                extract_ok = False
                return

    # offer to back up the existing cache
    if os.path.exists(cfg.skyrim / config.animdata) or os.path.exists(cfg.skyrim / config.animsetdata):
        print(f"Would you like to back up the existing cache files? Y/N")
        while True:
            match input().lower():
                case 'y':
                    system.save_backup()
                    break
                case 'n':
                    print(f"Skipping backup.")
                    break


    if not os.path.exists(cfg.cache / config.animdata_json_path):
        print("Error: Can't find cache json.")
        return 1
    
    animdata_df = ud.animdata_df
    animsetdata_df = ud.animsetdata_df
    last_project_is_creature = cache.is_creature(animdata_df.iloc[-1]['project_name'])

    count_projects = len(animdata_df) + len(project_list)
    count_creatures = len(animsetdata_df)
    creatures_dict = cache.get_creature_projects(project_list)
    count_creatures += sum(1 for p in project_list if creatures_dict.get(p))


    # open old cache files
    old_animdata = cfg.skyrim / config.animdata
    old_animsetdata = cfg.skyrim / config.animsetdata
    
    # create temporary cache folder
    if not os.path.exists(cfg.cache / "temp"):
        os.makedirs(cfg.cache / "temp", exist_ok=True)

    temp_animdata = cfg.cache / "temp" / "animationdatasinglefile.txt.tmp"
    temp_animsetdata = cfg.cache / "temp" / "animationsetdatasinglefile.txt.tmp"

    # //// COPYING OLD FILES ////

    # copy over old animdata file to temp cache file by line
    with open(temp_animdata, 'w', encoding="utf-8") as t_animdata:
        with open(old_animdata, 'r', encoding="utf-8") as o_animdata:

            o_animdata.readline()  # skip first line

            # write new project count
            t_animdata.write(f"{count_projects}")

            # copy existing project names
            for _ in range(len(animdata_df)):
                t_animdata.write("\n" + o_animdata.readline().strip())
            
            # append each new project name NO NEWLINE
            for project_name in project_list:
                t_animdata.write("\n" + project_name + ".txt")

            # copy everything else
            for line in o_animdata:
                t_animdata.write("\n" + line.strip())
    
    # copy over old animsetdata file to temp cache file by line
            with open(temp_animsetdata, 'w', encoding="utf-8") as t_animsetdata:
                with open(old_animsetdata, 'r', encoding="utf-8") as o_animsetdata:

                    # write new project count
                    t_animsetdata.write(f"{count_creatures}")

                    o_animsetdata.readline()  # skip first line

                    # copy existing project names
                    for _ in range(len(animsetdata_df)):
                        t_animsetdata.write("\n" + o_animsetdata.readline().strip())
                    
                    # append the new project names only if they are creatures
                    for project_name in project_list:
                        if creatures_dict.get(project_name):
                            t_animsetdata.write("\n" + project_name + "data\\" + project_name + ".txt")

                    # copy everything else
                    for line in o_animsetdata:
                        t_animsetdata.write("\n" + line.strip())


    # //// MERGING NEW PROJECTS ////
    for project_name in project_list:

        print(f"Appending {project_name}.")

        try:
            # check again to make sure the files exist
            proj_animdata = util.get_path_case_insensitive(cfg.skyrim / "meshes" / "animationdata" / f"{project_name}.txt")
            
            if not proj_animdata:
                raise Exception(f"Error: {project_name} is missing!")
        except Exception as e:
            print(e)
            return 1
        
        # will fail silently if its not a creature
        proj_boundanims = util.get_path_case_insensitive(cfg.skyrim / "meshes" / "animationdata" / "boundanims" / f"anims_{project_name}.txt")
        proj_animsetdata = util.get_path_case_insensitive(cfg.skyrim / "meshes" / "animationsetdata" / f"{project_name}data" / f"{project_name}.txt")

        if proj_boundanims and proj_animsetdata:
            is_creature = True
        else:
            is_creature = False

        if not os.path.exists(cfg.skyrim / proj_animdata):
            print(f"Error: {project_name} is missing!")
            return 1

        # if the last project was a creature, skip a line
        with open(temp_animdata, 'a',encoding="utf-8") as t_animdata:
            if last_project_is_creature:
                t_animdata.write("\n")  

            with open(proj_animdata, 'r', encoding="utf-8") as p_animdata:

                lines_animdata = util.count_lines_and_strip(proj_animdata)

                # append line count NO NEWLINE
                if is_creature: 
                    t_animdata.write(f"\n{lines_animdata + 1}") # +1 required for creatures
                else:
                    t_animdata.write(f"\n{lines_animdata}")
            
                # append each line to the temp cache file
                for _ in range(lines_animdata):
                    t_animdata.write("\n")
                    t_animdata.write(p_animdata.readline().strip())


                # append boundanims
                if is_creature:
                    with open(proj_boundanims, 'r', encoding="utf-8") as p_boundanims:

                        lines_boundanims = util.count_lines_and_strip(proj_boundanims)

                        t_animdata.write(f"\n\n{lines_boundanims + 1}") # +1 required here as well

                        for _ in range(lines_boundanims):
                            t_animdata.write("\n")
                            t_animdata.write(p_boundanims.readline().strip())

        # append animsetdata
        if is_creature:

            had_a_creature = True
            last_project_is_creature = True

            # convert creatureprojectdata txt to list
            with open (proj_animsetdata, 'r') as p_animsetdata:
                files_animsetdata = []
                expected_file_count = util.count_lines_and_strip(proj_animsetdata)

                for _ in range(expected_file_count):
                    files_animsetdata.append(p_animsetdata.readline().strip())

            with open(temp_animsetdata, 'a', encoding="utf-8") as t_animsetdata:

                # append file count
                t_animsetdata.write(f"\n{expected_file_count}")

                # append projectdata list contents to tmp animsetdata cache
                for entry in files_animsetdata:
                    t_animsetdata.write(f"\n{entry}")
                
                for entry in files_animsetdata:
                    # skip any blank lines
                    if entry.strip() == "\n":
                        continue

                    entry_casefold = util.get_path_case_insensitive(Path(cfg.skyrim / "meshes" / "animationsetdata" / f"{project_name}data" / f"{entry}".strip()))  # verify path exists

                    # copy contents from each txt to tmp animsetdata cache
                    with open(entry_casefold, 'r', encoding="utf-8") as p_file:
                        
                        for i in range(util.count_lines_and_strip(entry_casefold)):
                            t_animsetdata.write("\n")
                            t_animsetdata.write(p_file.readline().strip())
        else:
            last_project_is_creature = False

    # //// POST PROCESSING ////

    # extra newline at the very end
    with open(temp_animdata, 'a', encoding="utf-8") as t_animdata:
        t_animdata.write("\n")

    with open(temp_animsetdata, 'a', encoding="utf-8") as t_animsetdata:
        t_animsetdata.write("\n")

    # validate tmp cache files

    if not dryrun:
        # copy tmp cache files to real cache files
        copy2(temp_animdata, cfg.skyrim / config.animdata)

        if had_a_creature:
            copy2(temp_animsetdata, cfg.skyrim / config.animsetdata)

    else:
        print("Dry run complete. No changes were made.")
        util.pause_wait_for_input()

    # clean up tmp files
    if system.clean_temp() != 0:
        print("Error: Could not clean temporary files.")
        return 1

    # run updater
    ud.update_cache()

    return 0