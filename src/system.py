import os
import os.path
import shutil
from pathlib import Path

import update
import config, util

def save_backup(prefix="backup_"):
    cfg = config.require_config()
    
    if not os.path.exists(cfg.backups):
        os.makedirs(cfg.backups)

    animdata_src = cfg.skyrim / config.animdata
    animsetdata_src = cfg.skyrim / config.animsetdata
    
    if not os.path.exists(animdata_src) or not os.path.exists(animsetdata_src):
        print("Error: cannot backup cache, files missing.")
        return
    
    # create backup directory if we need to
    if not os.path.exists(cfg.backups):
        os.makedirs(cfg.backups)

    animdata_dst = cfg.backups / "animationdatasinglefile.txt"
    animsetdata_dst = cfg.backups / "animationsetdatasinglefile.txt"

    # user consent to overwrite
    if os.path.exists(animdata_dst) or os.path.exists(animsetdata_dst):
        print("Existing backup found. Overwrite? Y/N")
        while True:
            match input().lower():
                case 'y':
                    break
                case 'n':
                    print("Cancelling backup.")
                    return 0

    print("Creating backup...")
    copy_backups(animdata_src, animsetdata_src, animdata_dst, animsetdata_dst)

def load_backup():
    cfg = config.require_config()
    ud = update.require_update()

    backups_path = Path(cfg.backups)

    # make sure the backups directory exists and is a folder, and contains files
    if not os.path.exists(backups_path) or not backups_path.is_dir() or not any(backups_path.iterdir()):
        print("Warning: No backups found.")
        return 0
    
    # make sure we have a meshes folder to copy to
    if not os.path.exists(cfg.skyrim / "meshes"):
        os.makedirs(cfg.skyrim / "meshes")

    animdata_src = cfg.backups / "animationdatasinglefile.txt"
    animsetdata_src = cfg.backups / "animationsetdatasinglefile.txt"
    # make sure the backup files exist
    if not os.path.exists(animdata_src) or not os.path.exists(animsetdata_src):
        print("Error: Backup files missing.")
        return

    animdata_dst = cfg.skyrim / "meshes" / "animationdatasinglefile.txt"
    animsetdata_dst = cfg.skyrim / "meshes" / "animationsetdatasinglefile.txt"

    # user consent to overwrite
    if os.path.exists(animdata_dst) or os.path.exists(animsetdata_dst):
        print("This will overwrite your current animation cache. Is this okay? Y/N")
        while True:
            match input().lower():
                case 'y':
                    break
                case 'n':
                    print("Cancelling restore.")
                    return 0
    
    print("Restoring backup...")
    copy_backups(animdata_src, animsetdata_src, animdata_dst, animsetdata_dst)
    ud.update_all()

def copy_backups(animdata_src, animsetdata_src, animdata_dst, animsetdata_dst):
    try:
        # make sure the destination directories exist
        if not os.path.exists(os.path.dirname(animdata_dst)):
            os.makedirs(os.path.dirname(animdata_dst))
        if not os.path.exists(os.path.dirname(animsetdata_dst)):
            os.makedirs(os.path.dirname(animsetdata_dst))

        # create temporary backups of existing files
        if os.path.exists(animdata_dst):
            bak_path = Path(str(animdata_dst) + ".bak")
            old_animdata = Path(shutil.copy2(animdata_dst, bak_path))

        if os.path.exists(animsetdata_dst):
            bak_path = Path(str(animsetdata_dst) + ".bak")
            old_animsetdata = Path(shutil.copy2(animsetdata_dst, bak_path))
        
        try:
            # copy the cache files to the backup folder
            shutil.copy2(animdata_src, animdata_dst)
            shutil.copy2(animsetdata_src, animsetdata_dst)
        except Exception:
            print("Failed to create backup. Restoring previous backup.")
            # restore old backups
            if old_animdata is not None and old_animdata.exists():
                shutil.move(str(old_animdata), animdata_dst)
            if old_animsetdata is not None and old_animsetdata.exists():
                shutil.move(str(old_animsetdata), animsetdata_dst)
            return
        
        finally:
            # clean up any temp files
            if old_animdata is not None and old_animdata.exists():
                os.remove(str(old_animdata))
            if old_animsetdata is not None and old_animsetdata.exists():
                os.remove(str(old_animsetdata))

        print("Backup successful.")
        return 0

    except Exception:
        print("Failed to create temporary backup. Aborting.")

        old_animdata = Path(str(animdata_dst) + ".bak")
        old_animsetdata = Path(str(animsetdata_dst) + ".bak")

        # clean up any partial temp files
        if old_animdata is not None and old_animdata.exists():
            os.remove(str(old_animdata))
        if old_animsetdata is not None and old_animsetdata.exists():
            os.remove(str(old_animsetdata))
        return

def restore_vanilla_cache():
    ud = update.require_update()
    
    while True:
        print("Note: This will overwrite your current animation cache with the vanilla cache. Continue? Y/N")
        match input().lower():
            case 'y':
                    util.unpack_vanilla_cache()
                    ud.update_all()
                    print("Vanilla cache restored.")
                    return
            case 'n':
                print("Cancelled.")
                return
            
def clean_temp():
    cfg = config.require_config()
    temp_path = cfg.cache / "temp"
    if os.path.exists(temp_path):
        for root, dirs, files in os.walk(temp_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_path)
    else:
        return None
    return 0