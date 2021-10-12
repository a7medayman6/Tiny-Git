import hashlib


def readFile(path):
    """Read contents of file at given path as bytes."""
    with open(path, 'rb') as f:
        return f.read()


def writeFile(path, data):
    """Write data bytes to file at given path."""
    with open(path, 'wb') as f:
        f.write(data)

def generate_object_hash(data, type):
    """
        Description:
            Generates hash of the object including the data and it's header.
        Parameters:
            data (str): the object data
            type (str): the object type which is one of three types (blob, commit, tree) 
        Return:
            sha1 (SHA-1 string)): hashed object of the header and data.
    """

    # the obj header contains the type of the object, and it's size
    obj_header = '{} {}'.format(type, len(data)).encode()

    # the object consists of the header then Null byte then it's data
    obj = obj_header + b'\x00' + data

    # hash the object using sha1
    sha1 = hashlib.sha1(obj).hexdigest()

    return sha1