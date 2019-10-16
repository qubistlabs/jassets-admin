import hashlib


def get_file_hash(filename):
    hash = hashlib.new('sha1')
    with open(filename, 'rb') as fp:
        hash.update(fp.read())
    return hash.hexdigest()

