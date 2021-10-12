def readFile(path):
    """Read contents of file at given path as bytes."""
    with open(path, 'rb') as f:
        return f.read()


def writeFile(path, data):
    """Write data bytes to file at given path."""
    with open(path, 'wb') as f:
        f.write(data)