import os

from helpers import *


def init(path = '.'):
    """
        Description:
            Initialize a directory at $path as a git repository.
            Creates .git directory at path/.git .
        Parameters:
            path (string): the path to create the git repository at. path='.' by default.
        Return:
            (boolean): true if initialized successfully, false otherwise. 
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
    write_file(os.path.join(path, '.git', 'HEAD'), b'ref: refs/heads/master')
    
    print('Initialized an empty git repository at ', path)

    return True

