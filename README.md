# SkyCAT SE - Skyrim SE Cache Assembly Tool 0.1.0a
Small app to patch custom Havok creature projects.

## Currently in pre-alpha
All commands work in-game currently, with some limitations (see Limitations).

## What is SkyCAT?

The Skyrim SE Cache Assembly Tool started as a program that packs loose hkx project files into files readable by Skyrim SE. Now it can also extract full projects from the cache, help validate singlefiles before use, and restore singlefiles directly from the BSA.

SkyCAT SE was created as a way to simplify the patching process for having multiple custom creature mods at once. Skyrim's animation cache consists of two very long txt files containing root motion and annotations that are necessary to make the animations, sounds, attacks, etc play correctly. One of the issues with creating custom Havok projects is that each mod will have its own version of these files, overwriting each other so only the most recent cache is read. This prevents the animation cache data for any other custom Havok creature from being read, and will break those overwritten projects.

SkyCAT remedies this by building a new cache from the base game cache files, and appending the animation data from any other project it finds, so all animation data is readable by the game.

### Commands

| Argument | CLI Argument | Description | Example |
|-------------|-----------|--------------|----------|
| update | `-update` | Updates SkyCAT SE to your current cache. Runs automatically. | `skycat -update -m "C:\...path to Skyrim Special Edition\Data\meshes"` |
| extract | `-extract` | Extractone or more projects by name from the cache. Add `-remove` to delete from the cache after unpacking. | `skycat -extract catproject` |
| extractall | `-extractall` | Extract all non-vanilla projects. Add `-ireallymeanit` to include vanilla ones (not recommended). | `skycat -extractall` |
| append (project) | `-append` | Append one or more loose projects into the cache. | `skycat -append catproject` |
| backup | `-backup` | Back up your current cache files. | `skycat -backup' |
| restore | `-restore` | Restore your cache files from backup. | `skycat -restore |
| restorefromarchive | `-restorefromarchive` | Revert cache files to vanilla. Use flags `-animationdata` and/or `-animationsetdata`. | `skycat -restorefromarchive` |
| help | `-help` | Lists all commands and their descriptions. | `skycat -help` |

## Limitations:
* SkyCAT may overwrite your cache files and individual files. Always make a backup before running the program.
* Backup function is still very WIP, only one slot is available right now.
* Each project must have a unique name.
* SkyCAT performs some basic checks to make sure your cache is in the expected format. It is still possible for a broken cache to pass if it fits that format. Please make sure your singlefile cache is up-to-date and working before running this program.
* The loose cache files that ship with the game are outdated and may be incorrect. I strongly recommend you not use them for custom creatures. Instead copy the projects from the singlefiles directly, either by hand or with this program.

## Planned Functions
* Better backup/restore
* Better cache validation
* Project editing

## How to use it - Command Line
Install anywhere.\
`cd (skycat directory)`\
`skycat (command)`

Note that the program cache will be automatically updated each time it's run, and each time SkyCAT changes the cache singlefiles.

## How to use it - Mod Organizer 2

Install and run through Mod Organizer 2.

### MO2 Executable Setup
**Title:** SkyCAT SE  
**Binary:** D:\...path to skycat..\SkyCatSE\skycat.exe
**Start in:** 
**Arguments:**  (list the arguments you wish to run. Alternatively, SkyCAT can be run without arguments and interacted with like a normal program.

### Expected file structure  
(Case insensitive)\
\
Data/\
|__ Meshes/\
&emsp;|__ AnimationData/\
&emsp;&emsp;|__ [YourCreature]Project.txt\
&emsp;&emsp;|__ BoundAnims/\
&emsp;&emsp;&emsp;|__ Anims_[YourCreature]Project.txt\
\
&emsp;|__ AnimationSetData/ \
&emsp;&emsp;|__ [YourCreature]ProjectData/ \
&emsp;&emsp;&emsp;|__ [YourCreature]Project.txt <- contains a list of cache files.\
&emsp;&emsp;&emsp;|__ FullCreature.txt <- As many as you need, name it whatever you want.\
\
|__ Skyrim - Animations.bsa
