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
        # Ask the user for the Skyrim SE Data folder. If the dialog is cancelled
        # askdirectory returns an empty string; treat that as a user abort and
        # do not write an empty config file.
        skyrim_path = filedialog.askdirectory(title="Select Skyrim SE Data folder.", mustexist=True)
        if not skyrim_path or skyrim_path == "":
            raise errors.UserAbort(message="Operation cancelled by user.")

        # Require both cache files to exist either in the selected Skyrim Data folder
        # or in the application's local 'meshes' folder.
        s_mesh = Path(skyrim_path) / 'meshes'
        local_mesh = Path('meshes')
        if not ((s_mesh / 'animationdatasinglefile.txt').exists() and (s_mesh / 'animationsetdatasinglefile.txt').exists()) and not ((local_mesh / 'animationdatasinglefile.txt').exists() and (local_mesh / 'animationsetdatasinglefile.txt').exists()):
            raise FileNotFoundError("Selected directory does not appear to contain a valid animation cache.")

        cfgparser['PATHS'] = {
            'sPathSSE': str(skyrim_path),
            'sPathCache': str(Path.home() / 'AppData' / 'Local' / 'SkyCAT-SE'),
            'sPathBackups': str(Path.cwd() / 'backups')
        }

        with open('skycat.ini', 'w', encoding="utf-8") as configfile:
            cfgparser.write(configfile)
        return skyrim_path

        
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

        if value is not None:
            cfgparser[section][key] = value
        else:
            raise errors.ConfigError(message="No value provided to write to config.")

        try:
            with open('skycat.ini', 'w', encoding="utf-8") as configfile:
                cfgparser.write(configfile)
            self.load_config(cfgparser)
        except IOError as e:
            raise errors.ConfigError(message=f"Could not write config: {e}") from e
        return 0
    
def move_data(new_dir: Path = None):
    # Change the data directory
    cfg = get_global('config')

    if new_dir == None:
        new_dir = filedialog.askdirectory(title="Select Skyrim SE Data folder.", mustexist=True)
        if not new_dir:
            raise errors.UserAbort(message="Operation cancelled by user.")
        
    try:
        cfg.write_to_config('PATHS', 'sPathSSE', str(new_dir))
    except (OSError, PermissionError) as e:
        raise errors.ConfigError(message=f"Failed to write to config: {e}") from e

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