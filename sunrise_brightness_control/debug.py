from config import config

def debug(message):
    if config['v']:
        print('debug: ' + message)
