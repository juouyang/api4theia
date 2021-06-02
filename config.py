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
    HELLO_TENSORFLOW = (
        "import tensorflow as tf\n"
        "mnist = tf.keras.datasets.mnist\n"
        "(x_train, y_train), (x_test, y_test) = mnist.load_data()\n"
        "x_train, x_test = x_train / 255.0, x_test / 255.0\n"
        "model = tf.keras.models.Sequential([\n"
        "    tf.keras.layers.Flatten(input_shape=(28, 28)),\n"
        "    tf.keras.layers.Dense(128, activation='relu'),\n"
        "    tf.keras.layers.Dropout(0.2),\n"
        "    tf.keras.layers.Dense(10)\n"
        "])\n"
        "predictions = model(x_train[:1]).numpy()\n"
        "predictions\n"
        "tf.nn.softmax(predictions).numpy()\n"
        "loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)\n"
        "loss_fn(y_train[:1], predictions).numpy()\n"
        "model.compile(optimizer='adam',\n"
        "    loss=loss_fn,\n"
        "    metrics=['accuracy'])\n"
        "model.fit(x_train, y_train, epochs=5)\n"
        "model.evaluate(x_test,  y_test, verbose=2)\n"
        "probability_model = tf.keras.Sequential([\n"
        "    model,\n"
        "    tf.keras.layers.Softmax()\n"
        "])\n"
        "probability_model(x_test[:5])\n"
    )
    HELLO_TALIB = (
        "import numpy as np\n"
        "import pandas as pd\n"
        "import talib\n"
        "all_ta_label = talib.get_functions()\n"
        "all_ta_groups = talib.get_function_groups()\n"
        "table = pd.DataFrame({\n"
        "    'TA-Lib Groups': list(all_ta_groups.keys()),\n"
        "    'Index Count': list(map(lambda x: len(x), all_ta_groups.values()))\n"
        "})\n"
        "print(table)\n"
    )
    HELLO_SCIPY = (
        "from scipy.interpolate import interp1d\n"
        "import pylab\n"
        "import numpy as np\n"
        "x = np.linspace(0, 5, 10)\n"
        "y = np.exp(x) / np.cos(np.pi * x)\n"
        "f_nearest = interp1d(x, y, kind='nearest')\n"
        "f_linear  = interp1d(x, y)\n"
        "f_cubic   = interp1d(x, y, kind='cubic')\n"
        "x2 = np.linspace(0, 5, 100)\n"
        "pylab.plot(x, y, 'o', label='data points')\n"
        "pylab.plot(x2, f_nearest(x2), label='nearest')\n"
        "pylab.plot(x2, f_linear(x2), label='linear')\n"
        "pylab.plot(x2, f_cubic(x2), label='cubic')\n"
        "pylab.legend()\n"
        "pylab.show()\n"
    )
    HELLO_STATSMODEL = (
        "import numpy as np\n"
        "import statsmodels.api as sm\n"
        "import statsmodels.formula.api as smf\n"
        "dat = sm.datasets.get_rdataset('Guerry', 'HistData').data\n"
        "results = smf.ols('Lottery ~ Literacy + np.log(Pop1831)', data=dat).fit()\n"
        "print(results.summary())\n"
    )
    HELLO_QUANDL = (
        "import quandl\n"
        "quandl.ApiConfig.api_key = 'tEsTkEy-123456789' # Get your access key from https://www.quandl.com\n"
        "data = quandl.get('NSE/OIL')\n"
        "print(data.head())\n"
        "data = quandl.get_table('ZACKS/FC', ticker='AAPL')\n"
        "print(data.head())\n"
    )
    HELLO_PYTORCH = (
        "import torch\n"
        "import matplotlib.pyplot as plt\n"
        "myTensor = torch.FloatTensor(7, 7)\n"
        "myTensor[:, :] = 0   # Assign zeros everywhere in the matrix.\n"
        "myTensor[3, 3] = 1   # Assign one in position 3, 3\n"
        "myTensor[:2, :] = 1   # Assign ones on the top 2 rows.\n"
        "myTensor[-2:, :] = 1    # Assign ones on the bottom 2 rows.\n"
        "plt.figure()\n"
        "plt.imshow(myTensor.numpy())\n"
        "plt.colorbar()\n"
        "plt.show()\n"
    )
    PACK_CMD = "curl -s https://raw.githubusercontent.com/juouyang-aicots/py2docker/main/build.sh | bash"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    API_PORT = 5000
    CONTAINER_PORT = 30000
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 0 # ERROR=40, https://docs.python.org/3/howto/logging.html#logging-levels
    FQDN = "pve.dev.net"
    CRT_FILE = 'app/ssl/pve.dev.net.crt'
    KEY_FILE = 'app/ssl/pve.dev.net.key'
    TEMPLATE_PROJECT = basedir + "/migrations/Doquant/Strategy"
    STORAGE_POOL = "/media/nfs/theia"
    MAX_CONTAINER_NUM = 100
    MAX_STRATEGY_NUM = 100


class TestingConfig(DevelopmentConfig):
    TESTING = True
    DB = 'Ram'
    API_PORT = 65000
    CONTAINER_PORT = 60000
    FQDN = 'localhost'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    API_PORT = 443
    CONTAINER_PORT = 30000
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 40 # ERROR=40, https://docs.python.org/3/howto/logging.html#logging-levels
    FQDN = "dost1.doquant.com"
    CRT_FILE = '/etc/letsencrypt/live/dost1.doquant.com/fullchain.pem'
    KEY_FILE = '/etc/letsencrypt/live/dost1.doquant.com/privkey.pem'
    TEMPLATE_PROJECT = basedir + "/migrations/Doquant/Strategy"
    STORAGE_POOL = "/media/aicots/ssd/theia"
    MAX_CONTAINER_NUM = 3
    MAX_STRATEGY_NUM = 100


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,

    'default': DevelopmentConfig
}
