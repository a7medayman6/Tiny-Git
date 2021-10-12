from gitCache import listFiles
import sys 

import argparse

from git import *

from gitObjects import cat_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    sub_parsers = parser.add_subparsers(dest='command', metavar='command')

    sub_parsers.required = True

    sub_parser = sub_parsers.add_parser('add',
            help='add file(s) to index')
    sub_parser.add_argument('paths', nargs='+', metavar='path',
            help='path(s) of files to add')

    sub_parser = sub_parsers.add_parser('cat-file',
            help='display contents of object')

    valid_modes = ['commit', 'tree', 'blob', 'size', 'type', 'pretty']

    sub_parser.add_argument('mode', choices=valid_modes,
            help='object type (commit, tree, blob) or display mode (size, '
                 'type, pretty)')

    sub_parser.add_argument('hash_prefix',
            help='SHA-1 hash (or hash prefix) of object to display')

    sub_parser = sub_parsers.add_parser('commit',
            help='commit current state of index to master branch')

    sub_parser.add_argument('-a', '--author',
            help='commit author in format "A U Thor <author@example.com>" '
                 '(uses GIT_AUTHOR_NAME and GIT_AUTHOR_EMAIL environment '
                 'variables by default)')

    sub_parser.add_argument('-m', '--message', required=True,
            help='text of commit message')

    sub_parser = sub_parsers.add_parser('diff',
            help='show diff of files changed (between index and working '
                 'copy)')

    sub_parser = sub_parsers.add_parser('hash-object',
            help='hash contents of given path (and optionally write to '
                 'object store)')

    sub_parser.add_argument('path',
            help='path of file to hash')

    sub_parser.add_argument('-t', choices=['commit', 'tree', 'blob'],
            default='blob', dest='type',
            help='type of object (default %(default)r)')

    sub_parser.add_argument('-w', action='store_true', dest='write',
            help='write object to object store (as well as printing hash)')

    sub_parser = sub_parsers.add_parser('init',
            help='initialize a new repo')

    sub_parser.add_argument('repo',
            help='directory name for new repo')

    sub_parser = sub_parsers.add_parser('ls-files',
            help='list files in index')

    sub_parser = sub_parsers.add_parser('status',
            help='show status of working copy')

    args = parser.parse_args()

    if args.command == 'add':
        add(args.paths)

    elif args.command == 'cat-file':
        try:
            cat_file(args.mode, args.hash_prefix)
        except ValueError as error:
            print(error, file=sys.stderr)
            sys.exit(1)

    elif args.command == 'commit':
        commit(args.message, author=args.author)

    elif args.command == 'hash-object':
        sha1 = generate_object_hash(readFile(args.path), args.type, write=args.write)
        print(sha1)

    elif args.command == 'init':
        init(args.repo)

    elif args.command == 'ls-files':
        listFiles()

    elif args.command == 'status':
        status()

    else:
        raise Exception('unexpected command %' %args.command)