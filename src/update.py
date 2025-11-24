from pathlib import Path
import logging

import config, errors, util

class Updater:
    def __init__(self):

        # ensure the vanilla project list exists before continuing
        vanilla_projects_path = util.resource_path(Path("resources") / "vanilla_projects.txt")
        if not vanilla_projects_path.exists():
            raise FileNotFoundError("Can't find the vanilla projects list. You may need to reinstall the program.")

        # instance-scoped state (avoid shared mutable defaults)
        self.vanilla_projects = []
        self.cached_projects = []
        self.new_projects = []
        self.creature_projects = []

        self.animdata_list = None
        self.animsetdata_list = None

        self.cache_dir = None

        self.dryrun = False
    

    def update_cache(self, meshes_folder: Path = None):
        
        cfg = config.get_global('config')
        self.dryrun = config.get_global('dryrun')

        # allows us to use a custom meshes folder for testing
        if meshes_folder is None:
            meshes_folder = cfg.skyrim / "meshes"

        self.cache_dir = cfg.cache
        
        # instantiate empty temp variables
        cached_projects = []
        new_projects = []
        creature_projects = []
        
        # make sure we have our vanilla project list loaded
        vanilla_projects_path = util.resource_path(Path("resources") / "vanilla_projects.txt")
        if self.vanilla_projects == []:
            with open(vanilla_projects_path, "r", encoding="utf-8") as vanilla_dirlist:
                try:
                    # get all our vanilla project names
                    for line in vanilla_dirlist:
                        if line == "":
                            break
                        
                        self.vanilla_projects.append(line.strip().casefold())
                except IOError as e:
                    raise errors.ReadError(path=str(vanilla_dirlist), message=f"Failed to read vanilla projects list: {e}") from e

        logging.debug("Updating animdata index...")

        animdata_file = meshes_folder / config.animdata
        animsetdata_file = meshes_folder / config.animsetdata

        if not animdata_file.exists():
            raise FileNotFoundError(f"Missing animation data file: {animdata_file}")
        
        if not animsetdata_file.exists():
            raise FileNotFoundError(f"Missing animation set data file: {animsetdata_file}")

        try:
            with open(animdata_file, "r", encoding="utf-8") as readable:
                # bind repeated calls
                readline = readable.readline
                strip = str.strip

                # initialize list to hold dictionaries before passing to dataframe
                animdatalist = []                
                
                # initialize line counter
                # Note: this will be the line number in the text file MINUS ONE
                line_count = 0

                # initialize project index and name dictionary
                p_dict = {}

                try:
                    # get project count
                    total_projects_raw = strip(readline())
                    total_projects = int(total_projects_raw)
                    logging.debug(f"Expecting {total_projects} total projects.")
                    line_count += 1
                except ValueError as e:
                    raise errors.ParseError(path=str(animdata_file), message=f"Invalid total projects count '{total_projects_raw}' at line {line_count}") from e

                try:
                    # get project names
                    for i in range(total_projects):
                        myName_raw = readline()
                        myName = strip(myName_raw).split(".")[0]
                        p_dict[i] = myName
                        line_count += 1
                except ValueError as e:
                    raise errors.ParseError(path=str(animdata_file), message=f"Failed to parse project name: {myName_raw} at line {line_count}: {e}") from e

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

                    # keep track of our line skips & reset at the beginning of the loop
                    lines_skipped = 0

                    try:
                        # read line, this is the number of lines to expect for this project
                        expected_lines_raw = readline()
                        expected_lines = int(strip(expected_lines_raw))
                    except ValueError as e:
                        raise errors.ParseError(path=str(animdata_file), message=f"Invalid expected lines count '{expected_lines_raw}' at line {line_count}") from e

                    new_row["lines_anims"] = expected_lines
                    line_count += 1
                    lines_skipped += 1
                    
                    # skip a line that is identical (1) on all projects
                    util.fast_skip(readable, 1)
                    line_count += 1
                    lines_skipped += 1 
                    
                    try:
                        # the next line tells us how many hkx to expect
                        hkx_count_raw = readline()
                        hkx_count = int(strip(hkx_count_raw))
                        line_count += 1
                        lines_skipped += 1
                    except ValueError as e:
                        raise errors.ParseError(path=str(animdata_file), message=f"Invalid HKX count '{hkx_count_raw!r}' at line {line_count}") from e

                    util.fast_skip(readable, hkx_count)
                    line_count += hkx_count
                    lines_skipped += hkx_count

                    try:
                        # read boundanims flag
                        hasBoundAnims_raw = readline()
                        hasBoundAnims = int(strip(hasBoundAnims_raw))
                        line_count += 1
                    except ValueError as e:
                        raise errors.ParseError(path=str(animdata_file), message=f"Unexpected value for boundanims flag: {hasBoundAnims_raw} at line {line_count}: {e}") from e

                    # check for boundanims
                    if hasBoundAnims == 0:
                        new_row["project_type"]  = "noncreature"

                    elif hasBoundAnims == 1:
                        new_row["project_type"]  = "creature"
                    else:
                        raise errors.ParseError(path=str(animdata_file), message=f"Invalid boundanims flag '{hasBoundAnims_raw}' at line {line_count}")
                    
                    skip_animdata = expected_lines - lines_skipped
                    util.fast_skip(readable, skip_animdata)
                    line_count += skip_animdata

                    if hasBoundAnims == 1:
                        try:
                            # read number of lines expected for bound anims
                            expected_lines_raw = readline()
                            expected_lines = int(strip(expected_lines_raw))
                            line_count += 1
                        except ValueError as e:
                            raise errors.ParseError(path=str(animdata_file), message=f"Invalid boundanims line count '{expected_lines_raw}' at line {line_count}: {e}") from e

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
        except PermissionError as e:
            raise PermissionError(f"Permission denied: {e}") from e
          
        # saving local variables, will commit to class variables later
        for entry in animdatalist:
            cached_projects.append(entry['project_name'].casefold())
            if entry['project_type'] == "creature":
                creature_projects.append(entry['project_name'].casefold())

        new_projects = [proj for proj in cached_projects if proj not in self.vanilla_projects]
        if self.dryrun:
            # back up the old dataframe, restore it later
            old_animdata_list = self.animdata_list
            
        logging.debug("Updating animsetdata index...")
        # first we need to find how many projects have boundanims + root motion
        project_count = len(creature_projects)

        # initialize line count to 0
        line_count = 0

        # open the animsetdata file
        with open(animsetdata_file, "r", encoding="utf-8") as readable:
            # bind repeated calls
            readline = readable.readline
            strip = str.strip
            try:
                logging.debug(f"Expecting {project_count} creature projects.")

                try:
                    project_count_raw = strip(readline())
                    project_count_new = int(project_count_raw)

                except ValueError as e:
                    raise errors.ParseError(path=str(animsetdata_file), message=f"Invalid creature project count at line {line_count}") from e

                if project_count_new != project_count:
                    raise errors.ParseError(path=str(animsetdata_file), message=f"Creature project count mismatch: expected {project_count}, found {project_count_new} at line {line_count}")

                line_count += 1

                # skip project names, we already have them
                util.fast_skip(readable, project_count)
                line_count += project_count

                animsetdatalist = []

                for project_index in range(project_count):
                    # get project name from cached creature list
                    project_name = creature_projects[project_index]
                    
                    try:
                        # record expected anim count
                        set_count = int(strip(readline()))
                        line_count += 1
                    except ValueError as e:
                        raise errors.ParseError(path=str(animsetdata_file), message=f"Invalid animationset count: {set_count} at line {line_count}: {e}") from e

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

                        try:
                            # skip first set of notes (single line each)
                            notes_A_raw = readline()
                            notes_A = int(strip(notes_A_raw))
                            line_count += 1
                        except ValueError as e:
                            raise errors.ParseError(path=str(animsetdata_file), message=f"Invalid animationset notes count: {notes_A_raw} at line {line_count}: {e}") from e

                        if notes_A != 0:
                            util.fast_skip(readable, notes_A)
                            line_count += notes_A
                        
                        try:
                            # skip second set of notes (sets of 3)
                            notes_B_raw = readline()
                            notes_B = int(strip(notes_B_raw))
                            line_count += 1
                        except ValueError as e:
                            raise errors.ParseError(path=str(animsetdata_file), message=f"Invalid animation set notes count: {notes_B_raw} at line {line_count}: {e}") from e

                        if notes_B != 0:
                            util.fast_skip(readable, notes_B * 3) # notes B 3 lines
                            line_count += notes_B * 3

                        try:
                            # skip third set of notes (sets of 4)
                            notes_C_raw = readline()
                            notes_C = int(strip(notes_C_raw))
                            line_count += 1
                        except ValueError as e:
                            raise errors.ParseError(path=str(animsetdata_file), message=f"Invalid animation set notes count: {notes_C_raw} at line {line_count}: {e}") from e

                        # check for notes. each note is 4 lines.
                        if notes_C != 0:
                            for _ in range(notes_C):
                                # skip two lines
                                util.fast_skip(readable, 2)
                                line_count += 2

                                try:
                                    # read number of lines to skip
                                    n_raw = readline()
                                    n = int(strip(n_raw))
                                    line_count += 1
                                except ValueError as e:
                                    raise errors.ParseError(path=str(animsetdata_file), message=f"Invalid animation set notes count: {n_raw} at line {line_count}: {e}") from e

                                # skip 
                                util.fast_skip(readable, n)
                                line_count += n

                        try:
                            # this line is the number of animations (three line pairs) to expect
                            file_count_raw = readline()
                            file_count = int(strip(file_count_raw))
                            line_count +=1
                        except ValueError as e:
                            raise errors.ParseError(path=str(animsetdata_file), message=f"Invalid animation set file count: {file_count_raw} at line {line_count}: {e}") from e

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

            except (ValueError, IndexError, OSError) as e:
                raise errors.CacheError(path=str(animsetdata_file), message=f"Error while updating animsetdata: {e}") from e

            if not self.dryrun:
                self.animdata_list = animdatalist
                self.animsetdata_list = animsetdatalist

                self.cached_projects = cached_projects
                self.new_projects = new_projects
                self.creature_projects = creature_projects            
            else:
                # restore old animdata list
                self.animdata_list = old_animdata_list
            
        logging.info("Update complete.")
        return 0