import sys
import os
import argparse
import configparser

import update, extract, config, util

# random note: the individual cache files that ship with the game are not up to date.
# they should not be used to rebuild the cache, that will break your game!

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


def process_cli(args, ud, sr, cfg):
    #Run actions requested via command-line arguments and exit.

    # process gui first, even if other actions are requested
    if args.gui:
        # its not really a gui yet but i'll get there
        interactive_loop(ud, sr, cfg)

    if args.update:
        print("Updating cache.")
        #ud.update_all(ud)

    if args.extract:
        # extract may be a list of project names
        for project in args.extract:
            print(f"Extracting {project}.")
            #sr.extract_project(project)

    if args.extractall:
        if args.ireallymeanit:
            print("Extracting all projects.")
            #sr.extract_all_projects(and_i_mean_all_of_them=True)
        else:
            print("Extracting all non-vanilla projects.")
            #sr.extract_all_projects()

    if args.append:
        for project in args.append:
            print(f"Appending {project}.")
            #wr.append_project(project)
    return 0

# only runs this when you open the application
# commands can also be accessed from the command line
def interactive_loop(ud, sr, cfg):
    print("Entering interactive mode. Type 'help' for a list of commands.")
    try:
      while True:
          inp = input('> ').strip().lower()
          match inp:
              case "help":
                  print("Blah blah list of commands")
              case "update":
                  print("Updating cache...")
              case _ if inp.startswith("extract "):
                  project = inp.split(" ", 1)[1]
                  print(f"Extracting {project}.")
              case _ if inp.startswith("append "):
                  project = inp.split(" ", 1)[1]
                  print(f"Appending {project}.")
              case "quit":
                  print("Exiting...")
                  return
    except (KeyboardInterrupt, EOFError):
        print("Something went wrong, exiting...")
        os.system('pause')
        return

def main(argv=None):
    # detect whether the user invoked the program with command-line flags
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    # instantiate code objects
    cfgparser = configparser.ConfigParser()

    cfg = config.Configurator()
    ud = update.Updater()
    sr = extract.Extractor()

    # load values from config
    if not os.path.exists('skycat.ini'):
        cfg.setup_config(cfgparser)
    cfg.load_config(cfgparser)

    # make sure the cache is valid every time, quit on failure.
    if not util.sanitize_cache(cfg, cfgparser):
        return

    # check for command-line args
    if has_cli_actions(args):
        code = process_cli(args, ud, sr, cfg)
        if not args.gui:
            return 0
    else:
        # no command-line args, run interactive loop
        interactive_loop(ud, sr, cfg)
        return 0

if __name__ == "__main__":
    raise SystemExit(main())