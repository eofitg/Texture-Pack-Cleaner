import os

from utils import compare_tools as ct
from utils import config_reader as cr
from utils import operating_tools as ot
from utils import zip_tools as zt

building_message = True
keep_info = cr.get('keep_info')  # boolean
keep_hidden = cr.get('keep_hidden')  # boolean
whitelist = cr.get('whitelist')  # string list
blacklist = cr.get('blacklist')  # string list


def build(path, keep):
    # keep: if or not to force to keep file in this path, False means not
    # = True means some level of parent dir is in whitelist
    name = os.path.basename(path)  # with ext
    if name.startswith('.'):
        if keep_hidden:
            ot.build(path)
        return
    # priority: blacklist > whitelist
    if name in blacklist:
        return

    relative_path = ot.get_relative_path(path)
    original_path = ot.get_original_path(path)
    if relative_path in whitelist and not keep:
        keep = True
    if not os.path.exists(original_path) and not keep:
        return

    if os.path.isfile(path):
        if keep:
            ot.build(path)
        else:
            # match file if or not the same as original
            # same -> meaningless -> ignore
            # different -> build
            file = os.path.basename(path)
            _, ext = os.path.splitext(file)
            # JSON or MCMETA
            if ext == '.json' or ext == '.mcmeta':
                # diff json
                if not ct.comp_json(path, original_path):
                    ot.build(path)
                # same json
                else:
                    # if or not that this file is bind with a png
                    png_path = path[:-len(ext)]
                    # not exist = meaningless or just normal json
                    if os.path.exists(png_path):
                        ori_path = ot.get_original_path(png_path)
                        if os.path.exists(ori_path):
                            if not ct.comp_img(png_path, ori_path):
                                ot.build(path)
                                if building_message:
                                    print("  DIFF-PNG:" + png_path + " WITH")
                            else:
                                if building_message:
                                    print("  SAME-PNG:" + png_path + " WITH")
                        else:
                            # not exist = may be meaningless png
                            # this file haven't been checked for whitelist by 'keep' so need a re-check
                            rela_path = ot.get_relative_path(png_path)
                            if rela_path in whitelist:
                                ot.build(path)
                                if building_message:
                                    print("  WL-PNG:" + png_path + " THO")
                    if building_message:
                        print("  SAME-JSON:" + path)

            # PNG
            elif ext == '.png':
                # diff png
                if not ct.comp_img(path, original_path):
                    ot.build(path)
                    # if changed static png to dynamic
                    json_path = path + '.mcmeta'
                    if os.path.exists(json_path):
                        # Known Bug: static png but with mcmeta with be identified as dynamic
                        ot.build(json_path)
                        if building_message:
                            print("  DYNAMIZED-STATIC-PNG:" + path + " CONFIG IN")
                            print("  " + json_path)
                # same png
                else:
                    # if or not that this file is bind with a json
                    json_path = path + '.mcmeta'
                    # not exist = meaningless or just normal png
                    if os.path.exists(json_path):
                        ori_path = ot.get_original_path(json_path)
                        if os.path.exists(ori_path):
                            if not ct.comp_json(json_path, ori_path):
                                ot.build(path)
                                if building_message:
                                    print("  DIFF-JSON:" + json_path + " WITH")
                            else:
                                if building_message:
                                    print("  SAME-JSON" + json_path + " WITH")
                        else:
                            # not exist = may be meaningless json
                            # this file haven't been checked for whitelist by 'keep' so need a re-check
                            rela_path = ot.get_relative_path(json_path)
                            if rela_path in whitelist:
                                ot.build(path)
                                if building_message:
                                    print("  WL-JSON:" + json_path + " THO")
                    if building_message:
                        print("  SAME-PNG:" + path)

            # else files
            else:
                if not ct.comp_txt(path, original_path):
                    ot.build(path)
                else:
                    if building_message:
                        print("  SAME-TXT:" + path)

    elif os.path.isdir(path):
        if len(os.listdir(path)) == 0:  # dir is empty
            if keep:
                ot.build(path)
            return

        for item in os.scandir(path):
            build(item.path, keep)


def main():

    # clear output folder
    ot.clear()

    packs = ot.get_packs()
    for pack in packs:
        # ./input/{pack}
        pack_path = ot.get_pack_path(pack)
        if building_message:
            print('Building ' + pack_path + ' ......')

        for item in os.scandir(pack_path):
            # print('FILE_PATH:' + file.path)
            # check hidden items
            if item.name.startswith('.') and keep_hidden:
                ot.build(item.path)
                continue

            # check whitelist
            relative_path = ot.get_relative_path(item.path)
            if relative_path in whitelist or keep_info:
                ot.build(item.path)

        # ./input/{pack}/assets
        build(os.path.join(pack_path, 'assets'), False)

        zt.compress(ot.get_output_path(pack_path))
        ot.del_dir(ot.get_output_path(pack_path))
        ot.del_dir(pack_path)


if __name__ == '__main__':
    main()
    print("DONE.")
