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
source venv/bin/activate
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(16))')
sudo --preserve-env=SECRET_KEY ./api4theia.py
```

## Test

```
python -m pytest
```


## Documentation

https://localhosts:5000/doc
