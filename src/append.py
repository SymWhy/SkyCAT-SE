import logging
import os
from pathlib import Path
from shutil import copy2

import config, cache, errors, system, util

def append_projects(project_list: list[str], yes_im_sure: bool = False):
    cfg = config.get_global('config')
    ud = config.get_global('update')
    dryrun = config.get_global('dryrun')

    # ensure cache is up to date
    if ud.update_cache() != 0:
        raise errors.CacheError(message="Cache is not up to date, cannot append projects.")

    had_a_creature = False

    # //// PREPROCESSING ////

    # check if the project is available to be merged
    for project_name in project_list:
        if not cache.can_be_merged(project_name):
            logging.warning(f"{project_name} cannot be merged.")
            return
        
    # prompt user for confirmation of overwrite:
    if not yes_im_sure:
        if not util.prompt_yes_no(f"This process will overwrite existing cache files. Is this okay?",
                           message_y="Proceeding.",
                           message_n="Cancelling append."):
            return 0

        # offer to back up the existing cache
        if (cfg.skyrim / "meshes" / config.animdata).exists() or (cfg.skyrim / "meshes" / config.animsetdata).exists():
            if util.prompt_yes_no("Would you like to back up the existing cache files?",
                                message_y="Backing up cache files.",
                                message_n="Skipping backup."):
                system.save_backup(yes_im_sure=True)


    if ud.animdata_list is None or ud.animsetdata_list is None:
        if ud.update_cache() != 0:
            raise errors.CacheError(message="Unable to update cache, cannot append projects.")
        return 1
    
    animdata_list = ud.animdata_list
    animsetdata_list = ud.animsetdata_list

    # if not animdata_list:
    #     last_project_is_creature = False
    # else:
    #     last = animdata_list[-1]
    #     # handle dict-like row or plain string
    #     project_name = last.get('project_name') if isinstance(last, dict) and 'project_name' in last else str(last)
    #     last_project_is_creature = cache.is_creature(project_name)

    try: 
        last_project_is_creature = True if animdata_list[-1]["project_type"] == "creature" else False
    except (IndexError, KeyError) as e:
        raise errors.CacheError(message="Animation data cache is corrupted or empty, cannot append projects.") from e

    count_projects = len(animdata_list) + len(project_list)
    count_creatures = len(animsetdata_list)
    creatures_dict = cache.get_creature_projects(project_list)
    count_creatures += sum(1 for p in project_list if creatures_dict.get(p))

    # open old cache files
    old_animdata = cfg.skyrim / 'meshes' / config.animdata
    old_animsetdata = cfg.skyrim / 'meshes' / config.animsetdata
    
    # create temporary cache folder
    os.makedirs(cfg.cache / "temp", exist_ok=True)

    temp_animdata = cfg.cache / "temp" / "animationdatasinglefile.txt"
    temp_animsetdata = cfg.cache / "temp" / "animationsetdatasinglefile.txt"

    # //// COPYING OLD FILES ////

    # copy over old animdata file to temp cache file by line
    with open(temp_animdata, 'w', encoding="utf-8") as t_animdata:
        with open(old_animdata, 'r', encoding="utf-8") as o_animdata:
            readline = o_animdata.readline
            strip = str.strip

            try:
                o_animdata.readline()  # skip first line

                # write new project count
                t_animdata.write(f"{count_projects}")

                # copy existing project names
                for _ in range(len(animdata_list)):
                    t_animdata.write("\n" + strip(readline()))
                
                # append each new project name NO NEWLINE
                for project_name in project_list:
                    t_animdata.write("\n" + project_name + ".txt")

                # copy everything else
                for line in o_animdata:
                    t_animdata.write("\n" + strip(line))

            except (OSError, PermissionError) as e:
                raise errors.WriteError(path=str(old_animdata), message=f"Error copying from old animdata file: {e}") from e
    
            # copy over old animsetdata file to temp cache file by line
            with open(temp_animsetdata, 'w', encoding="utf-8") as t_animsetdata:
                with open(old_animsetdata, 'r', encoding="utf-8") as o_animsetdata:
                    
                    try:
                        # write new project count
                        t_animsetdata.write(f"{count_creatures}")

                        util.fast_skip(o_animsetdata)  # skip first line

                        # copy existing project names
                        for _ in range(len(animsetdata_list)):
                            t_animsetdata.write("\n" + strip(o_animsetdata.readline()))
                        
                        # append the new project names only if they are creatures
                        for project_name in project_list:
                            if creatures_dict.get(project_name):
                                t_animsetdata.write("\n" + project_name + "data\\" + project_name + ".txt")

                        # copy everything else
                        for line in o_animsetdata:
                            t_animsetdata.write("\n" + line.strip())
                            
                    except (OSError, PermissionError) as e:
                        raise errors.WriteError(path=str(old_animsetdata), message=f"Error copying from old animsetdata file: {e}") from e



    # //// MERGING NEW PROJECTS ////
    for project_name in project_list:

        logging.debug(f"Appending {project_name}.")

        # check again to make sure the files exist
        proj_animdata = cfg.skyrim / "meshes" / "animationdata" / f"{project_name}.txt"

        if not proj_animdata.exists():
            raise FileNotFoundError(f"Missing animation data for {project_name}")

        # will fail silently if its not a creature
        proj_boundanims = cfg.skyrim / "meshes" / "animationdata" / "boundanims" / f"anims_{project_name}.txt"
        proj_animsetdata = cfg.skyrim / "meshes" / "animationsetdata" / f"{project_name}data" / f"{project_name}.txt"

        if proj_boundanims.exists() and proj_animsetdata.exists():
            is_creature = True
        else:
            is_creature = False

        # if the last project was a creature, skip a line
        with open(temp_animdata, 'a',encoding="utf-8") as t_animdata:
            try:
                if last_project_is_creature:
                    t_animdata.write("\n")  

                with open(proj_animdata, 'r', encoding="utf-8") as p_animdata:
                    readline = p_animdata.readline
                    strip = str.strip

                    lines_animdata = util.count_lines_and_strip(proj_animdata)
                    
                    try:
                        debug_line = 0

                        # append line count NO NEWLINE
                        if is_creature: 
                            t_animdata.write(f"\n{lines_animdata + 1}") # +1 required for creatures
                        else:
                            t_animdata.write(f"\n{lines_animdata}")
                    
                        # append each line to the temp cache file
                        for _ in range(lines_animdata):
                            t_animdata.write("\n")
                            t_animdata.write(strip(readline()))
                            debug_line += 1
                    except (OSError, PermissionError) as e:
                        raise errors.WriteError(path=str(proj_animdata), message=f"Error appending animation data for {project_name} at line {debug_line}: {e}") from e


                    # append boundanims
                    if is_creature:
                        with open(proj_boundanims, 'r', encoding="utf-8") as p_boundanims:

                            debug_line = 0

                            lines_boundanims = util.count_lines_and_strip(proj_boundanims)

                            t_animdata.write(f"\n\n{lines_boundanims + 1}") # +1 required here as well

                            for _ in range(lines_boundanims):
                                t_animdata.write("\n")
                                t_animdata.write(p_boundanims.readline().strip())
                                debug_line += 1
            except (OSError, PermissionError) as e:
                raise errors.WriteError(path=str(proj_animdata), message=f"Error writing animation data for {project_name} at line {debug_line}: {e}") from e

        # append animsetdata
        if is_creature:

            had_a_creature = True
            last_project_is_creature = True

            try:
                # convert creatureprojectdata txt to list
                with open (proj_animsetdata, 'r') as p_animsetdata:
                    readline = p_animsetdata.readline
                    strip = str.strip

                    debug_line = 0
                    files_animsetdata = []
                    expected_file_count = util.count_lines_and_strip(proj_animsetdata)

                    for _ in range(expected_file_count):
                        files_animsetdata.append(strip(readline()))
            except IOError as e:
                raise errors.ReadError(path=str(proj_animsetdata), message=f"Error reading animsetdata for {project_name}: {e}") from e

            with open(temp_animsetdata, 'a', encoding="utf-8") as t_animsetdata:
                try:
                    strip = str.strip

                    # append file count
                    t_animsetdata.write(f"\n{expected_file_count}")

                    # append projectdata list contents to tmp animsetdata cache
                    for entry in files_animsetdata:
                        # skip any blank lines
                        if entry.strip() == "\n":
                            continue
                        t_animsetdata.write(f"\n{entry}")
                    
                except (OSError, PermissionError) as e:
                    raise errors.WriteError(path=str(temp_animsetdata), message=f"Error writing animsetdata for {project_name}: {e}") from e

                for entry in files_animsetdata:
                    entry_file = Path(cfg.skyrim / "meshes" / "animationsetdata" / f"{project_name}data" / f"{entry}".strip())  # verify path exists

                    if not entry_file.exists():
                        raise FileNotFoundError(f"Missing animsetdata entry file for {project_name}: {entry_file}")

                        # copy contents from each txt to tmp animsetdata cache
                    with open(entry_file, 'r', encoding="utf-8") as p_file:
                        try:
                            debug_line = 0
                            
                            for _ in range(util.count_lines_and_strip(entry_file)):
                                t_animsetdata.write("\n")
                                t_animsetdata.write(p_file.readline().strip())
                                debug_line += 1

                        except (OSError, PermissionError) as e:
                            raise errors.WriteError(path=str(entry_file), message=f"Error appending animsetdata for {project_name} at line {debug_line}: {e}") from e
        else:
            last_project_is_creature = False

    # //// POST PROCESSING ////

    # extra newline at the very end
    with open(temp_animdata, 'a', encoding="utf-8") as t_animdata:
        t_animdata.write("\n")

    with open(temp_animsetdata, 'a', encoding="utf-8") as t_animsetdata:
        t_animsetdata.write("\n")

    # validate tmp cache files
    if ud.update_cache(cfg.cache / "temp") != 0:
        raise errors.CacheError(message="Failed to validate new cache files. Cancelling...")

    logging.info(f"Successfully appended {project_name}.")

    if not dryrun:
        # copy tmp cache files to real cache files
        copy2(temp_animdata, cfg.skyrim / "meshes" / config.animdata)

        if had_a_creature:
            copy2(temp_animsetdata, cfg.skyrim / "meshes" / config.animsetdata)

    else:
        logging.info("Dry run complete. No changes were made.")
        util.pause_wait_for_input()

    # clean up tmp files
    if system.clean_temp() != 0:
        raise OSError("Failed to clean temporary files.")

    return 0