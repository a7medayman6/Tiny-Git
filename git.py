import os

import time 

from helpers import *

from gitCache import getWorkdirState, getCache, CacheEntry, writeCache

from gitObjects import generate_object_hash, getCommitHash, writeTree


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
    os.mkdir(os.path.join(path, '.git', 'refs/heads'))
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

def add(files):
    """
        Description:
            Add the list of files to the index.
        Parameters:
            files (list): list of files to add  
        Return:
            None.
    """
    # for windows, replace '\\' with '/'
    files = [path.replace('\\', '/') for path in files]

    cache_entries = getCache()

    entries = [entry for entry in cache_entries if entry.path not in files]

    for file in files:
        hash = generate_object_hash(readFile(file), 'blob')
        st = os.stat(file)
        flags = len(file.encode())

        entry = CacheEntry(
                int(st.st_ctime), 0, int(st.st_mtime), 0, st.st_dev,
                st.st_ino, st.st_mode, st.st_uid, st.st_gid, st.st_size,
                bytes.fromhex(hash), flags, file)
        entries.append(entry)
    
    writeCache(entries)

def commit(msg, author):
    """
        Description:
            Commits the staged files to the repository.
        Parameters:
            msg (string): the commit message.
            author (string): the commit author name.  
        Return:
            None.
    """   
    tree = writeTree()
    parent = getCommitHash()
    timestamp = int(time.mktime(time.localtime()))
    utc_offset = -time.timezone
    author_time = '{} {}{:02}{:02}'.format(
            timestamp,
            '+' if utc_offset > 0 else '-',
            abs(utc_offset) // 3600,
            (abs(utc_offset) // 60) % 60)
    lines = ['tree ' + tree]
    
    if parent:
        lines.append('parent ' + parent)
    lines.append('author {} {}'.format(author, author_time))
    lines.append('committer {} {}'.format(author, author_time))
    lines.append('')
    lines.append(msg)
    lines.append('')
    data = '\n'.join(lines).encode()

    obj_hash = generate_object_hash(data, 'commit')

    master_path = os.path.join('.git', 'refs', 'heads', 'master')

    writeFile(master_path, (obj_hash + '\n').encode())
    print('committed ', obj_hash, ' to master.')

    return obj_hash