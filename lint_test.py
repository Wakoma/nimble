#! /usr/bin/env python

"""
Linting for a GitHub action
"""
import sys
import argparse
from pylint.lint import Run
from colorama import Fore, Style

def main():
    """
    Check which type of files we are linting.
    i.e. the standard python exceuted files, or scripts executed by cq-cli
    Then pass these into the linting script
    """

    help_str = ('Run pylint on either the main python scripts or the CadQuery scripts '
                'for cq-cli. These are linted seperately to allow a different pylint-rc '
                'file. This is needed to allow special built-ins such as `show_object` '
                'and to allow top level parameters to use snake_case tather than UPPER_CASE'
                'naming styles')
    parser = argparse.ArgumentParser(
            prog='Nimble python linting',
            description=help_str)
    parser.add_argument(
            '-t',
            '--file_type',
            default='py',
            required=False,
            help = 'Options are either `py` or `cadquery`. Default: `py`')
    args = parser.parse_args()
    if args.file_type == "py":
        lint([
            'generate.py',
            'generate_static.py',
            'nimble_orchestration',
            'nimble_builder'
        ])
    elif args.file_type == "cadquery":
        lint(['mechanical', '--rcfile=cq.pylintrc'])
    else:
        print(Fore.RED+f"\n\nUnknown file type {args.file_type}\n\n"+Style.RESET_ALL)
        sys.exit(1)



def lint(pylint_args):
    """
    This will exit with a code of 1 for the CI to fail if:
    * There are any warnings, errors, or fatal errors.
    * The pylint score is less than 9.75
    Note this means that it fails if there are TODOs in the code.
    This means that TODOs are to warn you that is something is unfinished, if
    something needs doing in the future and you want to push to master then make an issue.
    """

    


    output = Run(pylint_args, exit=False)

    clean_exit = True
    linter_threshold = 9.75

    try:
        _ = iter(output.linter.stats)
        stats = output.linter.stats
    except TypeError:
        stats = {'fatal': output.linter.stats.fatal,
                 'error': output.linter.stats.error,
                 'warning': output.linter.stats.warning,
                 'global_note': output.linter.stats.global_note}

    if stats['fatal'] > 0:
        print(Fore.RED
              +f"There are {stats['fatal']} fatal errors!"
              +Style.RESET_ALL)
        clean_exit = False

    if stats['error'] > 0:
        print(Fore.RED
              +f"There are {stats['error']} errors!"
              +Style.RESET_ALL)
        clean_exit = False

    if stats['warning'] > 0:
        print(Fore.RED
              +f"There are {stats['warning']} warning!"
              +Style.RESET_ALL)
        clean_exit = False

    if stats['global_note'] < linter_threshold:
        print(Fore.RED
              +f"The linter score of f{stats['global_note']:.2f}"
              +f" is less than {linter_threshold:.2f}"
              +Style.RESET_ALL)
        clean_exit = False

    if clean_exit:
        print(Fore.GREEN+"\n\n This will pass on the CI!\n\n"+Style.RESET_ALL)
    else:
        print(Fore.RED+"\n\nThis will fail on the CI!\n\n"+Style.RESET_ALL)
        sys.exit(1)

if __name__ == "__main__":
    main()
