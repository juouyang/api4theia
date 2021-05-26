import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DB = 'Json'
    SECRET_KEY = os.environ.get("SECRET_KEY") or '85114481'
    DOCKER_IMAGE = "theia-python:aicots"
    GIT_IGNORE = (
        "/.pytest_cache/\n"
        "__pycache__/\n"
        "*.py[cod]\n"
        "/venv/\n"
        "/.vscode/\n"
        "**/log*\n"
        "**/.theia\n"
        "**/.sandbox\n"
        "**/.Trash*\n"
    )
    GIT_INIT = "git init;git config user.email 'root@local';git add ./*;git add .gitignore;git commit -m 'first commit'"
    HELLO_MATPLOTLIB = (
        "import matplotlib\n"
        "import matplotlib.pyplot as plt\n"
        "import numpy as np\n"
        "t = np.arange(0.0, 2.0, 0.01)\n"
        "s = 1 + np.sin(2 * np.pi * t)\n"
        "fig, ax = plt.subplots()\n"
        "ax.plot(t, s)\n"
        "ax.set(xlabel='time (s)', ylabel='voltage (mV)', title='About as simple as it gets, folks')\n"
        "ax.grid()\n"
        "fig.savefig(\"plot.png\")\n"
    )
    HELLO_PLOTLY = (
        "import plotly.graph_objects as go\n"
        "import pandas as pd\n"
        "from datetime import datetime\n"
        "df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')\n"
        "fig = go.Figure(data=[go.Candlestick(x=df['Date'],\n"
        "               open=df['AAPL.Open'],\n"
        "                high=df['AAPL.High'],\n"
        "                low=df['AAPL.Low'],\n"
        "                close=df['AAPL.Close'],\n"
        "                increasing_line_color= 'red',\n"
        "                decreasing_line_color= 'green')])\n"
        "fig.update_layout(hovermode='x')\n"
        "fig.show()\n"
    )
    HELLO_TENSORFLOW = '''
import tensorflow as tf
mnist = tf.keras.datasets.mnist

(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(10)
])
predictions = model(x_train[:1]).numpy()
predictions
tf.nn.softmax(predictions).numpy()
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
loss_fn(y_train[:1], predictions).numpy()
model.compile(optimizer='adam',
              loss=loss_fn,
              metrics=['accuracy'])
model.fit(x_train, y_train, epochs=5)
model.evaluate(x_test,  y_test, verbose=2)
probability_model = tf.keras.Sequential([
    model,
    tf.keras.layers.Softmax()
])
probability_model(x_test[:5])
'''
    PACK_CMD = "curl -s https://raw.githubusercontent.com/juouyang-aicots/py2docker/main/build.sh | bash"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    API_PORT = 5000
    CONTAINER_PORT = 30000
    WTF_CSRF_ENABLED = True
    LOG_LEVEL = 0 # ERROR=40, https://docs.python.org/3/howto/logging.html#logging-levels
    FQDN = "pve.dev.net"
    CRT_FILE = 'app/ssl/pve.dev.net.crt'
    KEY_FILE = 'app/ssl/pve.dev.net.key'
    TEMPLATE_PROJECT = "/root/builds/Doquant/Strategy"
    STORAGE_POOL = "/media/nfs/theia"
    MAX_CONTAINER_NUM = 100
    MAX_STRATEGY_NUM = 100


class TestingConfig(DevelopmentConfig):
    TESTING = True
    DB = 'Ram'
    API_PORT = 65000
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    API_PORT = 443
    CONTAINER_PORT = 30000
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 40 # ERROR=40, https://docs.python.org/3/howto/logging.html#logging-levels
    FQDN = "dost1.doquant.com"
    CRT_FILE = '/etc/letsencrypt/live/dost1.doquant.com/fullchain.pem'
    KEY_FILE = '/etc/letsencrypt/live/dost1.doquant.com/privkey.pem'
    TEMPLATE_PROJECT = "/home/aicots/builds/Doquant/Strategy"
    STORAGE_POOL = "/media/aicots/ssd/theia"
    MAX_CONTAINER_NUM = 3
    MAX_STRATEGY_NUM = 100


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
