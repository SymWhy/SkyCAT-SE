import logging
import sys
import argparse
from pathlib import Path

import config, cache, errors, system, update, util

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
  
  parser.add_argument("-debug",
                      action='store_true',
                      help=argparse.SUPPRESS)
  
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
        parsed_args.debug
    ])


def process_cli(args):
    ud = config.get_global('update')
    # Run actions requested via command-line arguments and exit.
    # Auto-update unless noupdate is specified
    if not args.noupdate:
        ud.update_cache()

    # Check if we want to change our data directory
    if args.cd is not None:
        if args.cd == "":
            # user passed "-cd" with no path -> open interactive chooser
            config.move_data()
        else:
            # user passed "-cd <path>"
            config.move_data(Path(args.cd))

    # process gui first, even if other actions are requested
    if args.gui:
        # its not really a gui yet but i'll get there
        interactive_loop()

    if args.backup:
        system.save_backup()

    if args.restorefromarchive:
        cache.restore_vanilla_cache(yes_im_sure=args.yesimsure)

    if args.restore:
        system.load_backup()

    if args.update:
        ud.update_cache()

    if args.extract:
        # extract may be a list of project names
        extract.extract_projects(yes_im_sure=args.yesimsure, listprojects=args.extract)

    if args.extractall:
        if args.ireallymeanit:
            extract.extract_all(yes_im_sure=args.yesimsure, and_i_mean_all_of_them=True)
        else:
            extract.extract_all(yes_im_sure=args.yesimsure)

    if args.append:
        append.append_projects(project_list=args.append, yes_im_sure=args.yesimsure)
        pass

    if args.appendall:
        append.append_all_available(yes_im_sure=args.yesimsure, dryrun=config.get_global('dryrun'))

    return 0

# only runs this when you open the application
# commands can also be accessed from the command line
def interactive_loop(args=None):    
    ud = config.get_global('update')

    print("Entering interactive mode. Type 'help' for a list of commands.")
    while True:
        inp = input('> ').strip().lower()
        match inp:
            case "help":
                print("Available commands:\n",
                      "  update                 - Update the program to the current cache.\n",
                      "  extract [projects]     - Extract one or more projects from the animation cache.\n",
                      "  extractall             - Extract all non-vanilla projects from the animation cache.\n",
                      "  append [projects]      - Append one or more projects to the animation cache.\n",
                      "  appendall              - Append all available projects to the animation cache.\n",
                      "  backup                 - Create a backup of the current animation cache.\n",
                      "  restore                - Restore the animation cache from the latest backup.\n",
                      "  restorefromarchive     - Restore the vanilla animation cache from the program archive.\n",
                      "  dumpjson               - Dump the current animation cache data to a JSON file.\n")

            case "update":
                ud.update_cache()

            case _ if inp.startswith("extract "):
                logging.info("Extracting projects...")
                project_list = inp.split(" ", 1)[1].split(" ")                  
                extract.extract_projects(listprojects=project_list, dryrun=config.get_global('dryrun'))

            case "extractall":
                if args and args.ireallymeanit:
                    logging.info("Extracting all projects, including vanilla...")
                    extract.extract_all(yes_im_sure=args.yesimsure, and_i_mean_all_of_them=True, dryrun=config.get_global('dryrun'))
                else:
                    logging.info("Extracting all non-vanilla projects...")
                    extract.extract_all(yes_im_sure=args.yesimsure if args else False, dryrun=config.get_global('dryrun'))

            case _ if inp.startswith("append "):
                logging.info("Appending projects...")
                project = inp.split(" ", 1)[1].split(" ") 
                append.append_projects(project_list=project)

            case "appendall":
                logging.info("Appending all available projects...")
                append.append_all_available(yes_im_sure=args.yesimsure if args else False, dryrun=config.get_global('dryrun'))

            case "backup":
                logging.info("Creating cache backup...")
                system.save_backup()

            case "restore":
                logging.info("Restoring cache backup...")
                system.load_backup()

            case "restorefromarchive":
                logging.info("Restoring vanilla cache from archive...")
                cache.restore_vanilla_cache()

            case "quit":
                return 0
            
            case "logging ":
                level = inp.split(" ", 1)[1].upper()
                system.set_log_level(level)
                logging.info(f"Log level set to {level}.")

            case "dumpjson" | "dumpjason":
                cfg = config.get_global('config')
                cache.dump_cache()

            case "changedir" | "cd":
                if inp.startswith("changedir ") or inp.startswith("cd "):
                    path = inp.split(" ", 1)[1]
                    config.move_data(Path(path))
                else:
                    config.move_data()

def main(argv=None): 
    
    # detect whether the user invoked the program with command-line flags
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    dryrun = bool(getattr(args, 'dryrun', False))

    system.set_log_level()

    if not config.set_globals(config.Configurator(), update.Updater(), dryrun=dryrun) == 0:
        raise errors.ConfigError()
    
    # make sure the cache is valid
    if not cache.sanitize_cache(args.yesimsure):
        raise errors.CacheError(message="Failed to sanitize cache.")

    force_update = True

    # check for command-line args
    if has_cli_actions(args):
        blah = process_cli(args)
        if not args.gui:
            return 0
        else: force_update = False # we have already updated via cli

    if force_update:
        # auto-update on launch
        ud = config.get_global('update')
        ud.update_cache()
    
    # no command-line args, or args.gui = True, run interactive loop
    interactive_loop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())