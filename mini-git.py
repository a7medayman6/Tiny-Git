import os

import hashlib

from helpers import *

def init(path):
    """
        Initialize a directory at $path as a git repository.
        Creates .git directory inside.
    """

    
    # if path is already a git repository -> raise and exception.
    if os.path.isdir(os.path.join(path, '.git')):
        raise Exception('Already a git repository.')

    
    # Create the nessecary dirs and files.
    os.mkdir(os.path.join(path, '.git'))
    os.mkdir(os.path.join(path, '.git', 'objects'))
    os.mkdir(os.path.join(path, '.git', 'refs'))
    os.mkdir(os.path.join(path, '.git', 'refs/HEAD'))
    write_file(os.path.join(path, '.git', 'HEAD'), b'ref: refs/heads/master')
    
    print('Initialized an empty git repository at ', path)

def generate_object_hash(data, type):
    """
        Generates hash of the object including the data and it's header.
    """

    # the obj header contains the type of the object, and it's size
    obj_header = '{} {}'.format(type, len(data)).encode()

    # the object consists of the header then Null byte then it's data
    obj = obj_header + b'\x00' + data

    # hash the object using sha1
    sha1 = hashlib.sha1(obj).hexdigest()

    return sha1;
