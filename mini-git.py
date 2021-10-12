import os

import sys 

import hashlib

import zlib

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

def generate_object_hash(data, type):
    """
        Description:
            Generates hash of the object including the data and it's header.
        Parameters:
            data (str): the object data
            type (str): the object type which is one of three types (blob, commit, tree) 
        Return:
            sha1 (hex string): hashed object of the header and data.
    """

    # the obj header contains the type of the object, and it's size
    obj_header = '{} {}'.format(type, len(data)).encode()

    # the object consists of the header then Null byte then it's data
    obj = obj_header + b'\x00' + data

    # hash the object using sha1
    sha1 = hashlib.sha1(obj).hexdigest()

    return sha1

def write_object(obj):
    """
        Description:
            Writes the object hash compressed to .git/objects as hex string.
        Parameters: 
            obj (sha1 hex string): object string generated using generate_object_hash function.
        Return:
            obj (sha1 hex string): object string generated using generate_object_hash function.
    """

    """
        if the object path doesn't exist create it, then write the object.
        the object is written to .git/objects/obj[:2]/obj[2:] 
        where obj[:2] is the first 2 chars of the 40 chars sha1 hash, and obj[2:0] are the rest 
    """
    obj_path = os.path.join('.git', 'objects', obj[:2], obj[2:])
    if not os.path.exists(obj_path):
        os.makedirs(os.path.dirname(obj_path), exist_ok=True)
        write_file(obj_path, zlib.compress(obj))
    else:
        raise Exception('The object already exists at %' % obj_path)

    return obj

def find_object(obj_hash_prefix):
    """
        Description: 
            Finds the path of an object using it's first 3 or more chars of it's sha1 hash, if it exists.
        Parameters:
            obj_hash_prefix (str): the first 3 or more chars of sha1 hash string.
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

def read_object(obj_hash_prefix):
    """
        Description: 
            Reads an object from it's sha1_prefix if it exist.
        Parameters:
            obj_hash_prefix (str): the first 3 or more chars of sha1 hash string.
        Return:
            type (str): the object type [blob, commit, tree].
            data (str): the decompressed data.
    """

    # get the object file path
    obj_path = find_object(obj_hash_prefix)
    
    # read the data from the obj_path 
    compressed_data = read_file(obj_path)

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

def cat_file(mode, sha1_prefix):
    """Write the contents of (or info about) object with given SHA-1 prefix to
    stdout. If mode is 'commit', 'tree', or 'blob', print raw data bytes of
    object. If mode is 'size', print the size of the object. If mode is
    'type', print the type of the object. If mode is 'pretty', print a
    prettified version of the object.
    """
    obj_type, data = read_object(sha1_prefix)
    if mode in ['commit', 'tree', 'blob']:
        if obj_type != mode:
            raise ValueError('expected object type {}, got {}'.format(
                    mode, obj_type))
        sys.stdout.buffer.write(data)
    elif mode == 'size':
        print(len(data))
    elif mode == 'type':
        print(obj_type)
    elif mode == 'pretty':
        if obj_type in ['commit', 'blob']:
            sys.stdout.buffer.write(data)
        elif obj_type == 'tree':
            for mode, path, sha1 in read_tree(data=data):
                type_str = 'tree' if stat.S_ISDIR(mode) else 'blob'
                print('{:06o} {} {}\t{}'.format(mode, type_str, sha1, path))
        else:
            assert False, 'unhandled object type {!r}'.format(obj_type)
    else:
        raise ValueError('unexpected mode {!r}'.format(mode))

def read_tree(obj_hash_prefix=None, data=None):

    if obj_hash_prefix is None and data is None:
        raise TypeError('must specify "obj_hash_prefix" or "data"')
    elif obj_hash_prefix is not None:
        type, data = read_object(obj_hash_prefix)
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