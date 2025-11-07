import pandas as pd
import os.path

import defs

class Updater:
    
    @staticmethod
    def update_animdata(animdata):
        readable = open(animdata, "r")

        data = pd.DataFrame(columns=["project_name", # name of project
                                    "project_type", # whether it's a creature or noncreature project
                                    "project_start", # line number where project starts
                                    "project_start_bits", # bit where the project starts
                                    "project_end", # line number where project ends
                                    "project_end_bits", # bit where the project ends
                                    "lines_anims", # expected number of lines for base anim data
                                    "lines_boundanims", # expected number of lines for bound anim data. 0 if nonexistant.
                                    ])
        
        data.head()

        # initialize line counter
        # Note: this will be the line number in the text file MINUS ONE
        line_count = 0

        # initialize project index and name dictionary
        p_dict = {}

        try:
            # get project count
            total_projects = int(readable.readline().strip())
            print("Expecting {} total projects.".format(total_projects))
            line_count += 1

            # get project names
            for i in range(total_projects):
                myName = readable.readline().strip().split(".")[0]
                p_dict[i] = myName
                line_count += 1

            # print(line_index) # expecting 430, got 430
                
            # typical read loop
            for i in range(total_projects):
                # Add new row for current project
                new_row = {
                    "project_name": p_dict[i].lower(),
                    "project_start": line_count + 1,
                    "project_start_bits": readable.tell()
                    }
                
                # Append new row to DataFrame
                data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
                                
                project_name = p_dict[i].lower()

                # keep track of our line skips & reset at the beginning of the loop
                lines_skipped = 0

                # read line, this is the number of lines to expect for this project
                expected_lines = int(readable.readline().strip())

                data.at[i, "lines_anims"] = expected_lines

                # print("Expecting {} lines.".format(expected_lines))
                line_count += 1
                lines_skipped += 1
                # print(line_index)

                # print(line_count) # expecting 431, got 431

                print("Reading project: {}".format(p_dict[i]))
                

                # skip a line that is identical (1) on all projects
                readable.readline()
                line_count += 1
                lines_skipped += 1 
                # print(line_index) # expected 432, got 432
                
                # the next line tells us how many hkx to expect
                hkx_count = int(readable.readline().strip())
                # print("HKX Count: {}".format(hkx_count))
                line_count += 1
                lines_skipped += 1
                # print(line_index) # expected 433, got 433

                for j in range(hkx_count):
                    # skip hkx lines
                    readable.readline()
                    line_count += 1
                    # print(line_count)
                    lines_skipped += 1

                hasBoundAnims = int(readable.readline().strip())
                line_count += 1

                ## All's good up to here!
                # print("Good up to {} at line {}.".format(hasBoundAnims, line_count))
                
                # check for boundanims
                if hasBoundAnims == 0:
                    data.at[i, "project_type"]  = "noncreature"
                    data.at[i, "lines_boundanims"] = 0
                    print("No boundanims found.")

                elif hasBoundAnims == 1:
                    data.at[i, "project_type"]  = "creature"
                    print("Boundanims found!")
                else:
                    print("Error: unexpected value when checking for boundanims.")
                    print("The value given was: {}".format(hasBoundAnims))
                    return
                
                # subtract skipped lines from expected lines and skip the rest
                for j in range (expected_lines - lines_skipped):
                    readable.readline()
                    line_count += 1

                # print(line_count) # expecting 759

                if hasBoundAnims == 1:
                    # read number of lines expected for bound anims
                    expected_lines = int(readable.readline().strip())

                    # print("Expecting {} lines.".format(expected_lines))
                    line_count += 1 

                    # record expected bound anim line count
                    data.at[i, "lines_boundanims"] = expected_lines

                    # skip lines containing the actual bound anim data

                    for j in range (expected_lines - 1):
                        readable.readline()
                        line_count += 1

                    # print(line_count) # expecting 979

                    # read empty line at end of boundanims
                    readable.readline()
                    line_count += 1
                    
                # Mark the project end
                data.at[i, "project_end"] = line_count
                data.at[i, "project_end_bits"] = readable.tell()

                i += 1
                # print(line_count) # expecting 9792
                # print(project_index) # expecting 1, 

                # print(data.head())
                # break

            data.to_csv("skycat\\cache\\animdata_index.csv", index=False)
        finally:
            readable.close()

    @staticmethod
    def update_animsetdata(animsetdata):
        
        # check if we already have a csv, if not run update_animdata()
        try:
            if not os.path.isfile("skycat\\cache\\animdata_index.csv"):
                Updater.update_animdata(defs.animdata)
        except:
            print("Error: Can't find CSV!")

        animdata_csv = pd.read_csv("skycat\\cache\\animdata_index.csv")
        
        # create empty dataframe
        data = pd.DataFrame(columns=["animset_name", # name of project
                                    "animset_start", # line number where project starts
                                    "animset_start_bits", # bit where the project starts
                                    "animset_end", # line number where project ends
                                    "animset_end_bits", # bit where the project ends
                                    "lines_animsets", # expected number of lines for base animset data
                                    ])

        # first we need to find how many projects have boundanims + root motion
        project_count = len(animdata_csv[(animdata_csv['project_type'] == "creature")])

        # initialize line count to 0
        line_count = 0

        # open the animsetdata file
        readable = open(animsetdata, "r")

        try:
            # make sure we're expecting the right number of projects
            if int(readable.readline().strip()) != project_count:
                print("Error: Creature count mismatch!")
            else:
                print("Expecting {} creature projects.".format(project_count))

            line_count += 1

            # skip project names, we already have them
            for i in range(project_count):
                readable.readline()
                line_count += 1
            
            # print(line_count) # expecting 50, got 50

            # initialize creature name list
            creatures_list = animdata_csv[animdata_csv['project_type'] == "creature"].loc[:, 'project_name'].tolist()

            for project_index in range(project_count):

                project_name = creatures_list[project_index]
                
                # record project name, line and bit count
                data.at[project_index, "animset_name"] = project_name.lower()
                data.at[project_index, "animset_start"] = line_count + 1
                data.at[project_index, "animset_start_bits"] = readable.tell()

                # record expected anim count
                set_count = int(readable.readline().strip())
                line_count += 1

                data.at[project_index, "count_animsets"] = set_count

                # skip the text file lines
                for i in range(set_count):
                    readable.readline()
                    line_count += 1

                for i in range(set_count):
                    # skip "V3"
                    readable.readline()
                    line_count += 1

                    # skip first set of notes (single line each)
                    notes_A = int(readable.readline().strip())
                    line_count += 1

                    if notes_A != 0:
                        for j in range(notes_A):
                            readable.readline()
                            line_count += 1

                    # skip second set of notes (sets of 3)
                    notes_B = int(readable.readline().strip())
                    line_count += 1

                    if notes_B != 0:
                        for j in range(notes_B):
                            for k in range(3):
                                readable.readline()
                                line_count += 1

                    # skip third set of notes (sets of 4)
                    notes_C = int(readable.readline().strip())
                    line_count += 1

                    # check for notes. each note is 4 lines.
                    if notes_C != 0:
                        for j in range(notes_C):
                            # skip two lines
                            for k in range(2):
                                readable.readline()
                                line_count += 1

                            n = int(readable.readline().strip())
                            line_count += 1

                            # skip 
                            for k in range(n):
                                readable.readline()
                                line_count += 1

                    # this line is the number of animations (three line pairs) to expect
                    file_count = int(readable.readline().strip())
                    line_count +=1

                    for j in range(file_count):
                        # skip two lines
                        for k in range(3):
                            readable.readline()
                            line_count += 1

                    if i == set_count - 1:
                        data.at[project_index, "animset_end"] = line_count
                        data.at[project_index, "animset_end_bits"] = readable.tell()
                        data.at[project_index, "lines_animsets"] = (line_count + 1) - data.at[project_index, "animset_start"]

            # print(data.head())
            data.to_csv("skycat\\cache\\animsetdata_index.csv", index=False)

        finally:
            readable.close()