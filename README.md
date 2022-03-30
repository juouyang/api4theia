# flask-restful-api for theia container

https://drive.google.com/file/d/13JaBX5NRyG7zzX2ajtHPEhRaFJYPHNMO/view?usp=sharing

## Prepare

```
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
./api4theia.py
```


## Test

```
cd api4theia/
python -m pytest
```


## Install systemd service

```
cd api4theia/scripts/
sudo bash install_systemd_services.sh
```


## Remove systemd service

```
cd api4theia/scripts/
sudo bash remove_systemd_services.sh
```
