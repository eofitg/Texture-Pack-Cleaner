import os
import shutil
from utils import config_reader as cr
import utils.zip_tools as zt

input_path = cr.get('path.input_path')
output_path = cr.get('path.output_path')
original_path = cr.get('path.original_path')
version = cr.get('version')


def clear_output():
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        return
    if len(os.listdir(output_path)) != 0:
        delete_dir(output_path)
        os.makedirs(output_path)


def delete_dir(dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)


# dst: parent folder path
def copy_file(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    shutil.copy(src, dst)


# dst: this folder path
def copy_dir(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


# Copy this file / dir to dst path
def copy(src, dst):
    s = str(src)
    if s.endswith(os.sep):
        s = src[:-1]

    name = os.path.basename(s)
    if os.path.isdir(s):  # folder
        copy_dir(src, dst)
    elif os.path.isfile(s):  # file
        copy_file(src, dst[:-len(name)])


# Add this file / dir from 'input' to 'output'
def build(src):
    copy(src, get_output_path(src))


# Turn input_path into output_path (No '/' at the end of path)
def get_output_path(path):
    return os.path.join(output_path, path[len(input_path):])


# Turn root path into the certain relative path in a pack (for whitelist check)
def get_relative_path(path):
    parts = path.split(os.sep)
    _from = 0
    for i in range(0, len(parts)):
        if parts[i] == 'assets' or parts[i].startswith("pack."):
            _from = i
            break
    rela = parts[_from]
    for i in range(_from + 1, len(parts)):
        rela = os.path.join(rela, parts[i])
    return rela


# Get pack list
def get_packs():
    dirs = []

    for item in os.scandir(input_path):

        raw_name, ext = os.path.splitext(item.name)

        if item.is_dir():
            dirs.append(os.path.basename(item.path))

        elif item.is_file() and ext == '.zip':
            # decompress .zip files
            zt.decompress(item.path)
            dirs.append(raw_name)

    return list(set(dirs))


# Get pack path by pack name
def get_pack_path(pack):
    return os.path.join(input_path, pack)


# Get original texture path by version and certain dir path
def get_original_path(path):
    return os.path.join(original_path, version, get_relative_path(path))
