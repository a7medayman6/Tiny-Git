# Data for one entry in the git index (.git/index)
import os 

import struct 

import collections

import hashlib

from helpers import *

from gitObjects import generate_object_hash

"""
    Description:
        The Cache/Index entry format.
"""
CacheEntry = collections.namedtuple('CacheEntry', 
    [
        'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'mode', 'uid',
        'gid', 'size', 'sha1', 'flags', 'path',
    ]
)

def getCache():
    """
        Description:
            Reads the entries of the cache/index, in the CacheEntry format.
        Parameters:
            None.
        Return:
            cache (list): list of the cache/index entries. 
    """
    # if the index file doesn't exist -> return an empty list
    try:
        cache_data = readFile(os.path.join('.git', 'index'))
    except FileNotFoundError:
        return []

    # get the signature, version, and number of entries from the cache
    signature, version, num_entries = struct.unpack('!4sLL', cache_data[:12])
    if signature != b'DIRC':
        raise Exception('Invalid cache signature %' % signature)
    
    # the cache list will contain all the entries in the git cache
    cache = []
    cache_entries = cache_data[12:-20]

    i = 0
    while i + 62 < len(cache_entries):
        # unpack the cache data
        fields_end = i + 62
        fields = struct.unpack('!LLLLLLLLLL20sH',
                               cache_entries[i:fields_end])
        # Get the Null index as the seprator of the path
        seperator = cache_entries.index(b'\x00', fields_end)

        # get the path of the entry/blob
        path = cache_entries[fields_end:seperator]

        # put the entry in the format of IndexEntry
        entry = CacheEntry(*(fields + (path.decode(),)))
        
        # add the entry to the list of entries extracted from the cache
        cache.append(entry)

        # calc the entry length
        entry_len = ((62 + len(path) + 8) // 8) * 8
        
        # update the loop pointer
        i += entry_len

    # return a list of all the entries in the cache/index file.
    return cache

def listFiles(quiet=False):
    """
        Description:
            Displays all the files paths from the cache.
        Parameters:
            [quiet] (boolean):  optional parameter, true by default
                                if print = true -> print the entries paths to the screen
                                else -> don't print. 
        Return:
            files (list) : list of files paths from the cache.        
    """

    # get the cache list
    cache = getCache()
    files = []

    # if the cache is empty -> print 'empty' and return an empty list
    if not cache:
        print('Git index is empty')
    
    # for each entry in the cache => print the entry path
    for entry in cache:
        if not quiet:
            print(entry.path)
        files.append(entry.path)
    
    # return list of all the files paths
    return files
    
def getWorkdirState(path = '.'):
    """
        Description:
            Gets the state of each file in the working dir.
            By calc the sha1 hash of the file and compare it to the cache hash for the crosspoding file. 
        Parameters:
            [path] (string): the path of the git repository, path = '.' by default. 
        Return:
            states (tuple) : tuple of the 3 lists 
                - new       => the list of new files
                - modified  => the list of modified files
                - deleted   => the list of deleted files
    """
    
    directory_files = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d != '.git']

        for file in files:
            path = os.path.join(root, file)
            
            # if running on windows -> change \\ to / in the path string
            path = path.replace('\\', '/')

            # if the path is simmilar to ./file -> remove './'
            if path.startswith('./'):
                path = path[2:]
            
            directory_files.append(path)
    
    # get the cache entries paths
    cache_entries_files = set(listFiles(quiet=True))
    
    # get list of the new files, by subtracting directory files list from the files in the cache
    new = directory_files - cache_entries_files
    # the modified files set
    modified = []
    # get list of the deleted files, by subtracting the list of files in the cache from the directory files list 
    deleted = cache_entries_files - directory_files
    
    # add the modified files to the list by comparing the sha1 hash of the working dir file and the cache file
    for file in (directory_files & cache_entries_files):
        if generate_object_hash(readFile(file), 'blob', write=False) != cache_entries_files[file].sha1.hex() :
            modified.add(file)
    
    states = (new, modified, deleted)
    
    return states

