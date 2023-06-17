import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-not-pass'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://-:-@localhost/myflaskdb"
    MAILADRESS = ['testMail@example.com']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    SECRET_KEY = '-'
    OAUTH_CREDENTIALS = {
        'vk': {
            'id': '-',
            'secret': '-'
        }
    }
