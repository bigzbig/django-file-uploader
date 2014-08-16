import os

def create_path_with_limit(id, limit=500):
    if not id:
        id = 0

    limit = int(limit)/2

    def _create_recursive_path(id, limit, path=[]):
        path.append(str((id % limit) + 1))
        p = id/limit
        if p > limit:
            path = _create_recursive_path(p, limit, path)
        return path
    path = _create_recursive_path(id, limit, [])
    return '/'.join(path)

def rm_empty_path(path):
    while len(os.listdir(path)) == 0:
        os.rmdir(path)
        path = os.path.dirname(path)