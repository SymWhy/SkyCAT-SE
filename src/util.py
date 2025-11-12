import os
from pathlib import Path
import tkinter.filedialog as filedialog

import sse_bsa

def sanitize_cache(cfg, cfgparser):

    # make sure all our resource files are available
    if (not os.path.exists("src\\resources\\vanilla_projects.txt")):
        print("Error: Source files corrupt! You may need to reinstall SkyCAT SE.")
        os.system('pause')
        return

    # prompt the user to navigate to the Skyrim SE directory
    if not os.path.exists(cfg.skyrim):
        new_path = filedialog.askdirectory(title="Select Skyrim SE Data folder.", mustexist=True)
        cfg.write_to_config(cfgparser, 'PATHS', 'sPathSSE', new_path)

    # make sure the animation cache is unpacked from the bsa.
    if not os.path.exists(cfg.skyrim + "\\meshes\\animationdatasinglefile.txt") or not os.path.exists(cfg.skyrim + "\\meshes\\animationdatasinglefile.txt"):
        
        # if we are missing the animations bsa entirely, abort.
        if not os.path.exists(cfg.skyrim + "\\Skyrim - Animations.bsa"):
            print("Error: could not find Skyrim - Animations.bsa. Please verify integrity of game files.")
            os.system('pause')
            return


        to_next = False
        while to_next == False:
            print("Animation cache appears to be missing. Unpack? Y/N")
            response = input().lower()
            match response:
                case 'y':
                    # unpack the necessary files
                    anims_archive = sse_bsa.BSAArchive(Path(cfg.skyrim + "\\skyrim - animations.bsa"))
                    anims_archive.extract_file("meshes\\animationdatasinglefile.txt", Path(cfg.skyrim))
                    anims_archive.extract_file("meshes\\animationsetdatasinglefile.txt", Path(cfg.skyrim))
                    to_next = True
                    
                case 'n':
                    print("Warning: SkyCAT SE cannot operate without a valid cache.")
                    os.system('pause')
                    return
    if not os.path.exists(cfg.cache):
        os.makedirs(cfg.cache)

    return True