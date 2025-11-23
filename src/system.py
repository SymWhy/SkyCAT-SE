import os
import shutil
from pathlib import Path
import logging

import config, errors, util

def save_backup(yes_im_sure: bool = False, prefix="backup_"):
    cfg = config.get_global('config')
    
    try:
        os.makedirs(cfg.backups, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise errors.WriteError(path=str(cfg.backups), message=f"Could not create backups directory: {e}") from e

    animdata_src = cfg.skyrim / 'meshes' / config.animdata
    animsetdata_src = cfg.skyrim / 'meshes' / config.animsetdata

    if not animdata_src.exists() or not animsetdata_src.exists():
        raise FileNotFoundError(f"Cannot backup cache, files missing.")

    animdata_dst = cfg.backups / "animationdatasinglefile.txt"
    animsetdata_dst = cfg.backups / "animationsetdatasinglefile.txt"

    # user consent to overwrite
    if (animdata_dst.exists() or animsetdata_dst.exists()) and not yes_im_sure:
        if not util.prompt_yes_no("Existing backup found. Overwrite?",
                                   message_y="Overwriting existing backup.",
                                   message_n="Cancelling backup."):
            return 0

    logging.info("Creating backup...")
    copy_backups(animdata_src, animsetdata_src, animdata_dst, animsetdata_dst)

def load_backup(yes_im_sure: bool = False):
    cfg = config.get_global('config')
    ud = config.get_global('update')

    backups_path = Path(cfg.backups)

    # make sure the backups directory exists and is a folder, and contains files
    if not backups_path.exists() or not backups_path.is_dir() or not any(backups_path.iterdir()):
        logging.warning("Warning: No backups found.")
        return 0
    
    # make sure we have a meshes folder to copy to
    if not (cfg.skyrim / "meshes").exists():
        os.makedirs(cfg.skyrim / "meshes")

    animdata_src = cfg.backups / "animationdatasinglefile.txt"
    animsetdata_src = cfg.backups / "animationsetdatasinglefile.txt"
    # make sure the backup files exist
    if not animdata_src.exists() or not animsetdata_src.exists():
        raise FileNotFoundError("Backup files missing.")

    animdata_dst = cfg.skyrim / "meshes" / "animationdatasinglefile.txt"
    animsetdata_dst = cfg.skyrim / "meshes" / "animationsetdatasinglefile.txt"

    # user consent to overwrite
    if (animdata_dst.exists() or animsetdata_dst.exists()) and not yes_im_sure:
        if not util.prompt_yes_no("Existing cache files found. Overwrite with backup?",
                                   message_y="Overwriting existing cache files.",
                                   message_n="Cancelling restore."):
            return 0

    logging.info("Restoring backup...")
    copy_backups(animdata_src, animsetdata_src, animdata_dst, animsetdata_dst)
    ud.update_cache()

def copy_backups(animdata_src:Path, animsetdata_src: Path, animdata_dst: Path, animsetdata_dst: Path):
    try:
        # make sure the destination directories exist
        os.makedirs(animdata_dst.parent, exist_ok=True)
        os.makedirs(animsetdata_dst.parent, exist_ok=True)

        # initialize temp variables for backup files
        old_animdata = None
        old_animsetdata = None

        # create temporary backups of existing files
        if animdata_dst.exists():
            bak_path = Path(str(animdata_dst) + ".bak")
            old_animdata = Path(shutil.copy2(animdata_dst, bak_path))

        if animsetdata_dst.exists():
            bak_path = Path(str(animsetdata_dst) + ".bak")
            old_animsetdata = Path(shutil.copy2(animsetdata_dst, bak_path))
        
        try:
            # copy the cache files to the backup folder
            shutil.copy2(animdata_src, animdata_dst)
            shutil.copy2(animsetdata_src, animsetdata_dst)
        except (OSError, PermissionError):
            # restore old backups
            if old_animdata is not None and old_animdata.exists():
                shutil.move(str(old_animdata), animdata_dst)
            if old_animsetdata is not None and old_animsetdata.exists():
                shutil.move(str(old_animsetdata), animsetdata_dst)
            raise OSError("Failed to backup files. Restoring previous backup.")
        
        finally:
            # clean up any temp files
                if old_animdata is not None and old_animdata.exists():
                    os.remove(str(old_animdata))
                if old_animsetdata is not None and old_animsetdata.exists():
                    os.remove(str(old_animsetdata))

        logging.info("Backup successful.")
        return 0

    except (OSError, PermissionError) as e:
        # attempt to clean up any partial temp backup files
        old_animdata = Path(str(animdata_dst) + ".bak")
        old_animsetdata = Path(str(animsetdata_dst) + ".bak")

        if old_animdata is not None and old_animdata.exists():
            os.remove(str(old_animdata))
        if old_animsetdata is not None and old_animsetdata.exists():
            os.remove(str(old_animsetdata))

        raise OSError(f"Failed to create temporary backup: {e}") from e

           
def clean_temp():
    cfg = config.get_global('config')
    temp_path = cfg.cache / "temp"
    if temp_path.exists():
        for root, dirs, files in os.walk(temp_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(str(temp_path))
    else:
        logging.info("No temporary files to clean.")
    return 0

def set_log_level(level: str = "INFO"):
    logging.getLogger().setLevel(level)
    return 0