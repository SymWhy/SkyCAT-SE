Note: Updated python version "SkyCAT-SE" in progress. The old version of CCAT is still available on the main for educational purposes, but does not work properly, hence the rebuilding.

# Creature Cache Assembly Tool for Skyrim SE
Small Java app to patch custom havok creature projects.

## What is CCAT?

The Creature Cache Assembly Tool is a program that packs loose animation cache files into files readable by Skyrim SE. CCAT can be run directly from Mod Organizer.

CCAT was created as a way to simplify the patching process for having multiple custom creatures mods at once. Skyrim's animation cache consists of two very long txt files containing root motion and annotations that is necessary to make the animations, sounds, attacks, etc play correctly. One of the issues with creating custom Havok projects is that each mod will have its own verson of these files, overwriting each other so only the most recent cache is read. This prevents the animation cache data for any other custom Havok creature from being read, and will break those overwritten projects.

CCAT remedies this by building a new cache from the base game cache files, and appending the animation data from any other project it finds, so all animation data is readable by the game.

## How to use it

Install anywhere and run through Mod Organizer 2.

### MO2 Executable Setup
**Title:** CCAT  
**Binary:** D:\...path to ccat..\CCAT\CCAT.bat  
**Start in:** D:\Steam\steamapps\common\Skyrim Special Edition\Data  
**Arguments:**  

### Expected file structure  
(Case insensitive)

AnimationData/  
|__ [YourCreature]Project.txt  
|__ BoundAnims/  
|&emsp;&emsp;|__ Anims_[YourCreature]Project.txt  
  
AnimationSetData/  
|__ [YourCreature]ProjectData/  
|&emsp;&emsp;|__ [YourCreature]Project.txt <- contains a list of cache files, not read by the program  
|&emsp;&emsp;|__ FullCreature.txt <- As many as you need, name it whatever you want.  
