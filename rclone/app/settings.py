import os

# Flask settings
HOST = os.environ.get("HOST","0.0.0.0")
PORT = os.environ.get("PORT", 80)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "ERROR")
SERVER_URL = os.environ.get("SERVER_URL", "http://localhost:{}".format(PORT))
BASE_PATH = "/" + os.environ.get("BASE_PATH", "")
ADMIN_CONFIG_FILE = os.environ.get("ADMIN_CONFIG_FILE", "/etc/rclone.conf")
USERS_CONFIG_PATH = os.environ.get("USERS_CONFIG_PATH", "/usr/local/etc")

# API Settings
API_KEY = 'X-API-KEY'
API_VERSION = "1.0"
API_TITLE = 'rClone config API'
API_DESCRIPTION = 'API Service to store rClone config to Vault'

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
SWAGGER_VALIDATOR_URL = os.environ.get("SWAGGER_VALIDATOR_URL", "{}/validator".format(SERVER_URL))
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# Vault settings
VAULT_ADDR = os.environ.get('VAULT_ADDR', 'http://localhost:8200')
VAULT_TOKEN = os.environ.get('VAULT_TOKEN', None)

# If no VAULT_TOKEN is provided, then the module tries to authenticate with User/Pass
VAULT_USER = os.environ.get('VAULT_USER', 'admin')
VAULT_PASS = os.environ.get('VAULT_PASS', 'secret')

# RClone Config
RCLONE_ADMIN_CONFIG = os.environ.get('RCLONE_ADMIN_CONFIG', '/etc/rclone.conf')
CACHE_DIR = os.environ.get('CACHE_DIR', '/tmp')

# PAM Settings
PAM_VALIDATE_ADMIN = os.environ.get('PAM_VALIDATE_ADMIN', '')
PAM_VALIDATE_USERS = os.environ.get('PAM_VALIDATE_USERS', '')
