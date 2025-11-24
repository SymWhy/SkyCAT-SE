import shutil
import os
import logging

import config, cache, errors, system, util

def extract_projects(listprojects: list[str], dryrun: bool=False, yes_im_sure: bool=False):
    cfg = config.get_global('config')
    ud = config.get_global('update')
    dryrun = config.get_global('dryrun')

    # ensure cache is up to date
    ud.update_cache()

    animdata_list = ud.animdata_list
    animsetdata_list = ud.animsetdata_list

    meshes_dir = cfg.skyrim / "meshes"
    v_animdata = config.animdata
    v_animsetdata = config.animsetdata

    for project in listprojects:
        project = project.lower()

        # check if project exists
        if not cache.is_in_cache(project.casefold()):
            logging.warning(f"Project {project} not found. Cancelling...")
            return 0

        unpacked = cache.is_unpacked(project)

        # check if there are already extracted files in meshes
        if (any(unpacked)) and not yes_im_sure:
            if not util.prompt_yes_no(f"Warning: Project {project} already has extracted files. Overwrite?",
                                            message_y=f"Overwriting existing files for project {project}.",
                                            message_n=f"Skipping extraction for project {project}."):
                continue
            
            

        project_index = ud.cached_projects.index(project)
        animset_index = None

        isCreature = False

        if ud.creature_projects.__contains__(project):
            isCreature = True
            animset_index = []
            for i in range(len(animsetdata_list)):
                if animsetdata_list[i]["animset_name"] == project:
                    animset_index = i
                    break

        ### ANIMATIONDATA ###

        # check that our animdata directory exists
        animdata_dir = cfg.skyrim / config.animdata_dir

        try:
            os.makedirs(animdata_dir, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise errors.WriteError(path=str(animdata_dir), message=f"Could not create animdata directory: {e}") from e

        # create temporary cache folders
        try:
            animdata_temp_folder = cfg.cache / "temp" / config.animdata_dir
            animsetdata_temp_folder = cfg.cache / "temp" / config.animsetdata_dir
            os.makedirs(animdata_temp_folder, exist_ok=True)
            os.makedirs(animsetdata_temp_folder, exist_ok=True)

        except (OSError, PermissionError) as e:
            raise errors.WriteError(path=str(cfg.cache / "temp"), message=f"Could not create temporary cache directories: {e}") from e 

        # open the animdata file
        with open(cfg.skyrim / "meshes" / config.animdata, "r", encoding="utf-8") as readable:

            readline = readable.readline
            strip = str.strip

            try:
                # record project start line for debug purposes
                debug_line = int(animdata_list[project_index]["project_start"])
            except (IndexError, ValueError) as e:
                raise errors.CacheError(path=str(meshes_dir / v_animdata), message=f"Could not find project start line for {project} in local cache: {e}") from e

            # write the animdata cache file
            try:
                with open((animdata_temp_folder / (project + ".txt")), 'w', encoding="utf-8") as animdata_cache:

                    try:
                        # read lines up to the project start
                        util.fast_skip(readable, int(animdata_list[project_index]["project_start"]))
                    except (OSError, PermissionError) as e:
                        raise errors.ReadError(path=str(meshes_dir / v_animdata), message=f"Could not read animdata file up to project {project} start line {debug_line}: {e}") from e
                    except (IndexError, ValueError) as e:
                        raise errors.CacheError(path=str(meshes_dir / v_animdata), message=f"Could not find project start line for {project} in local cache: {e}") from e
                    # skip line count
                    util.fast_skip(readable, 1)
                    debug_line += 1

                    try:
                        lines_anims = int(animdata_list[project_index]["lines_anims"])
                    except (IndexError, ValueError) as e:
                        raise errors.CacheError(path=str(meshes_dir / v_animdata), message=f"Could not find lines_anims for {project} in local cache: {e}") from e

                    n = 1
                    
                    if isCreature:
                        n = 2

                    for i in range(lines_anims - n):
                        animdata_cache.write(readline())
                        debug_line += 1

                    animdata_cache.write(strip(readline()))
                    debug_line += 1

            except ValueError as e:
                raise errors.ParseError(path=str(meshes_dir / v_animdata), message=f"Invalid lines_anims count at line {debug_line}") from e
            except (OSError, PermissionError) as e:
                raise errors.WriteError(path=str(meshes_dir / v_animdata), message=f"Error writing animdata cache for project {project} at line {debug_line}: {e}") from e

            # write the boundanims cache file
            if isCreature:

                boundanims_dir = animdata_temp_folder / "boundanims"

                try:
                    os.makedirs(boundanims_dir, exist_ok=True)
                except (OSError, PermissionError) as e:
                    raise errors.WriteError(path=str(boundanims_dir), message=f"Could not create boundanims directory: {e}") from e

                with open(boundanims_dir / ("anims_" + project + ".txt"), 'w', encoding="utf-8") as boundanims_cache:
                    try:

                        # skip whitespace and linecount
                        util.fast_skip(readable, 2)
                        debug_line += 2

                        try:
                            lines_boundanims = int(animdata_list[project_index]["lines_boundanims"])

                        except (IndexError, ValueError) as e:
                            raise errors.CacheError(path=str(meshes_dir / v_animdata), message=f"Could not find lines_boundanims for {project} in local cache: {e}") from e

                        for i in range(lines_boundanims - 2):
                            boundanims_cache.write(readline())
                            debug_line += 1

                        boundanims_cache.write(strip(readline()))
                        debug_line += 1

                    except (OSError, PermissionError) as e:
                        raise errors.WriteError(path=str(meshes_dir / v_animdata), message=f"Error writing boundanims cache for project {project} at line {debug_line}: {e}") from e

        ### ANIMATIONSETDATA ###

        if isCreature:
                
            # open the animdata file
            with open(cfg.skyrim / 'meshes' / config.animsetdata, "r", encoding="utf-8") as readable:

                readline = readable.readline
                strip = str.strip

                try:
                    debug_line = int(animsetdata_list[animset_index]["animset_start"])
                except (IndexError, ValueError) as e:
                    raise errors.CacheError(path=str(meshes_dir / v_animsetdata), message=f"Could not find animation set data start line for {project} in local cache: {e}") from e

                # write the animsetdata cache file
                try:
                    try:
                    # skip to the project start
                        util.fast_skip(readable, int(animsetdata_list[animset_index]["animset_start"]))  # skip line count
                    except (IndexError, ValueError) as e:
                        raise errors.CacheError(path=str(meshes_dir / v_animsetdata), message=f"Could not find animation set data start line for {project} in local cache: {e}") from e
                
                    # get the expected number of animation sets
                    animset_count = int(strip(readline()))
                    debug_line += 1

                    try:
                        expected_animset_count = int(animsetdata_list[animset_index]["count_animsets"])
                    except (IndexError, ValueError) as e:
                        raise errors.CacheError(path=str(meshes_dir / v_animsetdata), message=f"Could not find animation set data count for {project} in local cache: {e}") from e

                    # check to make sure the cache data matches
                    if animset_count != expected_animset_count:
                        logging.debug(f"Expected {expected_animset_count} sets, got {animset_count}.")
                        raise errors.ParseError(path=str(meshes_dir / v_animsetdata), message=f"Animation set count mismatch at line {debug_line}")

                    project_dir = animsetdata_temp_folder / str(project + "data")

                    # check to make sure the path to project's "projectdata" folder exists
                    try:
                        os.makedirs(project_dir, exist_ok=True)
                    except (OSError, PermissionError) as e:
                        raise errors.WriteError(path=str(project_dir), message=f"Could not create project animation set directory: {e}") from e

                    # create the set list file
                    # this file contains a list of all the animation set text files
                    with open(project_dir / (project + ".txt"), 'w', encoding="utf-8") as animsetlist:
                        animset_list = []

                        # write the file names to the animsetlist txt
                        for i in range(animset_count):
                            animset_list.append(strip(readline()).lower())
                            debug_line += 1

                        for item in animset_list:
                            animsetlist.write(item + "\n")

                    for i in range(animset_count):
                        with open(project_dir / animset_list[i], 'w', encoding="utf-8") as writable:

                            # write the first V3
                            writable.write(readline())
                            debug_line += 1
                        
                            try:
                                # write notes A, B, and C
                                notes_A = readline()
                                debug_line += 1
                                notes_A_int = int(strip(notes_A))
                                writable.write(notes_A)
                            except ValueError as e:
                                raise errors.ParseError(path=str(meshes_dir / v_animsetdata), message=f"Invalid animation set notes count: {notes_A} at line {debug_line}: {e}") from e


                            if notes_A_int != 0:
                                for j in range(notes_A_int):
                                    writable.write(readline())
                                    debug_line += 1

                            try:
                                notes_B = readline()
                                debug_line += 1
                                notes_B_int = int(strip(notes_B))
                            except ValueError as e:
                                raise errors.ParseError(path=str(meshes_dir / v_animsetdata), message=f"Invalid animation set notes count: {notes_B} at line {debug_line}: {e}") from e

                            writable.write(notes_B)
                            
                            if notes_B_int != 0:
                                for j in range(notes_B_int):
                                    for k in range(3):
                                        writable.write(readline())
                                        debug_line += 1

                            try:
                                notes_C = readline()
                                debug_line += 1
                                notes_C_int = int(strip(notes_C))
                            except ValueError as e:
                                raise errors.ParseError(path=str(meshes_dir / v_animsetdata), message=f"Invalid animation set notes count: {notes_C} at line {debug_line}: {e}") from e

                            writable.write(notes_C)

                            if notes_C_int != 0:
                                for j in range(notes_C_int):
                                    # skip two lines
                                    for k in range(2):
                                        writable.write(readline())
                                        debug_line += 1

                                    n = readline()
                                    debug_line += 1
                                    writable.write(n)

                                    # skip 
                                    for k in range(int(strip(n))):
                                        writable.write(readline())
                                        debug_line += 1
                            
                            try:
                                file_count = readline()
                                debug_line += 1
                                file_count_int = int(strip(file_count))
                            except ValueError as e:
                                raise errors.ParseError(path=str(meshes_dir / v_animsetdata), message=f"Invalid animation set file count: {file_count} at line {debug_line}: {e}") from e

                            writable.write(file_count)

                            for j in range(file_count_int):
                                # skip two lines
                                for k in range(2):
                                    writable.write(readline())
                                    debug_line += 1

                                # if we are on the last line, strip whitespace.
                                if i == animset_count - 1 and j == file_count_int - 1:
                                    writable.write(strip(readline()))
                                    debug_line += 1
                                
                                else:
                                    writable.write(readline())
                                    debug_line += 1
                      
                except (OSError, PermissionError) as e:
                    raise errors.WriteError(path=str(meshes_dir / v_animsetdata), message=f"Error writing animsetdata cache for project {project} at line {debug_line}: {e}") from e
                
        logging.info(f"Successfully extracted {project}.")

    if not dryrun:
        # move temp files to their final destination
        shutil.copytree(cfg.cache / "temp", cfg.skyrim, dirs_exist_ok=True)
    else:
        logging.info("Dry run complete. No changes were made.")

    # remove temp folders if they still exist
    system.clean_temp()
        
    return 0


def extract_all(yes_im_sure: bool=False, and_i_mean_all_of_them: bool=False, dryrun: bool=False):
    cfg = config.get_global('config')
    ud = config.get_global('update')

    vanilla_projects_count = len(ud.vanilla_projects)
    animdata_list = ud.animdata_list
    animsetdata_list = ud.animsetdata_list

    # get count for total projects
    total_projects = len(animdata_list)                  
    # make sure we have modded projects to extract
    if total_projects - vanilla_projects_count == 0 and not and_i_mean_all_of_them:
        logging.warning("No modded projects found.")
        return
    
    extract_everything = False
    
    if and_i_mean_all_of_them and not yes_im_sure:
        print("This will extract ALL projects, including vanilla ones.")
        extract_everything = util.prompt_yes_no("Are you sure you want to do this?", 
                                                message_y="Extracting all projects, including vanilla ones.",
                                                message_n="Cancelling operation.")

    to_extract = []

    match extract_everything:
        
        case True:
            if ud.cached_projects == []:
                logging.info("No cached projects found. Updating cache...")
                if ud.update_cache() != 0:
                    raise errors.CacheError(path=str(cfg.cache), message="Failed to update cache before extracting all projects.")
            to_extract = ud.cached_projects

        case False:
            if ud.cached_projects == []:
                logging.info("No cached projects found. Updating cache...")
                if ud.update_cache() != 0:
                    raise errors.CacheError(path=str(cfg.cache), message="Failed to update cache before extracting all projects.")
            to_extract = ud.new_projects

    extract_projects(to_extract, dryrun=dryrun, yes_im_sure=yes_im_sure)

    return 0