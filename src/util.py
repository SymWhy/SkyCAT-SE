from collections import deque
from itertools import islice
import os
from pathlib import Path
import pandas as pd
import json

def get_path_case_insensitive(source: Path):
    parent = source.parent
    target_name = source.name.casefold()
    try:
        for child in parent.iterdir():
            if child.name.casefold() == target_name:
                return child
    except FileNotFoundError:
        return None

def count_lines_and_strip(file: Path):

    with open(file, 'r', encoding="utf-8") as rfile:
        line_count = 0

        # count total lines in file
        for count, line in enumerate(rfile):
            line_count = count
        
        line_count += 1  # adjust for 0 indexing

        rfile.seek(0)

        # count lines in file up to our recorded line count
        for _ in range(line_count):
            
            line = rfile.readline()

            # check if we're at the end of the file and the last line is blank
            if rfile.tell() == os.fstat(rfile.fileno()).st_size and line.strip() == "\n":
                line_count -= 1

                # return to the top
                rfile.seek(0)

    return line_count

def pause_wait_for_input():
    print("Press enter to continue...")
    input()
    return 0

def fast_skip(fileobj, n):
    # deque with maxlen=0 consumes the islice iterator without building a list.
    deque(islice(fileobj, n), maxlen=0)
import io

def dump_json(parquet: Path, dst: Path):   
    datalist = pd.read_parquet(parquet).to_dict(orient='records')

    with open(dst, 'w', encoding='utf-8') as jsonfile:
        json.dump(datalist, jsonfile, indent=4)
    
    return 0