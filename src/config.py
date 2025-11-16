import os
from pathlib import Path
import configparser

# constants
animdata = Path("meshes") / "animationdatasinglefile.txt"
animsetdata = Path("meshes") / "animationsetdatasinglefile.txt"

animdata_dir = Path("meshes") / "animationdata"
animsetdata_dir = Path("meshes") / "animationsetdata"
animdata_csv_path = Path("cache") / "animdata_cache.csv"
animsetdata_csv_path = Path("cache") / "animsetdata_cache.csv"

parser = configparser.ConfigParser()

class Configurator:
    def __init__(self):
        # load values from config
        if not os.path.exists('skycat.ini'):
            self.setup_config()
        self.load_config()

        
        
    # configurables
    skyrim = Path('C:') / "Steam" / "steamapps" / "common" / "Skyrim Special Edition" / "Data"
    cache = Path.home() / 'AppData' / 'Local' / 'SkyCAT-SE' / 'cache'
    backups = Path.cwd() / 'backups'

    def setup_config(self, cfgparser=parser):
        cfgparser['PATHS'] = {'sPathSSE': str(Path('C:') / "Steam" / "steamapps" / "common" / "Skyrim Special Edition" / "Data"),
                          'sPathCache': str(Path.home() / 'AppData' / 'Local' / 'SkyCAT-SE'),
                          'sPathBackups': str(Path.cwd() / 'backups')}
        with open('skycat.ini', 'w', encoding="utf-8") as configfile:
            cfgparser.write(configfile)

        
    def load_config(self, cfgparser=parser):

        if not os.path.exists('skycat.ini'):
            self.setup_config(cfgparser)
        cfgparser.read('skycat.ini')
        self.skyrim = Path(cfgparser['PATHS']['sPathSSE'])
        self.cache = Path(cfgparser['PATHS']['sPathCache'])
        self.backups = Path(cfgparser['PATHS']['sPathBackups'])

    def write_to_config(self, section, key, value, cfgparser=parser):
        if not os.path.exists('skycat.ini'):
            self.setup_config(cfgparser)
            self.load_config(cfgparser)
            
        cfgparser[section][key] = value

        with open('skycat.ini', 'w', encoding="utf-8") as configfile:
            cfgparser.write(configfile)
        self.load_config(cfgparser)

# GLOBAL CONFIG

_GLOBAL_CONFIG = None

def set_global_config(cfg):
    global _GLOBAL_CONFIG
    _GLOBAL_CONFIG = cfg
    return _GLOBAL_CONFIG

def get_global_config():
    return _GLOBAL_CONFIG

# safe getter that raises if not set
def require_config():
    cfg = get_global_config()
    if cfg is None:
        print("Global config not set. Setting now...")
        cfg = set_global_config(Configurator())
        
    return cfg