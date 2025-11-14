import pandas as pd
import os.path

import config, util, update

def __init__():
    cfg = config.require_config()
    ud = update.require_update()

    # load the csv files
    ud.animdata_csv = pd.read_csv(cfg.cache + "\\animdata_index.csv")
    ud.animsetdata_csv = pd.read_csv(cfg.cache + "\\animsetdata_index.csv")


def extract_projects(listprojects):
    
    cfg = config.require_config()
    ud = update.require_update()

    # check if we've generated our cache files
    if not os.path.exists(cfg.cache + "\\animdata_index.csv") or not os.path.exists(cfg.cache + "\\animsetdata_index.csv"):
        print("Updating cache files...")
        if ud.update_all() != 0:
            print("Error: Could not update program.")
            return
        return 0
    
    for project in listprojects:
        project = project.lower()

        # check if project exists
        if util.is_in_cache(project) == False:
            print(f"Warning: Project {project} not found. Skipping...")
            continue

        unpacked = util.is_unpacked(project)

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
            animset_index = ud.animsetdata_csv.index[ud.animsetdata_csv['animset_name'] == project].to_list()[0]

        print("Project index for {} is {}. Animset index is {}.".format(project, project_index, animset_index))

        ### ANIMATIONDATA ###

        # check that our directory exists
        animdata_dir = cfg.skyrim + "\\meshes\\animationdata"

        if not os.path.exists(animdata_dir):
            os.makedirs(animdata_dir)

        # open the animdata file
        readable = open(cfg.skyrim + config.animdata, "r")

        # write the animdata cache file
        try:

            try:
                animdata_cache = open((animdata_dir + "\\" + project + ".txt"), 'w')

                # read lines up to the project start
                for _ in range(int(ud.animdata_csv.at[project_index, "project_start"])):
                    readable.readline()

                # skip line count
                readable.readline()

                lines_anims = int(ud.animdata_csv.at[project_index, "lines_anims"])

                n = 1
                
                if isCreature:
                    n = 2

                for i in range(lines_anims - n):
                    animdata_cache.write(readable.readline())
                animdata_cache.write(readable.readline().strip())

            finally: animdata_cache.close()

            # write the boundanims cache file
            if isCreature:

                boundanims_dir = cfg.skyrim + "\\meshes\\animationdata\\boundanims"
                if not os.path.exists(boundanims_dir):
                    os.makedirs(boundanims_dir)

                try:
                    boundanims_cache = open(os.path.join(boundanims_dir, "anims_" + project + ".txt"), 'w')

                    # skip whitespace and linecount
                    readable.readline()
                    readable.readline()

                    lines_boundanims = int(ud.animdata_csv.at[project_index, "lines_boundanims"])

                    for i in range(lines_boundanims - 2):

                        boundanims_cache.write(readable.readline())

                    boundanims_cache.write(readable.readline().strip())

                finally: boundanims_cache.close()

        finally: readable.close()

        ### ANIMATIONSETDATA ###

        if isCreature:
                
            # open the animdata file
            readable = open(cfg.skyrim + config.animsetdata, "r")

            # write the animsetdata cache file
            try:

                # skip to the project start
                for _ in range(int(ud.animsetdata_csv.at[animset_index, "animset_start"])):
                    readable.readline()

                # get the expected number of animation sets
                animset_count = int(readable.readline().strip())
                expected_animset_count = int(ud.animsetdata_csv.at[animset_index, "count_animsets"])

                # check to make sure the cache data matches
                if animset_count != expected_animset_count:
                    print("Error: Animset count mismatch. Regenerating the cache might fix this.")
                    print("Expected {}, got {}.".format(expected_animset_count, animset_count))
                    return
                
                project_dir = cfg.skyrim + config.animsetdata_dir + "\\" + project + "data"

                # check to make sure the path to project's "projectdata" folder exists
                if not os.path.exists(project_dir):
                    os.makedirs(project_dir)

                # create the set list file
                # this file contains a list of all the animation set text files
                animsetlist = open(project_dir + "\\" + project + ".txt", 'w')
                try:
                    animset_list = []

                    # write the file names to the animstlist txt
                    for i in range(animset_count):
                        animset_list.append(readable.readline().strip().lower())

                    for item in animset_list:
                        animsetlist.write(item + "\n")
                finally:
                    animsetlist.close()

                for i in range(animset_count):
                    writable = open(project_dir + "\\" + animset_list[i], 'w')
                    try:
                        # write the first V3
                        writable.write(readable.readline())
                    
                        # write notes A, B, and C
                        notes_A = readable.readline()
                        notes_A_int = int(notes_A.strip())

                        writable.write(notes_A)

                        if notes_A_int != 0:
                            for j in range(notes_A_int):
                                writable.write(readable.readline())

                        notes_B = readable.readline()
                        notes_B_int = int(notes_B.strip())

                        writable.write(notes_B)
                        
                        if notes_B_int != 0:
                            for j in range(notes_B_int):
                                for k in range(3):
                                    writable.write(readable.readline())

                        notes_C = readable.readline()
                        notes_C_int = int(notes_C.strip())

                        writable.write(notes_C)

                        if notes_C_int != 0:
                            for j in range(notes_C_int):
                                # skip two lines
                                for k in range(2):
                                    writable.write(readable.readline())

                                n = readable.readline()
                                writable.write(n)

                                # skip 
                                for k in range(int(n.strip())):
                                    writable.write(readable.readline())

                        file_count = readable.readline()
                        file_count_int = int(file_count.strip())

                        writable.write(file_count)

                        for j in range(file_count_int):
                            # skip two lines
                            for k in range(2):
                                writable.write(readable.readline())

                            # if we are on the last line, strip whitespace.
                            if i == animset_count - 1 and j == file_count_int - 1:
                                writable.write(readable.readline().strip())
                            
                            else: writable.write(readable.readline())
                    finally:
                        writable.close()

            finally: readable.close()

        print(f"Successfully extracted {project}.")
    return 0


def extract_all(and_i_mean_all_of_them = False):
    ud = update.require_update()

    vanilla_projects_count = len(ud.vanilla_projects)
    
    # get count for total projects
    total_projects = ud.animdata_csv.shape[0]                  

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
    for project_name in ud.animdata_csv['project_name']:
        project_name = project_name.lower()
    
    to_extract = []

    match extract_everything:
        
        case True:
            to_extract = ud.cached_projects

        case False:
            to_extract = ud.new_projects

    extract_projects(to_extract)

    return 0