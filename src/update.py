from pathlib import Path
import os.path
import pandas as pd
import pyarrow.parquet as pq

import config
import util

class Updater:
    # instantiate empty variables
    vanilla_projects = []
    cached_projects = []
    new_projects = []
    creature_projects = []

    animdata_df = None
    animsetdata_df = None

    cache_dir = None
    skyrim_dir = None

    dryrun = False

    def __init__(self):
        if not os.path.exists(Path("src") / "resources" / "vanilla_projects.txt"):
            print("Error: Missing vanilla projects list. You may need to reinstall the program.")
            return
        return

    def update_cache(self):
        
        cfg = config.get_global('config')
        self.dryrun = config.get_global('dryrun')

        self.cache_dir = cfg.cache
        self.skyrim_dir = cfg.skyrim

        
        # instantiate empty temp variables
        cached_projects = []
        new_projects = []
        creature_projects = []

        # make sure any stray backups have been deleted
        clean_parquet_backups(self.cache_dir / "cache")
        
        # backup old cache files
        backup_parquets(self.cache_dir / "cache")

        # make sure we have our vanilla project list loaded
        if self.vanilla_projects == []:
            with open(Path("src") / "resources" / "vanilla_projects.txt", "r", encoding="utf-8") as vanilla_dirlist:
                try:
                    # get all our vanilla project names
                    for line in vanilla_dirlist:
                        if line == "":
                            break
                        
                        self.vanilla_projects.append(line.strip().lower())
                except Exception as e:
                    print(f"Error loading vanilla project list: {e}")
                    restore_parquets(self.cache_dir)
                    return

        animdata = config.animdata
        animsetdata = config.animsetdata

        print("Updating animdata index...")

        with open(self.skyrim_dir / animdata, "r", encoding="utf-8") as readable:
            # bind repeated calls
            readline = readable.readline
            strip = str.strip

            try:
                # initialize list to hold dictionaries before passing to dataframe
                animdatalist = []                
                
                # initialize line counter
                # Note: this will be the line number in the text file MINUS ONE
                line_count = 0

                # initialize project index and name dictionary
                p_dict = {}

                # # debug flag
                # found_my_creature = False

            except Exception as e:
                print(f"Error initializing animdata index: {e}")
                restore_parquets(self.cache_dir)
                return

            try:
                # get project count
                total_projects = int(strip(readline()))
                print(f"Expecting {total_projects} total projects.")
                line_count += 1

                # get project names
                for i in range(total_projects):
                    myName = strip(readline()).split(".")[0]
                    p_dict[i] = myName
                    line_count += 1
                    
                # typical read loop
                for i in range(total_projects):
                    # Add new row for current project
                    new_row = {
                        "project_name": p_dict[i].lower(), # name of project
                        "project_type": None, # whether it's a creature or noncreature project
                        "project_start": line_count, # this is the line right before the project starts
                        "project_end": None, # line number where project ends
                        "lines_anims": 0, # expected number of lines for base anim data
                        "lines_boundanims": 0 # expected number of lines for bound anim data. 0 if nonexistent.
                        }

                    # # debug check for test projects
                    # project_name = p_dict[i].lower()
                    # if project_name == "woodenbow".lower():
                    #     found_my_creature = True
                    #     os.system("pause")

                    # keep track of our line skips & reset at the beginning of the loop
                    lines_skipped = 0

                    # read line, this is the number of lines to expect for this project
                    expected_lines = int(strip(readline()))

                    new_row["lines_anims"] = expected_lines
                    line_count += 1
                    lines_skipped += 1
                    
                    # skip a line that is identical (1) on all projects
                    util.fast_skip(readable, 1)
                    line_count += 1
                    lines_skipped += 1 
                    
                    # the next line tells us how many hkx to expect
                    hkx_count = int(strip(readline()))
                    line_count += 1
                    lines_skipped += 1

                    util.fast_skip(readable, hkx_count)
                    line_count += hkx_count
                    lines_skipped += hkx_count

                    hasBoundAnims = int(strip(readline()))
                    line_count += 1
                    
                    # check for boundanims
                    if hasBoundAnims == 0:
                        new_row["project_type"]  = "noncreature"

                    elif hasBoundAnims == 1:
                        new_row["project_type"]  = "creature"
                    else:
                        print("Error: unexpected value when checking for boundanims.")
                        print("The value given was: {}".format(hasBoundAnims))
                        restore_parquets(self.cache_dir)
                        return
                    
                    skip_animdata = expected_lines - lines_skipped
                    util.fast_skip(readable, skip_animdata)
                    line_count += skip_animdata

                    if hasBoundAnims == 1:
                        # read number of lines expected for bound anims
                        expected_lines = int(strip(readline()))
                        line_count += 1 

                        # record expected bound anim line count
                        new_row["lines_boundanims"] = expected_lines

                        # skip lines containing the actual bound anim data (including the final newline)
                        util.fast_skip(readable, expected_lines)
                        line_count += expected_lines
                        
                    # Mark the project end
                    new_row["project_end"] = line_count

                    # append new row to list of rows
                    animdatalist.append(new_row)
                    i += 1

                if not self.dryrun:
                    
                    self.animdata_df = pd.DataFrame.from_records(animdatalist)
                    
                    # only save variables if we're not in dry run mode
                    for entry in animdatalist:
                        cached_projects.append(entry['project_name'])
                        if entry['project_type'] == "creature":
                            creature_projects.append(entry['project_name'])

                    new_projects = [proj for proj in cached_projects if proj not in self.vanilla_projects]
            
            # note: we don't want to raise here, we can fix the cache later
            except Exception as e:
                print(f"Error at line {line_count} while updating animdata: {e}")
                restore_parquets(self.cache_dir)
                return None
            
        print("Updating animsetdata index...")

        # first we need to find how many projects have boundanims + root motion
        project_count = len(creature_projects)

        # initialize line count to 0
        line_count = 0

        # open the animsetdata file
        with open(self.skyrim_dir / animsetdata, "r", encoding="utf-8") as readable:
            # bind repeated calls
            readline = readable.readline
            strip = str.strip

            print(f"Expecting {project_count} creature projects.")

            try:
                # make sure we're expecting the right number of projects
                if int(strip(readline())) != project_count:
                    print("Error: Creature count mismatch!")
                    restore_parquets(self.cache_dir)
                    return None

                line_count += 1

                # skip project names, we already have them
                util.fast_skip(readable, project_count)
                line_count += project_count

                animsetdatalist = []

                for project_index in range(project_count):
                    # get project name from cached creature list
                    project_name = creature_projects[project_index]

                    # record expected anim count
                    set_count = int(strip(readline()))
                    line_count += 1

                    new_row = {
                        "animset_name": project_name.lower(), # name of project
                        "animset_start": line_count - 1, # line number where project starts
                        "animset_end": None, # line number where project ends
                        "lines_animsets": 0, # expected number of lines for base animset data
                        "count_animsets": set_count # expected number of animsets
                    }

                    # skip the text file lines
                    util.fast_skip(readable, set_count)
                    line_count += set_count

                    for i in range(set_count):
                        # skip "V3"
                        util.fast_skip(readable, 1)
                        line_count += 1

                        # skip first set of notes (single line each)
                        notes_A = int(strip(readline()))
                        line_count += 1

                        if notes_A != 0:
                            util.fast_skip(readable, notes_A)
                            line_count += notes_A
                        
                        # skip second set of notes (sets of 3)
                        notes_B = int(strip(readline()))
                        line_count += 1

                        if notes_B != 0:
                            util.fast_skip(readable, notes_B * 3) # notes B 3 lines
                            line_count += notes_B * 3

                        # skip third set of notes (sets of 4)
                        notes_C = int(strip(readline()))
                        line_count += 1

                        # check for notes. each note is 4 lines.
                        if notes_C != 0:
                            for _ in range(notes_C):
                                # skip two lines
                                util.fast_skip(readable, 2)
                                line_count += 2

                                n = int(strip(readline()))
                                line_count += 1

                                # skip 
                                util.fast_skip(readable, n)
                                line_count += n

                        # this line is the number of animations (three line pairs) to expect
                        file_count = int(strip(readline()))
                        line_count +=1

                        # skip three lines per animation file
                        # 2046540817 <- path to animations folder
                        # 329189360 <- animation file name
                        # 7891816 <- hkx extension (always same number, uses little-endian encoding)

                        util.fast_skip(readable, file_count * 3)
                        line_count += file_count * 3

                        if i == set_count - 1:
                            new_row["animset_end"] = line_count - 1
                            new_row["lines_animsets"] = (line_count) - new_row["animset_start"]
                        
                    animsetdatalist.append(new_row)

                if not self.dryrun:
                    self.animdata_df = pd.DataFrame.from_records(animdatalist)
                    self.animsetdata_df = pd.DataFrame.from_records(animsetdatalist)

                    self.cached_projects = cached_projects
                    self.new_projects = new_projects
                    self.creature_projects = creature_projects

                    pq_dir = self.cache_dir / "cache"

                    try: os.makedirs(pq_dir, exist_ok=True)
                    except Exception as e:
                        print(f"Error creating cache directory: {e}")
                        restore_parquets(pq_dir)
                        return
                    
                    if not os.path.exists(pq_dir):
                        print("Error: Could not create cache directory.")
                        restore_parquets(pq_dir)
                        return

                    # create parquets
                    self.animdata_df.to_parquet(pq_dir / "animdata_cache.parquet.tmp")
                    self.animsetdata_df.to_parquet(pq_dir / "animsetdata_cache.parquet.tmp")

                    # replace old parquets with new ones
                    os.replace(pq_dir / "animdata_cache.parquet.tmp", pq_dir / "animdata_cache.parquet")
                    os.replace(pq_dir / "animsetdata_cache.parquet.tmp", pq_dir / "animsetdata_cache.parquet")

                    # clean up backup files
                    clean_parquet_backups(self.cache_dir / "cache")

            except Exception as e:
                restore_parquets(self.cache_dir)
                raise Exception(f"Error while updating animsetdata: {e}")
            
        print("Update complete.")
        return 0
    

def load_dataframes(cache_dir):
    if not os.path.exists(cache_dir / config.animdata_pq_path):
        print("Error: Parquet cache not found. Please run update first.")
        return None
    
    animdata_df = pd.read_parquet(cache_dir / config.animdata_pq_path)
    animsetdata_df = pd.read_parquet(cache_dir / config.animsetdata_pq_path)
    return animdata_df, animsetdata_df

def backup_parquets(cache_dir):
    animdata_bak = None
    animsetdata_bak = None

# backup old program cache files
    if os.path.exists(cache_dir / config.animdata_pq_path):
        animdata_bak = os.rename(cache_dir / config.animdata_pq_path, cache_dir / "animdata.parquet.bak")
    if os.path.exists(cache_dir / config.animsetdata_pq_path):
        animsetdata_bak = os.rename(cache_dir / config.animsetdata_pq_path, cache_dir / "animsetdata.parquet.bak")
    return animdata_bak, animsetdata_bak

def restore_parquets(cache_dir):
    animdata_restored = None
    animsetdata_restored = None
    # restore old program cache files
    if os.path.exists(cache_dir / "animdata.parquet.bak"):
        animdata_restored = os.rename(cache_dir / "animdata.parquet.bak", cache_dir / "animdata.parquet")
    if os.path.exists(cache_dir / "animsetdata.parquet.bak"):
        animsetdata_restored = os.rename(cache_dir / "animsetdata.parquet.bak", cache_dir / "animsetdata.parquet")
    return animdata_restored, animsetdata_restored

def clean_parquet_backups(cache_dir):
    # delete backup files
    if os.path.exists(cache_dir / "animdata.parquet.bak"):
        os.remove(cache_dir / "animdata.parquet.bak")
    if os.path.exists(cache_dir / "animsetdata.parquet.bak"):
        os.remove(cache_dir / "animsetdata.parquet.bak")
    return 0