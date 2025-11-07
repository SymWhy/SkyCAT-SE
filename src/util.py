import os
from shutil import copyfile
import sys

def sanitize_cache():

    # make sure all our resource files are available
    if (not os.path.exists("skycat\\src\\resources\\animationdatasinglefile.txt") 
        or not os.path.exists("skycat\\src\\resources\\animationsetdatasinglefile.txt")
        or not os.path.exists("skycat\\src\\resources\\dirlist.txt")):
        print("Error: Source files corrupt! You may need to reinstall.")

    if not os.path.exists("meshes"):
        print("Warning: Can't find meshes/ folder. Press any key to exit.")
        os.system('pause')
        sys.exit()

    # make sure our actual animation cache exists
    if not os.path.exists("meshes\\animationdatasinglefile.txt"):
        to_next = False
        while to_next == False:
            print('You are missing your "animationdatasinglefile.txt" file. Replace with default? Y/N')
            response = input().lower()
            match response:
                case 'y':
                    copyfile("skycat\\src\\resources\\animationdatasinglefile.txt", "meshes\\animationdatasinglefile.txt")
                    to_next = True
                case 'n':
                    print("Warning: SkyCAT cannot operate without the animation cache files. Press any key to exit.")
                    os.system('pause')
                    sys.exit()
        

    if not os.path.exists("meshes\\animationsetdatasinglefile.txt"):
        to_next = False
        while to_next == False:
            print('You are missing your "animationsetdatasinglefile.txt" file. Replace with default? Y/N')
            response = input().lower()
            match response:
                case 'y':
                    copyfile("skycat\\src\\resources\\animationsetdatasinglefile.txt", "meshes\\animationsetdatasinglefile.txt")
                    to_next = True
                case 'n':
                    print("Warning: SkyCAT cannot operate without the animation cache files. Press any key to exit.")
                    os.system('pause')
                    sys.exit()
        

    # check if we need to update the program cache
    if not os.path.exists("skycat\\cache\\animdata_index.csv"):
        return "animdata"
    
    elif not os.path.exists("skycat\\cache\\animdata_index.csv"):
        return "animsetdata"
    
    else: return None