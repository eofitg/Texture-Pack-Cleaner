import os

from utils import compare_tools as ct
from utils import config_reader as cr
from utils import operating_tools as ot
from utils import zip_tools as zt

necessary_message = True
building_message = False

keep_info = cr.get('keep_info')  # boolean
keep_hidden = cr.get('keep_hidden')  # boolean
whitelist = cr.get_path_list('whitelist')  # string list
blacklist = cr.get_path_list('blacklist')  # string list


# if or not this path only has one dir
# True -> return the path of this dir
# False -> return ""
def nest_check(path):
    count = False
    res_path = ""

    for item in os.scandir(path):

        # ignore hidden items
        if item.name.startswith('.'):
            continue

        # should not have any files
        if item.is_file():
            return ""

        # found dir
        else:
            if not count:
                count = True
                res_path = item.path

            # found another dir while has counted one
            else:
                return ""

    # return the only directory's path
    return res_path


def build(path, keep):
    # keep: if or not to force to keep file in this path, False means not
    # = True means some level of parent dir is in whitelist

    name = os.path.basename(path)  # with ext

    # priority: blacklist > keep_hidden > whitelist
    if name in blacklist:
        if building_message:
            print("  Found blacklist item at \"" + path + "\"")
            print("    Cleared.")
        return

    # hidden items check
    if name.startswith('.'):
        if building_message:
            print("  Found hidden item at \"" + path + "\"")
        if keep_hidden:
            ot.build(path)
            if building_message:
                print("    Retained as keep_hidden=" + str(keep_hidden))
        else:
            if building_message:
                print("    Cleared as keep_hidden=" + str(keep_hidden))
        return

    relative_path = ot.get_relative_path(path)
    original_path = ot.get_original_path(path)

    # whitelist check
    if relative_path in whitelist and not keep:
        keep = True

    # file or dir but no source can correspond
    if not os.path.exists(original_path):
        if building_message:
            print("  Found extra item at \"" + path + "\"")
        if not keep:
            if building_message:
                print("    Cleared.")
            return

    # check files
    if os.path.isfile(path):

        # whitelist file
        if keep:
            ot.build(path)
            if building_message:
                print("  Found whitelist file at \"" + path + "\"")
                print("    Retained.")

        # not in whitelist
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
                    if building_message:
                        print("  Found meaning json at \"" + path + "\"")
                        print("    Retained.")
                # same json
                else:
                    if building_message:
                        print("  Found meaningless json at \"" + path + "\"")
                    # if or not that this file is bind with a png
                    png_path = path[:-len(ext)]
                    # not exist = meaningless or just normal json
                    if os.path.exists(png_path):
                        ori_path = ot.get_original_path(png_path)
                        if os.path.exists(ori_path):
                            # Because .png needs .mcmeta to load rightly
                            # As long as a changed .png file exists,
                            # .mcmeta file has to be retained though it is unchanged
                            if not ct.comp_img(png_path, ori_path):
                                ot.build(path)
                                if building_message:
                                    print("  - with meaning pic at \"" + png_path + "\"")
                                    print("    Retained.")
                            else:
                                if building_message:
                                    print("  - with meaningless pic at \"" + png_path + "\"")
                                    print("    Cleared.")
                        else:
                            # not exist = may be meaningless png
                            # this file haven't been checked for whitelist by 'keep' so need a re-check
                            # json file also need to retain when its png is in the whitelist
                            rela_path = ot.get_relative_path(png_path)
                            if rela_path in whitelist:
                                ot.build(path)
                                if building_message:
                                    print("  - with whitelist pic at \"" + png_path + "\"")
                                    print("    Retained.")

            # PNG
            elif ext == '.png':
                # diff png
                if not ct.comp_img(path, original_path):
                    ot.build(path)
                    if building_message:
                        print("  Found meaning pic at \"" + path + "\"")
                        print("    Retained.")

                    # if changed static png to dynamic
                    json_path = path + '.mcmeta'
                    if os.path.exists(json_path):
                        # Known Bug: static png but with mcmeta with be identified as dynamic
                        ot.build(json_path)
                        if building_message:
                            print("  - with its custom json to dynamize at \"" + json_path + "\"")
                            print("    Retained.")
                # same png
                else:
                    if building_message:
                        print("  Found meaningless pic at \"" + path + "\"")
                    # if or not that this file is bind with a json
                    json_path = path + '.mcmeta'
                    # not exist = meaningless or just normal png
                    if os.path.exists(json_path):
                        ori_path = ot.get_original_path(json_path)
                        if os.path.exists(ori_path):
                            if not ct.comp_json(json_path, ori_path):
                                ot.build(path)
                                if building_message:
                                    print("  - with meaning json at \"" + json_path + "\"")
                                    print("    Retained.")
                            else:
                                if building_message:
                                    print("  - with meaningless json at \"" + json_path + "\"")
                                    print("    Cleared.")
                        else:
                            # not exist = may be meaningless json
                            # this file haven't been checked for whitelist by 'keep' so need a re-check
                            rela_path = ot.get_relative_path(json_path)
                            if rela_path in whitelist:
                                ot.build(path)
                                if building_message:
                                    print("  - with whitelist json at \"" + json_path + "\"")
                                    print("    Retained.")

            # other files
            else:
                if not ct.comp_txt(path, original_path):
                    ot.build(path)
                    if building_message:
                        print("  Found meaning txt at \"" + path + "\"")
                        print("    Retained.")
                else:
                    if building_message:
                        print("  Found meaningless txt at \"" + path + "\"")
                        print("    Cleared.")

    # check dirs
    elif os.path.isdir(path):

        # dir is empty
        if len(os.listdir(path)) == 0:

            # whitelist dir
            if keep:
                ot.build(path)
                if building_message:
                    print("  Found empty whitelist dir at \"" + path + "\"")
                    print("    Retained.")

            # not in whitelist
            else:
                if building_message:
                    print("  Found empty dir at \"" + path + "\"")
                    print("    Cleared.")

            return

        # dir is not empty
        if building_message:
            print("  Scanning dir at \"" + path + "\"")

        for item in os.scandir(path):
            build(item.path, keep)


def main():

    # clear output folder
    ot.clear_output()
    if building_message or necessary_message:
        print("Cleared output folder.")

    packs = ot.get_packs()
    for pack in packs:
        # ./input/{pack}
        pack_path = ot.get_pack_path(pack)
        pack_path_backup = pack_path
        if building_message or necessary_message:
            print("Building \"" + pack_path + "\" ......")

        # this pack may be nested like
        # ./input/XXX/{pack}
        # for this, recognize dirs with only 1 internal dir as a layer of nesting
        # (Not the best way, I know. BUT I AM TOO LAZY TO FIND A BETTER METHOD :///)
        if nest_check(pack_path) != "":
            pack_path = nest_check(pack_path)
            if building_message or necessary_message:
                print("Building nested dir \"" + pack_path + "\" ......")

        for item in os.scandir(pack_path):

            # assets dir has to be kept
            if item.is_dir() and item.name == "assets":
                continue

            # priority: blacklist > keep_hidden > keep_info > whitelist
            if item.name in blacklist:
                if building_message:
                    print("  Found blacklist item at \"" + item.path + "\"")
                    print("    Cleared.")
                continue

            # check hidden items
            if item.name.startswith('.') and keep_hidden:
                ot.build(item.path)
                if building_message:
                    print("  Found hidden item at \"" + item.path + "\"")
                    print("    Retained.")
                continue

            # check whitelist & keep info or not
            relative_path = ot.get_relative_path(item.path)
            # print("RELA: " + relative_path)
            if relative_path in whitelist or keep_info:
                ot.build(item.path)
                if building_message:
                    print("  Found item need to keep at \"" + item.path + "\"")
                    print("    Retained.")
                continue

            if building_message:
                print("  Found meaningless item at \"" + item.path + "\"")
                print("    Cleared.")

        # ./input/{pack}/assets
        build(os.path.join(pack_path, 'assets'), False)
        if building_message or necessary_message:
            print("Building \"" + os.path.join(pack_path, 'assets') + "\" ......")

        # Compress output
        zt.compress(ot.get_output_path(pack_path))
        if building_message or necessary_message:
            print("Compressed output files.")

        # Delete previously decompressed dirs in the "input" folder
        ot.delete_dir(ot.get_output_path(pack_path))
        ot.delete_dir(pack_path_backup)
        if building_message or necessary_message:
            print("Cleared extra files.")


if __name__ == '__main__':
    main()
    print("DONE.")
