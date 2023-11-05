# Signum Explorer

apt install python3-dev default-libmysqlclient-dev build-essential redis-server supervisor pkg-config mariadb-server python3-venv
sudo mariadb-secure-installation
sudo mariadb
CREATE DATABASE IF NOT EXISTS explorer CHARACTER SET utf8;
CREATE USER IF NOT EXISTS 'explorer'@'localhost' IDENTIFIED BY 'ByjTFyabRJqAfg963KPx';
GRANT ALL PRIVILEGES ON explorer.* TO 'explorer'@'localhost';

CREATE DATABASE IF NOT EXISTS java_wallet CHARACTER SET utf8;
CREATE USER IF NOT EXISTS 'java_wallet'@'localhost' IDENTIFIED BY 'tE2CIhuv7Dowt49RI1zG';
GRANT ALL PRIVILEGES ON java_wallet.* TO 'java_wallet'@'localhost';
FLUSH PRIVILEGES;
QUIT;
python3 -m venv venv
. venv/bin/activate
pip install -U pip
pip install -r requirements.txt
mv .env.example .env
find . -path -maxdepth 3 "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path -maxdepth 3 "*/migrations/*.pyc"  -delete
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --database=java_wallet
gunicorn config.wsgi -c gunicorn.conf.py

For update SIGNA PRICE:
python3 manage.py tasks

This documentation is a work in progress. More details to follow.
<br>
<br>
<br>
<br>
<br>
## API Info
```json/SNRinfo/```                   Used to sync multiple explorers to the SNR master so they are all show the same info.<br>
```json/state/123.123.123.123```      Returns node state (ONLINE=1 UNREACHABLE=2 SYNC=3 STUCK=4 FORKED=5). <br>
```json/accounts/```                  Returns top 10 richest accounts. <br>
