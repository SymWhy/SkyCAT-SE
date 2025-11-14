import os
import configparser

# constants
animdata = "\\meshes\\animationdatasinglefile.txt"
animsetdata = "\\meshes\\animationsetdatasinglefile.txt"

animdata_dir = "\\meshes\\animationdata"
animsetdata_dir = "\\meshes\\animationsetdata"

animdata_csv_path = "\\cache\\animdata_cache.csv"
animsetdata_csv_path = "\\cache\\animsetdata_cache.csv"

parser = configparser.ConfigParser()

class Configurator:
    def __init__(self):
        # load values from config
        if not os.path.exists('skycat.ini'):
            self.setup_config()
        self.load_config()

        
        
    # configurables
    skyrim = 'C:\\Steam\\steamapps\\common\\Skyrim Special Edition\\Data'
    cache = os.path.expanduser('~') + '\\AppData\\Local\\SkyCAT-SE\\cache'
    backups = os.getcwd() + '\\backups'

    def setup_config(self, cfgparser=parser):
        cfgparser['PATHS'] = {'sPathSSE': 'C:\\Steam\\steamapps\\common\\Skyrim Special Edition\\Data',
                          'sPathCache': os.path.expanduser('~') + '\\AppData\\Local\\SkyCAT-SE',
                          'sPathBackups': os.getcwd() + '\\backups'}
        with open('skycat.ini', 'w') as configfile:
            cfgparser.write(configfile)

        
    def load_config(self, cfgparser=parser):

        if not os.path.exists('skycat.ini'):
            self.setup_config(cfgparser)
        cfgparser.read('skycat.ini')
        self.skyrim = cfgparser['PATHS']['sPathSSE']
        self.cache = cfgparser['PATHS']['sPathCache']
        self.backups = cfgparser['PATHS']['sPathBackups']

    def write_to_config(self, section, key, value, cfgparser=parser):
        if not os.path.exists('skycat.ini'):
            self.setup_config(cfgparser)
            self.load_config(cfgparser)
            
        cfgparser[section][key] = value

        with open('skycat.ini', 'w') as configfile:
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
        raise RuntimeError("Global config not set. Call bootstrap() before using config.")
    return cfg