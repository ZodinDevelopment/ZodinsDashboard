import os
import secrets
# create global var for the absolute path to the app's top level dir
basedir = os.path.abspath(os.path.dirname(__file__))


# create a class for the app to configure on startup
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe()
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['dmgarrett72@protonmail.com', 'michael.landon@zodin.dev']
    POSTS_PER_PAGE = 25
    MEDIA_PER_PAGE = 5
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    IMAGE_EXTENSIONS = ['jpg', 'png', 'gif']
    VIDEO_EXTENSIONS = ['mp4', 'mov', 'webm']
    with open(os.path.join(basedir, 'about.txt'), 'r') as f:
        ABOUT_TEXT = f.read()    
