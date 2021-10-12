import os

from helpers import *

from gitCache import getWorkdirState


def init(path = '.'):
    """
        Description:
            Initialize a directory at $path as a git repository.
            Creates .git directory at path/.git .
        Parameters:
            path (string): the path to create the git repository at. path='.' by default.
        Return:
            (boolean): true if initialized successfully, otherwise raise an exception. 
    """

    
    # if path is already a git repository -> raise and exception.
    if os.path.isdir(os.path.join(path, '.git')):
        raise Exception('Already a git repository.')

    # Create the nessecary dirs and files.
    os.mkdir(os.path.join(path, '.git'))
    os.mkdir(os.path.join(path, '.git', 'objects'))
    os.mkdir(os.path.join(path, '.git', 'refs'))
    os.mkdir(os.path.join(path, '.git', 'refs/HEAD'))

    # Write to the HEAD file the branch pointer in refs. 
    writeFile(os.path.join(path, '.git', 'HEAD'), b'ref: refs/heads/master')
    
    print('Initialized an empty git repository at ', path)

    return True

def status(path = '.'):
    """
        Description:
            Displays the status of the working directory copy (new, modified, deleted).
        Parameters:
            [path] (string): the path of the git repository, path = '.' by default. 
        Return:
            None.
    """
    new, modified, deleted = getWorkdirState(path)
    
    # print the new list
    if new:
        print ("New files ..")
        for file in new:
            print('\t', file)
        print('\t', "__________________")

    # print the modified list
    if modified:
        print ("Modified files ..")
        for file in modified:
            print('\t', file)
        print('\t', "__________________")

    # print the deleted list
    if deleted:
        print ("Deleted files ..")
        for file in deleted:
            print('\t', file)
        print('\t', "__________________")

