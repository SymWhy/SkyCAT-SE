import os
from pathlib import Path
import configparser
import logging
from tkinter import filedialog

import errors, util

# constants
animdata = Path("animationdatasinglefile.txt")
animsetdata = Path("animationsetdatasinglefile.txt")

animdata_dir = Path("meshes") / "animationdata"
animsetdata_dir = Path("meshes") / "animationsetdata"

parser = configparser.ConfigParser()

class Configurator:
        
    # configurables
    skyrim = Path('C:') / "Steam" / "steamapps" / "common" / "Skyrim Special Edition" / "Data"
    cache = Path.home() / 'AppData' / 'Local' / 'SkyCAT-SE'
    backups = Path.cwd() / 'backups'

    def setup_config(self, cfgparser=parser):
        ini_file = Path('skycat.ini')

        if ini_file.exists():
            cfgparser.read(ini_file)
            # Ask the user for the Skyrim SE Data folder. If the dialog is cancelled
            # askdirectory returns an empty string; treat that as a user abort and
            # do not write an empty config file.
            if util.check_valid_directory(cfgparser.get('PATHS', 'sPathSSE', fallback="")):
                self.load_config(cfgparser)
                return 0
        
        skyrim_path = filedialog.askdirectory(title="Select Skyrim SE Data folder.", mustexist=True)

        # abort if empty
        if not skyrim_path or skyrim_path == "":
            raise errors.UserAbort()

        if not util.check_valid_directory(skyrim_path):
            raise errors.CacheError("Selected directory does not appear to contain a valid animation cache.")

        self.set_defaults(skyrim_path, cfgparser)
        self.load_config(cfgparser)
        return 0

    def set_defaults(self, skyrim_path, cfgparser=parser):
        cfgparser['PATHS'] = {'sPathSSE': str(skyrim_path),
                            'sPathCache': str(Path.home() / 'AppData' / 'Local' / 'SkyCAT-SE'),
                            'sPathBackups': str(Path.cwd() / 'backups')}
        with open(Path('skycat.ini'), 'w', encoding="utf-8") as configfile:
            cfgparser.write(configfile)
        
    def load_config(self, cfgparser=parser):
        ini_file = Path('skycat.ini')

        # check if config file exists
        if not ini_file.exists():
            return self.setup_config(cfgparser)

        cfgparser.read(ini_file)

        # Safely obtain values with fallbacks to avoid KeyError/NoSectionError.
        sPathSSE = cfgparser.get('PATHS', 'sPathSSE', fallback=None)
        if not sPathSSE or not util.check_valid_directory(Path(sPathSSE)):
            return self.setup_config(cfgparser)

        # Read optional paths, falling back to current defaults if missing.
        sPathCache = cfgparser.get('PATHS', 'sPathCache', fallback=str(self.cache))
        sPathBackups = cfgparser.get('PATHS', 'sPathBackups', fallback=str(self.backups))

        self.skyrim = Path(sPathSSE)
        self.cache = Path(sPathCache)
        self.backups = Path(sPathBackups)
        return 0
    
    def write_to_config(self, section: str, key: str, value: str, cfgparser=parser):
        if value is not None:
            try:
                if not cfgparser.has_section(section):
                    cfgparser.add_section(section)
                cfgparser[section][key] = value
            except KeyError:
                raise errors.ConfigError(message=f"Failed to add section {section} to config.")
        else:
            raise errors.ConfigError(message="No value provided to write to config.")

        try:
            with open(Path('skycat.ini'), 'w', encoding="utf-8") as configfile:
                cfgparser.write(configfile)
            self.load_config(cfgparser)
        except IOError as e:
            raise errors.ConfigError(message=f"Could not write config: {e}") from e
        return 0
    
def change_data_dir(new_dir: Path = None):
    # Change the data directory
    cfg = get_global('config')

    if new_dir == None:
        new_dir = filedialog.askdirectory(title="Select Skyrim SE Data folder.", mustexist=True)
        if not new_dir:
            raise errors.UserAbort()
        
    try:
        cfg.write_to_config('PATHS', 'sPathSSE', str(new_dir))
    except (OSError, PermissionError) as e:
        raise errors.ConfigError(message=f"Failed to write to config: {e}") from e
    return 0

# GLOBALS
_GLOBAL_CONFIG = None
_GLOBAL_UPDATE = None
_GLOBAL_LOGGER = None
_DRYRUN = False
_YESIMSURE = False

def set_globals(cfg, ud, dryrun=False, yes_im_sure: bool = False):
    global _GLOBAL_CONFIG, _GLOBAL_UPDATE, _GLOBAL_LOGGER, _DRYRUN
    _GLOBAL_CONFIG = cfg
    _GLOBAL_UPDATE = ud
    _GLOBAL_LOGGER = logging.getLogger(__name__)
    _DRYRUN = dryrun
    _YESIMSURE = yes_im_sure
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
    elif global_type == 'yesimsure':
        return _YESIMSURE
    else:
        logging.warning(f"Unknown global type requested: {global_type}")
        return None