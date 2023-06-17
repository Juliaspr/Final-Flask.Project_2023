import requests


def get_concate_username(token, user_id):
    data = {'user_id': user_id,
            'v': '5.92',
            'access_token': token,
            }

    user_info = requests.post('https://api.vk.com/method/users.get', data=data)

    if 'response' in user_info.json():
        user_info = user_info.json().get('response')[0]
        first_name, last_name = user_info['first_name'], user_info['last_name']
        return first_name + ' ' + last_name
    return None