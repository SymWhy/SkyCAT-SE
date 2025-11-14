import sys
import os
import argparse

import config, system, update

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
  parser.add_argument("-backup",
                      help="Create a backup of the current animation cache.",
                      action='store_true')
  parser.add_argument("-restore",
                      help="Restore the animation cache from the latest backup.",
                      action='store_true')
  parser.add_argument("-gui",
                      help="Launch the full program.",
                      action='store_true')
  return parser

def has_cli_actions(parsed_args) -> bool:
    # Check if any meaningful command-line arguments were provided.
    return any([
        parsed_args.update,
        parsed_args.extract,
        parsed_args.extractall,
        parsed_args.append,
        parsed_args.gui,
    ])


def process_cli(args):
    ud = update.require_update()
    #Run actions requested via command-line arguments and exit.

    # process gui first, even if other actions are requested
    if args.gui:
        # its not really a gui yet but i'll get there
        interactive_loop()

    if args.update:
        ud.update_all()

    if args.extract:
        # extract may be a list of project names
        extract.extract_projects(args.extract)

    if args.extractall:
        if args.ireallymeanit:
            extract.extract_all_projects(and_i_mean_all_of_them=True)
        else:
            extract.extract_all_projects()

    if args.append:
        # append_projects(args.append)
        pass

    if args.backup:
        system.save_backup()

    if args.restore:
        system.load_backup()

# only runs this when you open the application
# commands can also be accessed from the command line
def interactive_loop():
    ud = update.require_update()

    print("Entering interactive mode. Type 'help' for a list of commands.")
    try:
      while True:
          inp = input('> ').strip().lower()
          match inp:
                case "help":
                    print("Blah blah list of commands")
                case "update":
                    ud.update_all()
                case _ if inp.startswith("extract "):
                    project_list = inp.split(" ", 1)[1].split(" ")                  
                    extract.extract_projects(project_list)
                case _ if inp.startswith("append "):
                    project = inp.split(" ", 1)[1].split(" ") 
                    print(f"Appending {project}.")
                case "backup":
                    print("Creating cache backup...")
                    system.save_backup()
                case "restore":
                    print("Restoring cache backup...")
                    system.load_backup()
                case "restorefromarchive":
                    system.restore_vanilla_cache()
                case "quit":
                    print("Exiting...")
                    return
    except (KeyboardInterrupt, EOFError):
        print("Something went wrong, exiting...")
        os.system('pause')
        return

def main(argv=None):
    config.set_global_config(config.Configurator())
    update.set_global_update(update.Updater())

    print(config._GLOBAL_CONFIG)
       
    # detect whether the user invoked the program with command-line flags
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    # check for command-line args
    if has_cli_actions(args):
        code = process_cli(args)
        if not args.gui:
            return 0
    else:
        # no command-line args, run interactive loop
        interactive_loop()
        return 0

if __name__ == "__main__":
    raise SystemExit(main())