import pandas as pd
import os.path

import config

class Extractor:

    @staticmethod
    def unpack_project(cfg, query):

        query = query.lower()

        # check if we've generated our cache files
        if not os.path.exists(cfg.cache + "\\animdata_index.csv"):
            print("Error: Can't find animdata csv.")
            return

        animdata_csv = pd.read_csv(cfg.cache + "\\animdata_index.csv")

        if not os.path.exists(cfg.cache + "\\animsetdata_index.csv"):
            print("Error: Can't find animsetdata csv.")
            return

        animsetdata_csv = pd.read_csv(cfg.cache + "\\animsetdata_index.csv")

        # note: each project must have a unique name!
        # perhaps if we recieve a duplicate, we simply replace?

        project_index = animdata_csv.index[animdata_csv['project_name'] == query].to_list()[0]
        animset_index = None

        isCreature = False

        if animdata_csv.at[project_index, "project_type"] == "creature":
            isCreature = True
            animset_index = animsetdata_csv.index[animsetdata_csv['animset_name'] == query].to_list()[0]

        print("Project index for {} is {}. Animset index is {}.".format(query, project_index, animset_index))

        ### ANIMATIONDATA ###

        # check that our directory exists
        animdata_dir = config.skyrim + "meshes\\animationdata"

        if not os.path.exists(animdata_dir):
            os.makedirs(animdata_dir)

        # check if the file is already in the cache
        # if os.path.exists("meshes\\animationdata\\" + query + ".txt"):
        #     while True:
        #         print("Project file exists in cache, overwrite? Y/N")
        #         overwrite = input()
        #         if overwrite.lower() == "y":
        #             break
        #         elif overwrite.lower() == "n":
        #             return                

        # write the animdata cache file
        try:
            # open the animdata file
            readable = open(config.animdata, "r")

            try:
                animdata_cache = open(os.path.join(animdata_dir, query + ".txt"), 'w')

                # read lines up to the project start
                for _ in range(int(animdata_csv.at[project_index, "project_start"])):
                    animdata_cache.write(readable.readline())


                # skip line count
                readable.readline()

                lines_anims = int(animdata_csv.at[project_index, "lines_anims"])

                n = 1
                
                if isCreature:
                    n = 2

                for i in range(lines_anims - n):
                    animdata_cache.write(readable.readline())
                animdata_cache.write(readable.readline().strip())

            finally: animdata_cache.close()

            # write the boundanims cache file
            if isCreature:

                boundanims_dir = config.skyrim + "meshes\\animationdata\\boundanims"
                if not os.path.exists(boundanims_dir):
                    os.makedirs(boundanims_dir)

                # if os.path.exists("meshes\\animationdata\\boundanims\\anims_" + query + ".txt"):
                #     while True:
                #         print("Boundanims file exists in cache, overwrite? Y/N")
                #         overwrite = input()
                #         if overwrite.lower() == "y":
                #             break
                #         elif overwrite.lower() == "n":
                #             return              
                try:
                    boundanims_cache = open(os.path.join(boundanims_dir, "anims_" + query + ".txt"), 'w')

                    # skip whitespace and linecount
                    readable.readline()
                    readable.readline()

                    lines_boundanims = int(animdata_csv.at[project_index, "lines_boundanims"])

                    for i in range(lines_boundanims - 2):

                        boundanims_cache.write(readable.readline())

                    boundanims_cache.write(readable.readline().strip())

                finally: boundanims_cache.close()

        finally: readable.close()

        ### ANIMATIONSETDATA ###

        if isCreature:
            # check that our directory exists
            animsetdata_dir = config.skyrim +"meshes\\animationsetdata"

            if not os.path.exists(animsetdata_dir):
                os.makedirs(animsetdata_dir)

            # # check if the file is already in the cache
            # if os.path.exists("meshes\\animationsetdata\\" + query + ".txt"):
            #     while True:
            #         print("Animation set file exists in cache, overwrite? Y/N")
            #         overwrite = input()
            #         if overwrite.lower() == "y":
            #             break
            #         elif overwrite.lower() == "n":
            #             return
                    
            # write the animsetdata cache file

            try:
                # open the animdata file
                readable = open(config.animsetdata, "r")

                # skip to the project start
                for _ in range(int(animsetdata_csv.at[animset_index, "animset_start"])):
                    readable.readline()

                # get the expected number of animation sets
                animset_count = int(readable.readline().strip())
                expected_animset_count = int(animsetdata_csv.at[animset_index, "count_animsets"])

                # check to make sure the cache data matches
                if animset_count != expected_animset_count:
                    print("Error: Animset count mismatch. Regenerating the cache might fix this.")
                    print("Expected {}, got {}.".format(expected_animset_count, animset_count))
                    return

                try:
                    
                    # check to make sure the path to query's "queryprojectdata" folder exists
                    if not os.path.exists(os.path.join(animsetdata_dir, query + "data")):
                        os.makedirs(os.path.join(animsetdata_dir, query + "data"))

                    # check if the set list file is already in the cache
                    # if os.path.exists(os.path.join(animsetdata_dir, query + "data\\" + query + ".txt")):
                    #     while True:
                    #         print("Animation set list file exists in cache, overwrite? Y/N")
                    #         overwrite = input()
                    #         if overwrite.lower() == "y":
                    #             break
                    #         elif overwrite.lower() == "n":
                    #             return

                    # create the set list file
                    # this file contains a list of all the animation set text files
                    animsetlist = open(os.path.join(animsetdata_dir, query + "data\\" + query + ".txt"), 'w')

                    animset_list = []

                    # write the file names to the animstlist txt
                    for i in range(animset_count):
                        animset_list.append(readable.readline().strip().lower())

                    for item in animset_list:
                        animsetlist.write(item + "\n")

                    animsetlist.close()

                    for i in range(animset_count):
                        writable = open(os.path.join(animsetdata_dir, query + "data\\" + animset_list[i]), 'w')

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

                finally: animsetlist.close()

            finally: readable.close()


    @staticmethod
    def unpack_all(cfg, and_i_mean_all_of_them = False):

        vanilla_dirlist = open("src\\resources\\vanilla_projects.txt", "r")

        vanilla_projects = []

        # get all our vanilla project names
        while True:
            line = vanilla_dirlist.readline()

            if line == "":
                break
            
            vanilla_projects.append(line.strip().lower().split("."))

        vanilla_projects_count = len(vanilla_projects)

        animdata_csv = pd.read_csv(cfg.cache + "\\animdata_index.csv")
        
        # get count for total projects
        total_projects = animdata_csv.shape[0]                  


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
                            return

        for index in range(total_projects):
            project_name = animdata_csv.at[index, "project_name"]

            match extract_everything:
                case True:
                    Extractor.extract_project(project_name)

                case False:
                        if project_name not in vanilla_projects:
                            Extractor.extract_project(project_name)

        return