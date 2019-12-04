#!/usr/bin/env python3
"""
    Public Meetings utility commands

    From:
    https://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
"""
import argparse
import sys
import public_meetings


class PublicMeetingsCommands(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Utilities for the `public_meetings` corpus"
        )

        command_list = [
            func for func in dir(PublicMeetingsCommands)
            if callable(getattr(PublicMeetingsCommands, func))
            and "__" not in func
        ]
        parser.add_argument('command', help='Subcommand to run',
                            choices=command_list)
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            print("Invalid command '%s'" % args.command)
            parser.print_help()
            exit(1)

        command_fct = getattr(self, args.command)
        sys.argv = sys.argv[1:]
        command_fct()

    def prepare(self):
        public_meetings.prepare.main()

    def segmentation(self):
        public_meetings.meetings_to_segmentation.main()


def main():
    PublicMeetingsCommands()
