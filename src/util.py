from collections import deque
from itertools import islice
import os
from pathlib import Path
import json
import logging
import sys

import sse_bsa

import errors


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

def dump_json(data, cache: Path, dst: Path):
    # normalize to a plain list of records
    # this means we can handle pandas DataFrames or other structures
    if hasattr(data, "to_dict"):
        try:
            datalist = data.to_dict(orient='records')
        except Exception:
            # fall back to using the object directly if conversion fails
            datalist = list(data)
    else:
        datalist = list(data)

    try:
        tmpdir = cache / "tmp"
        os.makedirs(tmpdir, exist_ok=True)
        tmpfile = tmpdir / dst.name
        with open(tmpfile, 'w', encoding='utf-8') as jsonfile:
            json.dump(datalist, jsonfile, indent=4, ensure_ascii=False)

        os.makedirs(dst.parent, exist_ok=True)
        os.replace(str(tmpfile), str(dst))

        # cleanup tmp dir if empty
        try:
            os.rmdir(tmpdir)
        except OSError:
            pass

        return 0
    except (OSError, PermissionError) as e:
        raise OSError(f"Failed to write JSON file: {e}") from e
    

# Return absolute path to resource, works for dev and for PyInstaller
def resource_path(rel_path: str) -> Path:
    #if we're running in a PyInstaller bundle
    if getattr(sys, "_MEIPASS", None):
        # Get the base path from PyInstaller's temporary directory
        base = Path(sys._MEIPASS)
    else:
        # Get the base path from the current working directory
        base = Path(__file__).parent.parent
    # Return the absolute path to the resource
    return (base / rel_path).resolve()

def unpack_vanilla_cache(path):
    try:
        anims_archive = sse_bsa.BSAArchive(Path(path / "Skyrim - Animations.bsa"))
        anims_archive.extract_file(Path("meshes") / "animationdatasinglefile.txt", Path(path))
        anims_archive.extract_file(Path("meshes") / "animationsetdatasinglefile.txt", Path(path))
    except (OSError, RuntimeError) as e:
        raise errors.CacheError(path=str(path), message=f"Failed to unpack vanilla cache: {e}") from e
    return 0

# check if a directory contains the files needed
def check_valid_directory(path: Path | str) -> bool:
    # check for cache files
    path = Path(path)
    if (path / "meshes" / "animationdatasinglefile.txt").exists() and (path / "meshes" / "animationsetdatasinglefile.txt").exists():
        return True

    # check for BSA
    elif (path / "Skyrim - Animations.bsa").exists():

        if not prompt_yes_no("Animation cache appears to be missing. Unpack?",
                      message_y="Unpacking animation cache from BSA.",
                      message_n="Program cannot operate without the animation cache."):
            raise errors.UserAbort()
        # unpack BSA
        unpack_vanilla_cache(path)
        # check for cache files again
        if (path / "meshes" / "animationdatasinglefile.txt").exists() and (path / "meshes" / "animationsetdatasinglefile.txt").exists():
            return True
        else:
            raise errors.CacheError("Failed to unpack animation cache from BSA.")
    else:
        return False

    