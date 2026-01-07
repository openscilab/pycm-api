"""Application parameters and configurations."""

import os

PATH2DB = os.path.join(os.path.dirname(__file__), "DB.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{PATH2DB}"

PATH2CMS = os.path.join(os.path.dirname(__file__), "cms")
if not os.path.exists(PATH2CMS):
    os.makedirs(PATH2CMS)
PATH2REPORTS = os.path.join(os.path.dirname(__file__), "reports")
if not os.path.exists(PATH2REPORTS):
    os.makedirs(PATH2REPORTS)
PATH2PLOTS = os.path.join(os.path.dirname(__file__), "plots")
if not os.path.exists(PATH2PLOTS):
    os.makedirs(PATH2PLOTS)


PASSWORD_SALT = "pycm_salt"

USER_UID_LENGHT = 8
API_KEY_LENGTH = 32
CM_OBJECT_NAME_MAIN_LENGTH = 16

try:
    PYCM_ADMIN = os.environ['PYCM_API_ADMIN']
    PYCM_ADMIN_PASSWORD = os.environ['PYCM_API_ADMIN_PASSWORD']
except KeyError:
    raise KeyError("Environment variables PYCM_API_ADMIN and PYCM_API_ADMIN_PASSWORD must be set")
