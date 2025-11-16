import os
from pathlib import Path
import shutil
import pandas as pd

import config, util, system, update

def append_projects(project_list):
    cfg = config.require_config()
    ud = update.require_update()

    had_a_creature = False

    # pre-processing steps:
    # check if the project is available to be merged
    for project_name in project_list:
        if not util.can_be_merged(project_name):
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


    if not os.path.exists(cfg.cache / config.animdata_csv_path):
        print("Error: Can't find cache csv.")
        return 1
    
    animdata_csv = pd.read_csv(cfg.cache / config.animdata_csv_path)
    last_project_is_creature = util.is_creature(animdata_csv.iloc[-1]['project_name'])

    
    # merging steps:
    for project_name in project_list:

        print(f"Appending {project_name}.")

        # check again to make sure the files exist
        proj_animdata = util.get_path_case_insensitive(cfg.skyrim / "meshes" / "animationdata" / f"{project_name}.txt")

        # will fail silently if its not a creature
        proj_boundanims = util.get_path_case_insensitive(cfg.skyrim / "meshes" / "animationdata" / "boundanims" / f"anims_{project_name}.txt")
        proj_animsetdata = util.get_path_case_insensitive(cfg.skyrim / "meshes" / "animationsetdata" / f"{project_name}data" / f"{project_name}.txt")

        if proj_boundanims and proj_animsetdata:
            is_creature = True
        else:
            is_creature = False

        os.makedirs(cfg.cache / "temp", exist_ok=True)

        old_animdata = cfg.skyrim / config.animdata
        old_animsetdata = cfg.skyrim / config.animsetdata

        temp_animdata = cfg.cache / "temp" / "animationdatasinglefile.txt.tmp"
        temp_animsetdata = cfg.cache / "temp" / "animationsetdatasinglefile.txt.tmp"

        count_projects = 0
        count_creatures = 0

        with open(old_animdata, 'r', encoding="utf-8") as o_animdata:
            count_projects = int(o_animdata.readline().strip())

        with open(old_animsetdata, 'r', encoding="utf-8") as o_animsetdata:
            count_creatures = int(o_animsetdata.readline().strip())

        if not os.path.exists(cfg.skyrim / proj_animdata):
            print(f"Error: {project_name} is missing!")
            return 1
        
        # copy over old cache files to temp cache files by line
        with open(temp_animdata, 'w', encoding="utf-8") as t_animdata:
            with open(old_animdata, 'r', encoding="utf-8") as o_animdata:

                o_animdata.readline()  # skip first line

                # write new project count
                t_animdata.write(f"{count_projects + 1}\n")

                # copy existing project names
                for _ in range(count_projects):
                    t_animdata.write(o_animdata.readline())
                
                # append the new project name NO NEWLINE
                t_animdata.write(project_name + ".txt\n")

                # copy everything else
                for line in o_animdata:
                    t_animdata.write(line)

        # if the last project was a creature, skip a line
        with open(temp_animdata, 'a',encoding="utf-8") as t_animdata:
            if last_project_is_creature:
                t_animdata.write("\n")

            with open(proj_animdata, 'r', encoding="utf-8") as p_animdata:

                lines_animdata = util.count_lines_and_strip(proj_animdata)

                # append line count NO NEWLINE
                t_animdata.write(f"{lines_animdata + 1}")
            
                # append each line to the temp cache file
                for _ in range(lines_animdata):
                    t_animdata.write("\n")
                    t_animdata.write(p_animdata.readline().strip())


                # append boundanims
                if is_creature:
                    with open(proj_boundanims, 'r', encoding="utf-8") as p_boundanims:

                        lines_boundanims = util.count_lines_and_strip(proj_boundanims)

                        t_animdata.write(f"\n\n{lines_boundanims + 1}")

                        for _ in range(lines_boundanims):
                            t_animdata.write("\n")
                            t_animdata.write(p_boundanims.readline().strip())

        # append animsetdata
        if is_creature:

            had_a_creature = True

            # copy over old cache files to temp cache files by line
            with open(temp_animsetdata, 'w', encoding="utf-8") as t_animsetdata:
                with open(old_animsetdata, 'r', encoding="utf-8") as o_animsetdata:
                    # write new project count
                    t_animsetdata.write(f"{count_creatures + 1}\n")

                    o_animsetdata.readline()  # skip first line

                    # copy existing project names
                    for _ in range(count_creatures):
                        t_animsetdata.write(o_animsetdata.readline())
                    
                    # append the new project name.
                    t_animsetdata.write(project_name + "data\\" + project_name + ".txt\n")

                    # copy everything else
                    for line in o_animsetdata:
                        t_animsetdata.write(line)

            # convert creatureprojectdata txt to list
            with open (proj_animsetdata, 'r') as p_animsetdata:
                files_animsetdata = []
                expected_file_count = util.count_lines_and_strip(proj_animsetdata)

                for _ in range(expected_file_count):
                    files_animsetdata.append(p_animsetdata.readline().strip())

            with open(temp_animsetdata, 'a', encoding="utf-8") as t_animsetdata:

                # append file count
                t_animsetdata.write(f"{expected_file_count}\n")

                # append projectdata list contents to tmp animsetdata cache
                for entry in files_animsetdata:
                    t_animsetdata.write(f"{entry}\n")
                
                for entry in files_animsetdata:
                    # skip any blank lines
                    if entry.strip() == "\n":
                        continue

                    entry_casefold = util.get_path_case_insensitive(Path(cfg.skyrim / "meshes" / "animationsetdata" / f"{project_name}data" / f"{entry}".strip()))  # verify path exists

                    # copy contents from each txt to tmp animsetdata cache
                    with open(entry_casefold, 'r', encoding="utf-8") as p_file:
                        
                        for i in range(util.count_lines_and_strip(entry_casefold)):
                            if i != 0:
                                t_animsetdata.write("\n")
                            t_animsetdata.write(p_file.readline().strip())

        last_project_is_creature = is_creature

    # post-processing steps:

    # extra newline at the very end
    with open(temp_animdata, 'a', encoding="utf-8") as t_animdata:
        t_animdata.write("\n")

    with open(temp_animsetdata, 'a', encoding="utf-8") as t_animsetdata:
        t_animsetdata.write("\n")

    # validate tmp cache files

    # copy tmp cache files to real cache files
    shutil.copy2(temp_animdata, cfg.skyrim / config.animdata)

    if had_a_creature:
        shutil.copy2(temp_animsetdata, cfg.skyrim / config.animsetdata)

    # clean up tmp files
    if util.clean_temp() != 0:
        print("Error: Could not clean temporary files.")
        return 1

    # run updater
    ud.update_all()

    return 0