import os
from pathlib import Path
import configparser
from tkinter import filedialog

import util

# constants
animdata = Path("meshes") / "animationdatasinglefile.txt"
animsetdata = Path("meshes") / "animationsetdatasinglefile.txt"

animdata_dir = Path("meshes") / "animationdata"
animsetdata_dir = Path("meshes") / "animationsetdata"
animdata_pq_path = Path("cache") / "animdata_cache.parquet"
animsetdata_pq_path = Path("cache") / "animsetdata_cache.parquet"
animdata_json_path = Path("cache") / "animdata_cache.json"
animsetdata_json_path = Path("cache") / "animsetdata_cache.json"

parser = configparser.ConfigParser()

class Configurator:
    def __init__(self):
        # load values from config
        if not os.path.exists('skycat.ini'):
            self.setup_config()
        self.load_config()
        return None
        
    # configurables
    skyrim = Path('C:') / "Steam" / "steamapps" / "common" / "Skyrim Special Edition" / "Data"
    cache = Path.home() / 'AppData' / 'Local' / 'SkyCAT-SE' / 'cache'
    backups = Path.cwd() / 'backups'

    def setup_config(self, cfgparser=parser):
        cfgparser['PATHS'] = {'sPathSSE': str(filedialog.askdirectory(title="Select Skyrim SE Data folder.", mustexist=True)),
                          'sPathCache': str(Path.home() / 'AppData' / 'Local' / 'SkyCAT-SE'),
                          'sPathBackups': str(Path.cwd() / 'backups')}
        with open('skycat.ini', 'w', encoding="utf-8") as configfile:
            cfgparser.write(configfile)

        
    def load_config(self, cfgparser=parser):
        try:
            if not os.path.exists('skycat.ini'):
                self.setup_config(cfgparser)
            cfgparser.read('skycat.ini')
        except Exception as e:
            print(f"Error writing config: {e}")
            return None
        
        self.skyrim = Path(cfgparser['PATHS']['sPathSSE'])
        self.cache = Path(cfgparser['PATHS']['sPathCache'])
        self.backups = Path(cfgparser['PATHS']['sPathBackups'])
        return 0

    def write_to_config(self, section: str, key: str, value: str, cfgparser=parser):
        if not os.path.exists('skycat.ini'):
            self.setup_config(cfgparser)
            self.load_config(cfgparser)
            
        cfgparser[section][key] = value

        try:
            with open('skycat.ini', 'w', encoding="utf-8") as configfile:
                cfgparser.write(configfile)
            self.load_config(cfgparser)
        except Exception as e:
            print(f"Error writing config: {e}")
            return None
        return 0

# GLOBALS
_GLOBAL_CONFIG = None
_GLOBAL_UPDATE = None
_DRYRUN = False

def set_globals(cfg, ud, dryrun=False):
    global _GLOBAL_CONFIG, _GLOBAL_UPDATE, _DRYRUN
    _GLOBAL_CONFIG = cfg
    _GLOBAL_UPDATE = ud
    _DRYRUN = dryrun
    return 0

# safe getter that raises if not set
def get_global(global_type):
    if global_type == 'config':
        if not _GLOBAL_CONFIG:
            raise Exception("Global config not set!")
        return _GLOBAL_CONFIG
    elif global_type == 'update':
        if not _GLOBAL_UPDATE:
            raise Exception("Global update not set!")
        return _GLOBAL_UPDATE
    elif global_type == 'dryrun':
        return _DRYRUN
    else:
        print("Invalid global type requested!")
        return None