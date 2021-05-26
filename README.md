# flask-restful-api for theia container


## Prepare

```
git clone https://github.com/juouyang-aicots/api4theia.git
cd api4theia/
python3 -m venv venv/
source venv/bin/activate
venv/bin/pip install -U pip
venv/bin/pip install -r requirements.txt
```


## Run

```
cd api4theia/
source venv/bin/activate
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(16))')
sudo --preserve-env=SECRET_KEY ./api4theia.py
```


## Test

```
cd api4theia/
python -m pytest
```


## Install as systemd service

```
cd api4theia/scripts/
bash install_systemd_services.sh
```