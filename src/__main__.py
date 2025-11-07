import pandas as pd
import sys

import updater
import search
import defs
import util

ud = updater.Updater()
sr = search.Search()

# random note: the individual cache files that ship with the game are not up to date.
# they should not be used to rebuild the cache, that will break your game!

import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-update",
                    action='store_true',
                    help="Sync the program with your existing animation cache.")

parser.add_argument("-unpack",
                    action='append',
                    help='Unpack one or more projects from the animation cache.\n'
                    'For example: "-unpack catproject snakeproject"')

parser.add_argument("-unpackall",
                     action='store_true',
                     help='Unpack all non-vanilla projects from the animation cache.\n'
                     'Use "-ireallymeanit" to also unpack vanilla projects.\n'
                     '(Use at your own risk.)')
parser.add_argument("-ireallymeanit",
                    action='store_true')

parser.add_argument("-append",
                    action='append',
                    help='Append one or more projects to the animation cache.\n'
                    'For example: "-append catproject snakeproject"')

# Pass an empty list to parse_args() to ignore Colab's default arguments
args = parser.parse_args([])

if args.update:
  print("Updating cache.")

if args.extract:
  for project in args.extract:
    print(f"Extracting {project}.")

if args.extractall:
  if args.ireallymeanit:
    print("Extracting all projects.")
  else:
    print("Extracting all non-vanilla projects.")

if args.append:
  for project in args.append:
    print(f"Appending {project}.")

# only runs this when you open the application
# commands can also be accessed from the command line
def main():
    cache_clean = util.sanitize_cache()
    match cache_clean:
        case "animdata":
            ud.update_animdata(defs.animdata)
            ud.update_animdata(defs.animsetdata)

        case "animsetdata":
            ud.update_animsetdata(defs.animsetdata)

    to_next = False

    # suggest cache update
    while not to_next:
        print("Update cache? Y/N")
        inp = input().lower()
        match inp:
            case "y":
                ud.update_animdata(defs.animdata)
                ud.update_animsetdata(defs.animsetdata)
                to_next = True
            case "n":
                to_next = True

    # main loop
    while True:
        inp = input().lower()
        match inp.split(maxsplit=1):
            case ["help"]:
                print("Blah blah list of commands")
            case ["update"]:
                print("Updating cache...")
            case ["extract", project]:
                print(f"Extracting {project}.")
            case ["quit"]:
                print("Goodbye.")
                sys.exit()


# ud.update_animdata(defs.animdata)
# ud.update_animsetdata(defs.animsetdata)

# searcher.extract_project("VampireLord")
# searcher.extract_project("WoodenBow")
# searcher.extract_project("SnailProject")
# searcher.extract_project("IBHFTrapYokuRuinsSawblade01")

# searcher.extract_all_projects(True)


if __name__ == '__main__':
    main()