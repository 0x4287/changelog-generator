#!/usr/bin/env python3

import argparse
import os
import re
import sys
from enum import Enum, auto
from subprocess import PIPE, Popen


class Commit:

    def __init__(self, version_tag=None, commit_hash=None, commit_msg=None, commit_type=None, commit_category=None,
                 commit_description=None):
        self.version_tag = version_tag
        self.commit_hash = commit_hash
        self.commit_msg = commit_msg
        self.commit_type = commit_type
        self.commit_category = commit_category
        self.commit_description = commit_description


class Type(Enum):
    BREAK = auto()
    BUILD = auto()
    DOCS = auto()
    FEAT = auto()
    FIX = auto()
    MISC = auto()
    PERF = auto()
    REFAC = auto()
    TEST = auto()


def consent_overwrite():
    overwrite = input('Do you want to overwrite it? [Y/n]: ').upper()
    if overwrite == 'Y' or overwrite == '':
        return True
    elif overwrite == 'N':
        return False
    else:
        print('invalid input')
        return consent_overwrite()


TYPE_TEXT = {
    Type.BREAK.name: 'Breaking Changes',
    Type.BUILD.name: 'Build and Dependency Changes',
    Type.DOCS.name: 'Documentation Changes',
    Type.FEAT.name: 'New Features',
    Type.FIX.name: 'Bugfixes',
    Type.MISC.name: 'Miscellaneous',
    Type.PERF.name: 'Performance Improvements',
    Type.REFAC.name: 'Refactoring',
    Type.TEST.name: 'Tests'
}

CLOGG_VERSION = "v1.0.0"
VERSION_PATTERN = re.compile('v?[0-9]+\.[0-9]+\.[0-9]+(-([0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*))?')
TYPE_PATTERN = re.compile('^\[[a-zA-Z]{3,5}\]')
CATEGORY_PATTERN = re.compile('\([a-zA-Z\d\ ]+\)')

# reading CLI arguments
parser = argparse.ArgumentParser(prog='clogg',
                                 description="A simple CLI tool for generating changelogs"
                                             " from git commits and version tags.")

parser.add_argument('-v', action='store_true', help='return the installed version of clogg')
parser.add_argument('-a', action='store_true', help='append the generated changelog to an existing file')
parser.add_argument('-d', help='root directory of the git project, defaults to ./', metavar='<Directory>', default="./")
# parser.add_argument('-e', help='version tag where the changelog should end', metavar='<End_Tag>')
parser.add_argument('-f', action='store_true', help='force override existing output file', default=False)
parser.add_argument('-o', help='output for the changelog file, defaults to ./CHANGELOG.md', metavar='<Output>',
                    default='./CHANGELOG.md')
# parser.add_argument('-s', help='version tag where teh changelog should start', metavar='<Start_Tag>')

args = parser.parse_args()

# handling -v argument
if args.v:
    print('clogg ' + CLOGG_VERSION)
    sys.exit(0)

# changing working directory
try:
    os.chdir(args.d)
except FileNotFoundError as e:
    print('error: directory ' + args.d + ' not found')
    sys.exit(1)

# reading git log data
p = Popen(['git', 'log', '-E', '--format=@@DEC%d@@CMS %s@@CID %H@@CMD %b'], stdin=PIPE, stdout=PIPE,
          stderr=PIPE)
output, err = p.communicate()

# handling git log errors
if err:
    print('error: directory ' + os.getcwd() + ' is not a git repository')
    sys.exit(1)

output = output.decode('utf-8').split('@@')

# parsing commits
commits = []
versions = []
cur_commit = Commit()
for entry in output:
    if entry[:3] == 'DEC':
        match = VERSION_PATTERN.search(entry)
        if match:
            cur_commit.version_tag = match.group(0)
            versions.append(match.group(0))
    elif entry[:3] == 'CMS':
        match = TYPE_PATTERN.search(entry[4:])
        if match:
            cur_commit.commit_type = match.group(0)[1:-1].upper()
            cur_commit.commit_msg = entry[4 + len(match.group(0)):].strip()
    elif entry[:3] == 'CID':
        cur_commit.commit_hash = entry[4:]
    elif entry[:3] == 'CMD':
        match = CATEGORY_PATTERN.search(entry[4:])
        if match:
            cur_commit.commit_category = match.group(0)[1:-1].strip()
            cur_commit.commit_description = entry[4 + len(match.group(0)):].strip()
        else:
            cur_commit.commit_description = entry[4:].strip()
        if cur_commit.commit_type:
            commits.append(cur_commit)
        version_tag_tmp = cur_commit.version_tag
        cur_commit = Commit()
        cur_commit.version_tag = version_tag_tmp

# check if changelog file exist and get consent to overwrite
if os.path.exists(args.o) and not (args.f or args.a):
    print('the file ' + os.path.abspath(args.o) + ' already exists')
    if not consent_overwrite():
        sys.exit(0)

# open changelog file
try:
    if args.a:
        changelog = open(args.o, 'a', -1)
    else:
        changelog = open(args.o, 'w', -1)
        changelog.write('# Changelog \n\n')
except PermissionError:
    print('error: please make sure you have permission to edit ' + os.path.abspath(args.o))
    sys.exit(1)

for version in versions:
    changelog.write('## ' + version + ' \n\n')
    version_set = [n for n in commits if n.version_tag == version]
    for name in Type.__members__.keys():
        type_set = [n for n in version_set if n.commit_type == name]
        if len(type_set) > 0:
            changelog.write('### ' + TYPE_TEXT[name] + ' \n\n')
            for change in type_set:
                string = '- '
                if change.commit_category:
                    string += '**' + change.commit_category + ':** '
                string += change.commit_msg.replace('\n', '\n  >')
                string += ' (' + change.commit_hash[:7] + ') \n'
                if change.commit_description:
                    string += '  >' + change.commit_description + '\n\n'
                else:
                    string += '\n'
                changelog.write(string)

changelog.close()
print('successfully created changelog at: ', os.path.abspath(args.o))
sys.exit(0)
