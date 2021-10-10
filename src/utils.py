from datetime import datetime

def flatten(list):
    flat_list = []
    for sublist in list:
        for item in sublist:
            flat_list.append(item)

    return flat_list


def clean_name(name, role):
    cleaned_name = name
    if role in name:
        cleaned_name = name.replace(
            '(' + role + ')', '')

    return cleaned_name


def clean_role(role, name):
    cleaned_role = role
    if name in role:
        cleaned_role = role.replace(name, '')

    return cleaned_role

def convert_time(time):
    if time == 'NA':
        return time
    hour, minute = time.split('h')
    data_ISO = datetime.now().replace(
        hour=int(hour), minute=int(minute), second=0, microsecond=0).isoformat()

    return data_ISO