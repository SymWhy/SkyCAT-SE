import logging
import sys
import argparse
from pathlib import Path

import config, cache, errors, system, update, util

from CRC32 import CRC32

import extract, append


def build_parser():
  
  parser = argparse.ArgumentParser()

  parser.add_argument("-update",
                      action='store_true',
                      help="Sync the program with your existing animation cache.")

  parser.add_argument("-extract",
                      nargs='+',
                      help='extract one or more projects from the animation cache.\n'
                      'For example: "-extract catproject snakeproject"')

  parser.add_argument("-extractall",
                      action='store_true',
                      help='extract all non-vanilla projects from the animation cache.\n'
                      'Use "-ireallymeanit" to also extract vanilla projects.\n'
                      '(Use at your own risk.)')
  parser.add_argument("-ireallymeanit",
                      action='store_true')

  parser.add_argument("-append",
                      nargs='+',
                      help='Append one or more projects to the animation cache.\n'
                      'For example: "-append catproject snakeproject"')
  
  parser.add_argument("-appendall",
                      action='store_true',
                      help='Append all available modded projects to the animation cache.')

  parser.add_argument("-backup",
                      help="Create a backup of the current animation cache.",
                      action='store_true')
  
  parser.add_argument("-restore",
                      help="Restore the animation cache from the latest backup.",
                      action='store_true')
  
  parser.add_argument("-restorefromarchive",
                      help="Restore the vanilla animation cache from the program archive.",
                      action='store_true')
  
  parser.add_argument("-crc32",
                      help="Calculate the CRC32 checksum of a given string.",
                      action='store',
                      metavar='STRING')
  
  parser.add_argument("-getchecksum",
                        help="Calculate the CRC32 checksum of a given animation file.",
                        action='store',
                        nargs='?',
                        const='',
                        default=None,
                        metavar='PATH')
  
  parser.add_argument("-gui",
                      help="Launch the full program.",
                      action='store_true')
  
  # addon commands
  parser.add_argument("-cd",
                      help="Change the data directory.",
                      action='store',
                      nargs='?',
                      const='',
                      default=None,
                      metavar='PATH')
  
  # debug helpers
  parser.add_argument("-yesimsure",
                      action='store_true',
                        help="Automatically skip confirmation prompts. Not recommended!")
  
  parser.add_argument("-noupdate",
                      action='store_true',
                      help="Skip updating the program. Note: This might break stuff, only use if you know what you're doing.")
  
  parser.add_argument("-level",
                      nargs='?',
                      help="Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR).",
                      action='store',
                      default="INFO")
  
  parser.add_argument("-dryrun",
                      action='store_true',
                      help="Run the program in dry run mode, where no actual changes are made to files.")
  return parser

def has_cli_actions(parsed_args) -> bool:
    # check if any meaningful command-line arguments were provided.
    # only consider arguments that trigger actions
    return any([
        getattr(parsed_args, 'cd', None) is not None,
        parsed_args.update,
        parsed_args.extract,
        parsed_args.extractall,
        parsed_args.append,
        parsed_args.appendall,
        parsed_args.gui,
        parsed_args.backup,
        parsed_args.restore,
        parsed_args.restorefromarchive,
        parsed_args.crc32,
        parsed_args.getchecksum
    ])


def process_cli(args):
    ud = config.get_global('update')
    # Run actions requested via command-line arguments and exit.

    # Set logging level
    system.set_log_level(args.level)

    # Check if we want to change our data directory
    if args.cd is not None:
        if args.cd == "":
            # user passed "-cd" with no path -> open interactive chooser
            config.change_data_dir()
        else:
            # user passed "-cd <path>"
            config.change_data_dir(Path(args.cd))

    # process gui first, even if other actions are requested
    if args.gui:
        # its not really a gui yet but i'll get there
        interactive_loop()
        return 0
    # Auto-update unless noupdate is specified
    if not args.noupdate:
        ud.update_cache()

    if args.backup:
        system.save_backup()

    if args.restorefromarchive:
        cache.restore_vanilla_cache()

    if args.restore:
        system.load_backup()

    if args.update:
        ud.update_cache()

    if args.extract:
        # extract may be a list of project names
        extract.extract_projects(listprojects=args.extract)

    if args.extractall:
        if args.ireallymeanit:
            extract.extract_all(and_i_mean_all_of_them=True)
        else:
            extract.extract_all()

    if args.append:
        append.append_projects(project_list=args.append)
        pass

    if args.appendall:
        append.append_all_available()

    if args.crc32:
        my_crc32 = CRC32()
        checksum = my_crc32.convert(data=args.crc32)
        print(checksum)

    if args.getchecksum:
        util.get_file_crc32(Path(args.getchecksum))

    return 0

# only runs this when you open the application
# commands can also be accessed from the command line
def interactive_loop(args=None):

    ud = config.get_global('update')

    while True:
        print("Entering interactive mode. Type 'help' for a list of commands.")
        inp = input('> ').strip().lower()
        match inp:
            case "help":
                print("Available commands:\n",
                      "  update                 - Update the program to the current cache.\n",
                      "  changedir | cd         - Change the data directory read by the program.\n",
                      "  extract [projects]     - Extract one or more projects from the animation cache.\n",
                      "  extractall             - Extract all non-vanilla projects from the animation cache.\n",
                      "  append [projects]      - Append one or more projects to the animation cache.\n",
                      "  appendall              - Append all available projects to the animation cache.\n",
                      "  backup                 - Create a backup of the current animation cache.\n",
                      "  restore                - Restore the animation cache from the latest backup.\n",
                      "  restorefromarchive     - Restore the vanilla animation cache from the program archive.\n",
                      "  CRC32 [string]         - Calculate the CRC32 checksum of a given string.\n",
                      "  getchecksum [file]     - Calculate the CRC32 checksum of a given animation file.\n",
                      "  dumpjson               - Dump the current animation cache data to a JSON file.\n",
                      "  level [LEVEL]          - Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR).\n",)

            case "update":
                ud.update_cache()

            case _ if inp.startswith("extract "):
                try:
                    logging.info("Extracting projects...")
                    project_list = inp.split(" ", 1)[1].split(" ")
                    extract.extract_projects(listprojects=project_list)
                except Exception:
                    logging.exception(f"Extraction cancelled.")

            case "extractall":
                try:
                    if args and args.ireallymeanit:
                        logging.info("Extracting all projects, including vanilla...")
                        extract.extract_all(and_i_mean_all_of_them=True)
                    else:
                        logging.info("Extracting all non-vanilla projects...")
                        extract.extract_all()
                except Exception:
                    logging.exception(f"Extraction cancelled.")

            case _ if inp.startswith("append "):
                try:
                    logging.info("Appending projects...")
                    project = inp.split(" ", 1)[1].split(" ") 
                    append.append_projects(project_list=project)
                except Exception:
                    logging.exception(f"Append cancelled.")

            case "appendall":
                try:
                    logging.info("Appending all available projects...")
                    append.append_all_available()
                except Exception:
                    logging.exception(f"Append cancelled.")

            case "backup":
                try:
                    logging.info("Creating cache backup...")
                    system.save_backup()
                except Exception:
                    logging.exception(f"Failed to backup cache.")

            case "restore":
                try:
                    logging.info("Restoring cache backup...")
                    system.load_backup()
                except Exception:
                    logging.exception(f"Failed to restore saved cache.")

            case "restorefromarchive":
                try:
                    logging.info("Restoring vanilla cache from archive...")
                    cache.restore_vanilla_cache()
                except Exception:
                    logging.exception(f"Failed to restore vanilla cache.")

            case _ if inp.startswith("level "):
                try:
                    level = inp.split(" ", 1)[1].upper()
                    system.set_log_level(level)
                    logging.info(f"Log level set to {level}.")
                except Exception:
                    logging.exception(f"Failed to set log level.")

            case _ if inp.startswith("crc32 "):
                try:
                    string = inp.split(" ", 1)[1]
                    my_crc = CRC32()
                    checksum = my_crc.convert(data=string)
                    print(f"CRC32 Checksum of '{string}': {checksum}")
                except Exception:
                    logging.exception(f"Failed to compute CRC32.")

            case _ if inp.startswith("getchecksum"):
                try:
                    parts = inp.split(" ", 1)
                    if len(parts) > 1:
                        path = Path(parts[1])
                    else:
                        path = None
                    util.get_file_crc32(path)
                except Exception:
                    logging.exception(f"Failed to compute file CRC32.")

            case "dumpjson" | "dumpjason":
                try:
                    logging.info("Dumping cache to JSON...")
                    cfg = config.get_global('config')
                    cache.dump_cache()
                except Exception:
                    logging.exception(f"Failed to dump cache to JSON.")

            case "changedir" | "cd":
                try:
                    logging.info("Changing data directory...")
                    if inp.startswith("changedir ") or inp.startswith("cd "):
                        path = inp.split(" ", 1)[1]
                        config.change_data_dir(Path(path))
                    else:
                        config.change_data_dir()
                except Exception:
                    logging.exception(f"Failed to change data directory.")

            case "quit":
                return 0

def main(argv=None): 
    
    # detect whether the user invoked the program with command-line flags
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    dryrun = bool(getattr(args, 'dryrun', False))
    yes_im_sure = bool(getattr(args, 'yesimsure', False))

    system.set_log_level()

    if not config.set_globals(config.Configurator(), update.Updater(), dryrun=dryrun, yes_im_sure=yes_im_sure) == 0:
        raise errors.ConfigError()
    
    # make sure the cache is valid
    if not cache.sanitize_cache():
        raise errors.CacheError(message="Failed to sanitize cache.")

    force_update = True

    # check for command-line args
    if has_cli_actions(args):
        process_cli(args)
        if not args.gui:
            return 0
        if args.noupdate:
            force_update = False

    if force_update:
        # auto-update on launch
        ud = config.get_global('update')
        ud.update_cache()
    
    # no command-line args, or args.gui = True, run interactive loop
    interactive_loop()
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        # allow user to cancel without a traceback
        raise
    except errors.UserAbort as e:
        print(f"Setup cancelled, no changes were made.")
        raise SystemExit(0)
    except Exception:
        # Print full traceback so the user can see what went wrong
        import traceback

        traceback.print_exc()
        # Pause so double-click users can read the error
        try:
            input("\nPress Enter to exit...")
        except Exception:
            # ignore any issues with input
            pass
        raise