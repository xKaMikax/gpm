import os
import stat
import pwd
import grp
import argparse
from datetime import datetime

def get_permissions(mode):
    file_type = 'd' if stat.S_ISDIR(mode) else '-'
    perms_map = [
        (stat.S_IRUSR, 'r'), (stat.S_IWUSR, 'w'), (stat.S_IXUSR, 'x'),
        (stat.S_IRGRP, 'r'), (stat.S_IWGRP, 'w'), (stat.S_IXGRP, 'x'),
        (stat.S_IROTH, 'r'), (stat.S_IWOTH, 'w'), (stat.S_IXOTH, 'x'),
    ]
    permissions_str = ''.join(p[1] if mode & p[0] else '-' for p in perms_map)
    return file_type + permissions_str

def list_directory(long_format=False, path='.'):
    try:
        items = sorted([f for f in os.listdir(path) if not f.startswith('.')])
    except OSError as e:
        print(f"Error: {e}")
        return

    if not long_format:
        print("  ".join(items))
        return

    for item in items:
        full_path = os.path.join(path, item)
        stats = os.lstat(full_path)
        
        mode = get_permissions(stats.st_mode)
        links = stats.st_nlink
        user = pwd.getpwuid(stats.st_uid).pw_name
        group = grp.getgrgid(stats.st_gid).gr_name
        size = stats.st_size
        
        mtime = datetime.fromtimestamp(stats.st_mtime)
        time_str = mtime.strftime('%b %d %H:%M')

        print(f"{mode} {links:2} {user} {group} {size:8} {time_str} {item}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", action="store_true")
    parser.add_argument("path", nargs="?", default=".")
    
    args = parser.parse_args()
    list_directory(long_format=args.l, path=args.path)
