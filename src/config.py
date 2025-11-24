from pathlib import Path
import configparser
import logging
from tkinter import filedialog

import errors

# constants
animdata = Path("animationdatasinglefile.txt")
animsetdata = Path("animationsetdatasinglefile.txt")

animdata_dir = Path("meshes") / "animationdata"
animsetdata_dir = Path("meshes") / "animationsetdata"

parser = configparser.ConfigParser()

class Configurator:
    def __init__(self):
        # load values from config
        if not Path('skycat.ini').exists():
            self.setup_config()
        self.load_config()
        return None
        
    # configurables
    skyrim = Path('C:') / "Steam" / "steamapps" / "common" / "Skyrim Special Edition" / "Data"
    cache = Path.home() / 'AppData' / 'Local' / 'SkyCAT-SE'
    backups = Path.cwd() / 'backups'

    def setup_config(self, cfgparser=parser):
        cfgparser['PATHS'] = {'sPathSSE': str(filedialog.askdirectory(title="Select Skyrim SE Data folder.", mustexist=True)),
                          'sPathCache': str(Path.home() / 'AppData' / 'Local' / 'SkyCAT-SE'),
                          'sPathBackups': str(Path.cwd() / 'backups')}
        with open('skycat.ini', 'w', encoding="utf-8") as configfile:
            cfgparser.write(configfile)

        
    def load_config(self, cfgparser=parser):
        try:
            if not Path('skycat.ini').exists():
                self.setup_config(cfgparser)
            cfgparser.read('skycat.ini')
        except IOError as e:
            raise errors.ConfigError(message=f"Could not read config: {e}") from e
        
        self.skyrim = Path(cfgparser['PATHS']['sPathSSE'])
        self.cache = Path(cfgparser['PATHS']['sPathCache'])
        self.backups = Path(cfgparser['PATHS']['sPathBackups'])
        return 0

    def write_to_config(self, section: str, key: str, value: str, cfgparser=parser):
        if not Path('skycat.ini').exists():
            self.setup_config(cfgparser)
            self.load_config(cfgparser)
            
        cfgparser[section][key] = value

        try:
            with open('skycat.ini', 'w', encoding="utf-8") as configfile:
                cfgparser.write(configfile)
            self.load_config(cfgparser)
        except IOError as e:
            raise errors.ConfigError(message=f"Could not write config: {e}") from e
        return 0

# GLOBALS
_GLOBAL_CONFIG = None
_GLOBAL_UPDATE = None
_GLOBAL_LOGGER = None
_DRYRUN = False

def set_globals(cfg, ud, dryrun=False):
    global _GLOBAL_CONFIG, _GLOBAL_UPDATE, _GLOBAL_LOGGER, _DRYRUN
    _GLOBAL_CONFIG = cfg
    _GLOBAL_UPDATE = ud
    _GLOBAL_LOGGER = logging.getLogger(__name__)
    _DRYRUN = dryrun
    return 0

# safe getter that raises if not set
def get_global(global_type):
    if global_type == 'config':
        if not _GLOBAL_CONFIG:
            raise errors.ConfigError(message="Global config not set!")
        return _GLOBAL_CONFIG
    elif global_type == 'update':
        if not _GLOBAL_UPDATE:
            raise errors.ConfigError(message="Global update not set!")
        return _GLOBAL_UPDATE
    elif global_type == 'logger':
        if not _GLOBAL_LOGGER:
            raise errors.ConfigError(message="Global logger not set!")
        return _GLOBAL_LOGGER
    elif global_type == 'dryrun':
        return _DRYRUN
    else:
        logging.warning(f"Unknown global type requested: {global_type}")
        return None