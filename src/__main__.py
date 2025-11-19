import sys
import os
import argparse

import config, system, update, util

import extract, append, validate


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
  
  # debug helpers
  parser.add_argument("-noupdate",
                      action='store_true',
                      help="Skip updating the program. Note: This might break stuff, only use if you know what you're doing.")
  
  parser.add_argument("-debug",
                      action='store_true',
                      help=argparse.SUPPRESS)
  
  parser.add_argument("-dryrun",
                      action='store_true',
                      help=argparse.SUPPRESS)
  return parser

def has_cli_actions(parsed_args) -> bool:
    # check if any meaningful command-line arguments were provided.
    # only consider arguments that trigger actions
    return any([
        parsed_args.update,
        parsed_args.extract,
        parsed_args.extractall,
        parsed_args.append,
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

    # process gui first, even if other actions are requested
    if args.gui:
        # its not really a gui yet but i'll get there
        interactive_loop()

    if args.backup:
        system.save_backup()

    if args.restorefromarchive:
        system.restore_vanilla_cache()

    if args.restore:
        system.load_backup()

    if args.update:
        ud.update_cache()

    if args.extract:
        # extract may be a list of project names
        extract.extract_projects(args.extract)

    if args.extractall:
        if args.ireallymeanit:
            extract.extract_all_projects(and_i_mean_all_of_them=True)
        else:
            extract.extract_all_projects()

    if args.append:
        append.append_projects(args.append)
        pass
    return 0

# only runs this when you open the application
# commands can also be accessed from the command line
def interactive_loop(args=None):    
    ud = config.get_global('update')

    print("Entering interactive mode. Type 'help' for a list of commands.")
    try:
      while True:
          inp = input('> ').strip().lower()
          match inp:
                case "help":
                    print("Blah blah list of commands")

                case "update":
                    ud.update_cache()

                case _ if inp.startswith("extract "):
                    project_list = inp.split(" ", 1)[1].split(" ")                  
                    extract.extract_projects(project_list)

                case _ if inp.startswith("append "):
                    project = inp.split(" ", 1)[1].split(" ") 
                    append.append_projects(project)

                case "backup":
                    print("Creating cache backup...")
                    system.save_backup()

                case "restore":
                    print("Restoring cache backup...")
                    system.load_backup()

                case "restorefromarchive":
                    system.restore_vanilla_cache()

                case "quit":
                    return 0
              
                # case "debug":
                #     import util
                #     util.helper_function()

                case "dumpjson":
                    cfg = config.get_global('config')
                    util.dump_json(cfg.cache / config.animdata_pq_path, cfg.cache / config.animdata_json_path)
                    util.dump_json(cfg.cache / config.animsetdata_pq_path, cfg.cache / config.animsetdata_json_path)
                    print("Dumped animdata and animsetdata to JSON.")
              
    except Exception as e:
        print(f"An error has occurred: {e}")
        util.pause_wait_for_input()
        return 1

def main(argv=None): 
    
    # detect whether the user invoked the program with command-line flags
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    dryrun = argv.dryrun if argv else False

    if not config.set_globals(config.Configurator(), update.Updater(), dryrun=dryrun) == 0:
        print("Could not set globals!")
        return 1
    
    # make sure the cache is valid
    if not util.sanitize_cache():
        return

    force_update = True

    # check for command-line args
    if has_cli_actions(args):
        code = process_cli(args)
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