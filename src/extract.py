import shutil
import os.path
import config, cache, system, util

def extract_projects(listprojects: list[str]):
    cfg = config.get_global('config')
    ud = config.get_global('update')
    dryrun = config.get_global('dryrun')

    # ensure cache is up to date
    ud.update_cache()

    animdata_df = ud.animdata_df
    animsetdata_df = ud.animsetdata_df

    for project in listprojects:
        project = project.lower()

        # check if project exists
        if cache.is_in_cache(project) == False:
            print(f"Warning: Project {project} not found. Cancelling...")
            return 0

        unpacked = cache.is_unpacked(project)

        # check if there are already extracted files in meshes
        if unpacked[0] == True or unpacked[1] == True or unpacked[2] == True:
            print(f"Warning: Project {project} already has extracted files. Overwrite? Y/N")
            extract_ok = False
            while True:
                match input().lower():
                    case 'y':
                        extract_ok = True
                        break
                    case 'n':
                        print(f"Skipping extraction of {project}.")
                        extract_ok = False
                        break
            if not extract_ok:
                continue
            

        project_index = ud.cached_projects.index(project)
        animset_index = None

        isCreature = False

        if ud.creature_projects.__contains__(project):
            isCreature = True
            animset_index = animsetdata_df.index[animsetdata_df['animset_name'] == project].to_list()[0]

        ### ANIMATIONDATA ###

        # check that our animdata directory exists
        animdata_dir = cfg.skyrim / config.animdata_dir

        if not os.path.exists(animdata_dir):
            os.makedirs(animdata_dir)

        # create temporary cache folders
        try:
            animdata_temp_folder = cfg.cache / "temp" / config.animdata_dir
            animsetdata_temp_folder = cfg.cache / "temp" / config.animsetdata_dir
            os.makedirs(animdata_temp_folder, exist_ok=True)
            os.makedirs(animsetdata_temp_folder, exist_ok=True)

        except Exception as e:
            print(f"Error creating temporary folders: {e}")
            system.clean_temp()
            return 1

        # open the animdata file
        with open(cfg.skyrim / config.animdata, "r", encoding="utf-8") as readable:

            readline = readable.readline
            strip = str.strip

            # write the animdata cache file
            try:
                with open((animdata_temp_folder / (project + ".txt")), 'w', encoding="utf-8") as animdata_cache:
                    # read lines up to the project start
                    util.fast_skip(readable, int(animdata_df.at[project_index, "project_start"]))

                    # skip line count
                    util.fast_skip(readable, 1)

                    lines_anims = int(animdata_df.at[project_index, "lines_anims"])

                    n = 1
                    
                    if isCreature:
                        n = 2

                    for i in range(lines_anims - n):
                        animdata_cache.write(readline())
                    animdata_cache.write(strip(readline()))

            except Exception as e:
                print(f"Error extracting animdata for {project}: {e}")
                system.clean_temp()
                return 1

            # write the boundanims cache file
            if isCreature:

                boundanims_dir = animdata_temp_folder / "boundanims"
                if not os.path.exists(boundanims_dir):
                    os.makedirs(boundanims_dir)

                try:
                    with open(boundanims_dir / ("anims_" + project + ".txt"), 'w', encoding="utf-8") as boundanims_cache:

                        # skip whitespace and linecount
                        util.fast_skip(readable, 2)

                        lines_boundanims = int(animdata_df.at[project_index, "lines_boundanims"])

                        for i in range(lines_boundanims - 2):

                            boundanims_cache.write(readline())

                        boundanims_cache.write(strip(readline()))


                except Exception as e:
                    print(f"Error extracting boundanims for {project}: {e}")
                    system.clean_temp()
                    return 1

        ### ANIMATIONSETDATA ###

        if isCreature:
                
            # open the animdata file
            with open(cfg.skyrim / config.animsetdata, "r", encoding="utf-8") as readable:

                readline = readable.readline
                strip = str.strip

                # write the animsetdata cache file
                try:
                    # skip to the project start
                    util.fast_skip(readable, int(animsetdata_df.at[animset_index, "animset_start"]))  # skip line count

                    # get the expected number of animation sets
                    animset_count = int(strip(readline()))
                    expected_animset_count = int(animsetdata_df.at[animset_index, "count_animsets"])

                    # check to make sure the cache data matches
                    if animset_count != expected_animset_count:
                        print("Error: Animset count mismatch. Regenerating the cache might fix this.")
                        print("Expected {}, got {}.".format(expected_animset_count, animset_count))
                        return

                    project_dir = animsetdata_temp_folder / str(project + "data")

                    # check to make sure the path to project's "projectdata" folder exists
                    if not os.path.exists(project_dir):
                        os.makedirs(project_dir)

                    # create the set list file
                    # this file contains a list of all the animation set text files
                    with open(project_dir / (project + ".txt"), 'w', encoding="utf-8") as animsetlist:
                        animset_list = []

                        # write the file names to the animsetlist txt
                        for i in range(animset_count):
                            animset_list.append(strip(readline()).lower())

                        for item in animset_list:
                            animsetlist.write(item + "\n")

                    for i in range(animset_count):
                        with open(project_dir / animset_list[i], 'w', encoding="utf-8") as writable:

                            # write the first V3
                            writable.write(readline())
                        
                            # write notes A, B, and C
                            notes_A = readline()
                            notes_A_int = int(strip(notes_A))
                            writable.write(notes_A)

                            if notes_A_int != 0:
                                for j in range(notes_A_int):
                                    writable.write(readline())

                            notes_B = readline()
                            notes_B_int = int(strip(notes_B))

                            writable.write(notes_B)
                            
                            if notes_B_int != 0:
                                for j in range(notes_B_int):
                                    for k in range(3):
                                        writable.write(readline())

                            notes_C = readline()
                            notes_C_int = int(strip(notes_C))

                            writable.write(notes_C)

                            if notes_C_int != 0:
                                for j in range(notes_C_int):
                                    # skip two lines
                                    for k in range(2):
                                        writable.write(readline())

                                    n = readline()
                                    writable.write(n)

                                    # skip 
                                    for k in range(int(strip(n))):
                                        writable.write(readline())

                            file_count = readline()
                            file_count_int = int(strip(file_count))

                            writable.write(file_count)

                            for j in range(file_count_int):
                                # skip two lines
                                for k in range(2):
                                    writable.write(readline())

                                # if we are on the last line, strip whitespace.
                                if i == animset_count - 1 and j == file_count_int - 1:
                                    writable.write(strip(readline()))
                                
                                else: writable.write(readline())
                      
                except Exception as e:
                    print(f"Error while extracting animset data for {project}: {e}")
                    system.clean_temp()
                    return 1
                
        print(f"Successfully extracted {project}.")

    if not dryrun:
        # move temp files to their final destination
        shutil.copytree(cfg.cache / "temp", cfg.skyrim, dirs_exist_ok=True)
    else:
        print("Dry run complete. No changes were made.")
        util.pause_wait_for_input()

    # remove temp folders if they still exist
    system.clean_temp()
        
    return 0


def extract_all(and_i_mean_all_of_them=False):
    cfg = config.get_global('config')
    ud = config.get_global('update')

    vanilla_projects_count = len(ud.vanilla_projects)
    animdata_df = ud.animdata_df
    animsetdata_df = ud.animsetdata_df

    # get count for total projects
    total_projects = animdata_df.shape[0]                  

    # make sure we have modded projects to extract
    if total_projects - vanilla_projects_count == 0 and not and_i_mean_all_of_them:
        print("Error: No modded projects found.")
        return
    
    extract_everything = False
    
    if and_i_mean_all_of_them:
            while extract_everything == False:
                print("This will extract ALL projects, including vanilla ones.")
                print("Are you sure you want to do this? Y/N")
                response = input().lower()

                match response:
                    case 'y':
                        extract_everything = True
                    case 'n':
                        return 0

    # loop through all projects and check if they are vanilla or not
    for project_name in (animdata_df)['project_name']:
        project_name = project_name.lower()
    
    to_extract = []

    match extract_everything:
        
        case True:
            to_extract = ud.cached_projects

        case False:
            to_extract = ud.new_projects

    extract_projects(to_extract)

    return 0