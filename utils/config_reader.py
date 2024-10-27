import yaml


with open('./config.yaml', 'r', encoding="utf-8") as f:
    config = yaml.safe_load(f)


def get(key_list):
    value = config
    keys = key_list.split('.')
    for key in keys:
        value = value[key]
    return value


def get_path_list(key_list):
    value = list(get(key_list))
    for s in value:
        if s.replace('/', '\\') == s:
            continue

        value.append(str(s).replace('/', '\\'))

    return value
