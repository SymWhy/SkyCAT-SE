import os

# constants
animdata = "\\meshes\\animationdatasinglefile.txt"
animsetdata = "\\meshes\\animationsetdatasinglefile.txt"

animdata_dir = "\\meshes\\animationdata\\"
animsetdata_dir = "\\meshes\\animationsetdata\\"

animdata_csv_path = "\\animdata_cache.csv"
animsetdata_csv_path = "\\animsetdata_cache.csv"


class Configurator:
    # configurables
    skyrim = 'C:\\Steam\\steamapps\\common\\Skyrim Special Edition\\Data'
    cache = os.path.expanduser('~') + '\\AppData\\Local\\SkyCAT-SE\\cache\\'
    backups = '\\backups'

    def setup_config(self, cfgparser):        
        cfgparser['PATHS'] = {'sPathSSE': 'C:\\Steam\\steamapps\\common\\Skyrim Special Edition\\Data',
                          'sPathCache': os.path.expanduser('~') + '\\AppData\\Local\\SkyCAT-SE\\cache\\',
                          'sPathBackups': os.path.expanduser('~') + '\\backups'}
        with open('skycat.ini', 'w') as configfile:
            cfgparser.write(configfile)

        
    def load_config(self, cfgparser):
        if not os.path.exists('skycat.ini'):
            self.setup_config(cfgparser)
        cfgparser.read('skycat.ini')
        self.skyrim = cfgparser['PATHS']['sPathSSE']
        self.cache = cfgparser['PATHS']['sPathCache']
        self.backups = cfgparser['PATHS']['sPathBackups']

    def write_to_config(self, cfgparser, section, key, input):
        cfgparser[section][key] = input
        with open('skycat.ini', 'w') as configfile:
            cfgparser.write(configfile)
        self.load_config(cfgparser)