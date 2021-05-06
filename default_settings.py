TESTING = False
DEBUG = False
CRT_FILE = 'ssl/dev.net.crt'
KEY_FILE = 'ssl/dev.net.key'
LOG_LEVEL = 40 # ERROR=40, https://docs.python.org/3/howto/logging.html#logging-levels
THEIA_ROOT = "/media/nfs/theia"
THEIA_PORT = 30000
STRATEGY_TEMPLATE = "/root/builds/Doquant/Strategy"
DOCKER_IMAGE = "theia-python:aicots"
DOCKER_HOST = "pve.dev.net"
PACK_CMD = "curl -s https://raw.githubusercontent.com/juouyang-aicots/py2docker/main/build.sh | bash"
RUNNING_THEIA_PER_USER = 3
MAX_STRATEGY_NUM = 100
GIT_IGNORE = '''
/.pytest_cache/
__pycache__/
*.py[cod]
/venv/
/.vscode/
**/log
**/.theia
**/.sandbox
**/.Trash*
'''
GIT_INIT = "git init;git config user.email 'root@local';git add ./*;git add .gitignore;git commit -m 'first commit'"