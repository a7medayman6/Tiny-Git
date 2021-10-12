import os

import sys 

import hashlib

import zlib

import stat

from helpers import *

from gitCache import getCache



def writeObject(obj):
    """
        Description:
            Writes the object hash compressed to .git/objects as hex string.
        Parameters: 
            obj (SHA-1 string)): object string generated using generate_object_hash function.
        Return:
            obj (SHA-1 string)): object string generated using generate_object_hash function.
    """

    """
        if the object path doesn't exist create it, then write the object.
        the object is written to .git/objects/obj[:2]/obj[2:] 
        where obj[:2] is the first 2 chars of the 40 chars sha1 hash, and obj[2:0] are the rest 
    """
    obj_path = os.path.join('.git', 'objects', obj[:2], obj[2:])
    if not os.path.exists(obj_path):
        os.makedirs(os.path.dirname(obj_path), exist_ok=True)
        writeFile(obj_path, zlib.compress(obj))
    else:
        raise Exception('The object already exists at %' % obj_path)

    return obj

def findObject(obj_hash_prefix):
    """
        Description: 
            Finds the path of an object using it's first 3 or more chars of it's sha1 hash, if it exists.
        Parameters:
            obj_hash_prefix (SHA-1 string)): the first 3 or more chars of object sha1 hash string.
        Return:
            (str): the path of the object if it exists, otherwise raise an exception.
    """
    # if the hash prefix length is less than 2, raise an excpetion.
    if len(obj_hash_prefix) < 3:
        raise Exception('The sha1 hash prefix must be more than 2 charcters.')
    
    # create the object dir which is at .git/objects/obj_hash_prefix[:2]
    # where obj_hash_prefix[:2] is the first two chars of the hash prefix.
    obj_dir = os.path.join('.git', 'objects', obj_hash_prefix[:2])
    
    # get a list of all the objects (files in obj_dir) that starts with the string obj_hash_prefix[2:]
    # where obj_hash_prefix[2:] is all the chars in the hash prefix after the second char
    objects_list = [name for name in os.listdir(obj_dir) if name.startswith(obj_hash_prefix[2:])]

    # if the objects list is empty -> raise an object not found exception.
    if not objects_list:
        raise Exception('Object % not found.' % obj_hash_prefix)
    
    # if the objects list has more than one object -> raise multiple objects found exception.
    if len(objects_list) > 1:
        raise Exception('There are multiple objects starts with the prefix % please spicify with more characters.' % obj_hash_prefix)
    
    # return the first (and only) object in the objects list.
    return os.path.join(obj_dir, objects_list[0])

def getObject(obj_hash_prefix):
    """
        Description: 
            Reads an object from it's sha1_prefix if it exist.
        Parameters:
            obj_hash_prefix (SHA-1 string)): the first 3 or more chars of object sha1 hash string.
        Return:
            type (str): the object type [blob, commit, tree].
            data (str): the decompressed data.
    """

    # get the object file path
    obj_path = findObject(obj_hash_prefix)
    
    # read the data from the obj_path 
    compressed_data = readFile(obj_path)

    # decompress the data
    decompressed_data = zlib.decompress(compressed_data) 
    
    # get the index of the Null character in the data.
    seperator = decompressed_data.index(b'\x00')

    # get the header data which is the string before the Null char.
    header = decompressed_data[:seperator]
    
    # decode the header
    decoded_header = header.decode()

    # get the type and ignore the size from the decoded header
    type, _ = decoded_header.split()
    
    # get the data which is the string after the Null char.
    data = decompressed_data[seperator + 1:]

    # return the type and data of the specified object
    return (type, data)


def getTree(obj_hash_prefix=None, data=None):
    """
        Description: 
            Reads a git tree and splits the objects inside it, 
            gevin it's hash prefix OR a tree object data.
        Parameters:
            obj_hash_prefix (SHA-1 string)): the first 3 or more chars of object sha1 hash string.
            data (str): the decoded data of a tree object file -without the header-.
        Return:
            entries (list): list of all the objects inside the specified tree.
    """
    if obj_hash_prefix is None and data is None:
        raise TypeError('must specify "obj_hash_prefix" or "data"')
    elif obj_hash_prefix is not None:
        type, data = getObject(obj_hash_prefix)
        assert type == 'tree', 'specified object type is not a tree'
        
    i = 0
    entries = []
    for _ in range(1000):
        end = data.find(b'\x00', i)
        if end == -1:
            break

        mode, path = data[i:end].decode().split()
        mode = int(mode, 8)
        digest = data[end + 1:end + 21]
        entries.append((mode, path, digest.hex()))
        i = end + 1 + 20

    return entries

def writeTree():
    """
        Description: 
            Writes a tree from the cache to the db.
        Parameters:
            None.
        Return:
            obj_hash (SHA-1 string)): generated hash of the tree object.
    """
    tree_entries = []

    for entry in getCache():
        mode_path = '{:o} {}'.format(entry.mode, entry.path).encode()

        # create the entry object
        object = mode_path + b'\x00' + entry.sha1
        tree_entries.append(object)

    obj_hash = generate_object_hash(b''.join(tree_entries), 'tree')
    return obj_hash

def cat_file(mode, obj_hash_prefix):
    """
        Description: 
            Displays an object in a specific format according to the mode argument.
        Parameters:
            mode (str): the mode to display the object.
            obj_hash_prefix (SHA-1 string)): the first 3 or more chars of object sha1 hash string.
        Return:
            None.
    """
    # get the object data and type
    type, data = getObject(obj_hash_prefix)

    if mode in ['commit', 'tree', 'blob']:
        # if the mode is a type, but not equivilant to the object type -> raise an exception
        # else -> print the object data
        if type != mode:
            raise Exception('expected object type % , got %' % mode %type)
        sys.stdout.buffer.write(data)

    # if the mode is size -> print the object size = length of obj data
    elif mode == 'size':
        print(len(data))
    
    # if the mode is type -> print the type of the object
    elif mode == 'type':
        print(type)

    # if the mode is pretty -> if the type is tree, print the tree in beautified format.
    elif mode == 'pretty':
        if type in ['commit', 'blob']:
            sys.stdout.buffer.write(data)
        elif type == 'tree':
            for mode, path, sha1 in getTree(data=data):
                inner_object_type = 'tree' if stat.S_ISDIR(mode) else 'blob'
                print('{:06o} {} {}\t{}'.format(mode, inner_object_type, sha1, path))
        else:
            raise Exception('Unexpected object type. %' % type)
    else:
        raise Exception('Unexpected mode %' % mode)

def getCommitHash():
    """
        Description: 
            Gets the current commit SHA-1 hash.
        Parameters:
            None.            
        Return:
            master_hash (SHA-1 string): generated hash of the tree object.
    """
    master_file = os.path.join('.git', 'refs', 'heads', 'master')

    try:
        master_hash = readFile(master_file).decode().strip()
        return master_hash
    except FileNotFoundError:
        return None