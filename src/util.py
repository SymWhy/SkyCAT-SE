from collections import deque
from itertools import islice
import os
from pathlib import Path
import pandas as pd
import json
import logging


# needs optimizing
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
    ("Press enter to continue...")
    input()
    return 0

def fast_skip(fileobj, n: int=1):
    # deque with maxlen=0 consumes the islice iterator without building a list.
    deque(islice(fileobj, n), maxlen=0)

def prompt_yes_no(message: str, message_y: str = None, message_n: str = None) -> bool:
    print(f"{message} Y/N")
    while True:
        match input().lower():
            case 'y':
                if message_y:
                    logging.info(message_y)
                return True
            case 'n':
                if message_n:
                    logging.info(message_n)
                return False

def dump_json(parquet: Path, dst: Path):   
    datalist = pd.read_parquet(parquet).to_dict(orient='records')

    os.makedirs(dst.parent, exist_ok=True)

    with open(dst, 'w', encoding='utf-8') as jsonfile:
        json.dump(datalist, jsonfile, indent=4)
    
    return 0