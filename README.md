# SkyCAT SE - Skyrim SE Cache Assembly Tool 0.0.1a
Small app to patch custom Havok creature projects.

## Currently in pre-alpha
All available commands work in-game currently, with some limitations (see Limitations).

## What is SkyCAT?

The Skyrim SE Cache Assembly Tool is a program meant to read and modify the Havok animation cache in Skyrim SE.

SkyCAT SE was created as a way to simplify the patching process for having multiple custom creature mods at once. Skyrim's animation cache consists of two very long txt files containing root motion and annotations that are necessary to make the animations, sounds, attacks, etc play correctly. One of the issues with creating custom Havok projects is that each mod will have its own version of these files, overwriting each other so only the most recent cache is read. This prevents the animation cache data for any other custom Havok creature from being read, and will break those overwritten projects.

SkyCAT remedies this by building a new cache from the base game cache files, and appending the animation data from any other project it finds, so all animation data is readable by the game.

## Patching Conflicting Mods
Copy the first mod's `animationdatasinglefile.txt` and `animationsetdatasinglefile.txt`into a clean `Data/meshes` folder.\
Run `skycat extractall` to extract all modded projects.\
Copy the second mod's `animationdatasinglefile.txt` and `animationsetdatasinglefile.txt` into Data/meshes. Overwrite if prompted.\
Run `skycat extractall`.\
Repeat for all mods you wish to patch.
Your `Data/meshes` folder should now contain an `animationdata/` folder and an `animationsetdata/` folder.\
Delete the `animationdatasinglefile.txt` and `animationsetdatasinglefile.txt` from `Data/meshes`.\
Run SkyCAT. You should be prompted to unpack the cache files. If not, run `skycat unpackfromarchive`. Overwrite if prompted.\
Your cache is now back to vanilla state.\
Run `skycat appendall` to merge the extracted files with the vanilla cache.\
You should now have two merged singlefiles in your cache. Move them to a new mod folder. Delete `animationdata/` and `animationsetdata/`.
Enable the new mod in MO and run the game.

## Appending New Projects
[Follow this guide to custom creature implementation up to step 5.](https://wiki.beyondskyrim.org/wiki/Arcane_University:Implementation_of_Custom_Animations#Custom_animated_creature_implementation)\
Delete the resulting `animationdata\`, `animationsetdata\`, `animationdatasinglefile.txt`, and `animationsetdatasinglefile.txt`.\
Run `skycat extract [donorproject]` with the same donor project you used for your custom creature.\
Make sure you have a new `animationdata\` and `animationsetdata\` in your Data folder. Change all instances of the vanilla creature's name to the name of your new creature. You must use the same project name for all the files.\

### Expected file structure
>(Case insensitive)\
>Data/\
>|__ Meshes/\
>&emsp;|__ AnimationData/\
>&emsp;&emsp;|__ [YourCreature]Project.txt\
>&emsp;&emsp;|__ BoundAnims/\
>&emsp;&emsp;&emsp;|__ Anims_[YourCreature]Project.txt\
>\
>&emsp;|__ AnimationSetData/ \
>&emsp;&emsp;|__ [YourCreature]ProjectData/ \
>&emsp;&emsp;&emsp;|__ [YourCreature]Project.txt <- contains a list of cache files.\
>&emsp;&emsp;&emsp;|__ FullCreature.txt <- As many as you need, name it whatever you want.\
>\
>|__ Skyrim - Animations.bsa\

Also go into `animationdata\yourcreatureproject.txt` and change the file paths to your creature's behavior and character hkx files.\
Double check the paths in your plugin, and make sure they match up to your new hkx names.\
Run `skycat append [yourproject]` with your project name.\
Your new creature should now animate properly.

## Installation
Extract the contents of the build folder to your modding tools directory.

## Installation (The hard way)
### Requires
Python: >=3.10

### How to install
Run: `python -m pip install -r requirements.txt` (include `sse_bsa`, `lz4`, `virtual_glob`)

### Running from CLI
Run: `python -m src.__main__ -(arguments)`

### Building from source
Use: `python -m PyInstaller`

Example build string:\
`pyinstaller --name "skycat-se" ^`\
  `--onedir ^`\
  `--console ^`\
  `--icon=resources\\icon\\dovahcat.ico ^`\
  `--paths=src^`\
  `--add-data "resources;resources"` ^\
  `src\\__main\__.py`

## Commands

| Argument | CLI Argument | Description | Example |
|-------------|-----------|--------------|----------|
| update | `-update` | Updates SkyCAT SE to your current cache. Runs automatically. | `skycat -update` |
| changedir | `-changedir` | Changes the working Data directory. Path optional.| `skycat -changedir "C:\...path to Skyrim Special Edition\Data\meshes"` |
| extract | `-extract` | Extract one or more projects by name from the cache. Add `-remove` to delete from the cache after unpacking. | `skycat -extract catproject` |
| extractall | `-extractall` | Extract all non-vanilla projects. Add `-ireallymeanit` to include vanilla ones (not recommended). | `skycat -extractall` |
| append (project) | `-append` | Append one or more loose projects into the cache. | `skycat -append catproject` |
| backup | `-backup` | Back up your current cache files. | `skycat -backup` |
| restore | `-restore` | Restore your cache files from backup. | `skycat -restore` |
| restorefromarchive | `-restorefromarchive` | Revert cache files to vanilla. | `skycat -restorefromarchive` |
| help | `-help` | Lists all commands and their descriptions. | `skycat -help` |

## Limitations:
* SkyCAT may overwrite your cache files and individual files. Always run `skycat -backup` before modifying your cache.
* Each project must have a unique name.
* Backup function is still very WIP, only one slot is available right now.
* SkyCAT performs some basic checks to make sure your cache is in the expected format. It is still possible for a broken cache to pass if it fits that format. Please make sure your singlefile cache is up-to-date and working before running this program.
* The loose cache files that ship with the game are outdated and may be incorrect. I strongly recommend you not use them for custom creatures. Instead copy the projects from the singlefiles directly, either by hand or with this program.
* Currently SkyCAT is cmd based and can't be run through Mod Organizer.
* Windows only at this time.
