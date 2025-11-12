import os

# constants
animdata = "meshes\\animationdatasinglefile.txt"
animsetdata = "meshes\\animationsetdatasinglefile.txt"


class Configurator:
    
    skyrim = 'C:\\Steam\\steamapps\\common\\Skyrim Special Edition\\Data'
    cache = os.path.expanduser('~') + '\\AppData\\Local\\SkyCAT-SE\\cache\\'

    def setup_config(self, cfgparser):        
        cfgparser['PATHS'] = {'sPathSSE': 'C:\\Steam\\steamapps\\common\\Skyrim Special Edition\\Data',
                          'sPathCache': os.path.expanduser('~') + '\\AppData\\Local\\SkyCAT-SE\\cache\\'}
        with open('skycat.ini', 'w') as configfile:
            cfgparser.write(configfile)

        
    def load_config(self, cfgparser):
        if not os.path.exists('skycat.ini'):
            self.setup_config(cfgparser)
        cfgparser.read('skycat.ini')
        self.skyrim = cfgparser['PATHS']['sPathSSE']
        self.cache = cfgparser['PATHS']['sPathCache']

    def write_to_config(self, cfgparser, section, key, input):
        cfgparser[section][key] = input
        with open('skycat.ini', 'w') as configfile:
            cfgparser.write(configfile)
        self.load_config(cfgparser)