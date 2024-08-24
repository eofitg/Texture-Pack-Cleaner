import os
from utils import config_reader as cr

from PIL import Image
import numpy as np
import json
from deepdiff import DeepDiff

detail_message = False
test = False
test_path = cr.get('path.test_path')


def read_file(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()


def preprocess(s):
    # remove ' '
    ret = s.replace(' ', '')
    # turn '\n' into ' '
    ret = ret.replace('\n', ' ')
    return ret


# .lang / .fsh / .txt / etc.
def comp_txt(p1, p2):
    if detail_message:
        print('  TXT:' + p1)
    s1 = read_file(p1)
    s2 = read_file(p2)
    return preprocess(s1) == preprocess(s2)


# for test output img
def save_test_img(img, p):
    tp = os.path.join(test_path, p)
    if not os.path.exists(tp[:-len(os.path.basename(tp))]):
        os.makedirs(tp[:-len(os.path.basename(tp))])
    img.save(tp)


# .png
def comp_img(p1, p2):
    if detail_message:
        print('  IMG:' + p1)

    img1 = Image.open(p1).convert('RGBA')
    img2 = Image.open(p2).convert('RGBA')
    if img1.size != img2.size:
        return False

    np1 = np.array(img1)
    np2 = np.array(img2)

    if test and np.array_equal(np1, np2):
        save_test_img(img1, p1)
        save_test_img(img2, p2)

    return np.array_equal(np1, np2)


def save_test_json(js, p):
    tp = os.path.join(test_path, p)
    if not os.path.exists(tp[:-len(os.path.basename(tp))]):
        os.makedirs(tp[:-len(os.path.basename(tp))])
    with open(tp, 'w', encoding='utf-8') as f:
        json.dump(js, f, indent=4, ensure_ascii=False)


# .json / .mcmeta
def comp_json(p1, p2):
    if detail_message:
        print('  JSON:' + p1)

    j1 = json.loads(read_file(p1))
    j2 = json.loads(read_file(p2))

    diff = DeepDiff(j1, j2, ignore_order=True)

    if test and not diff:
        save_test_json(j1, p1)
        save_test_json(j2, p2)

    return not diff
