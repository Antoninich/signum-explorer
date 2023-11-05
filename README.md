# Signum Explorer

# Installation

## Prerequisites
### Linux (Debian 12)

`sudo apt install python3-dev default-libmysqlclient-dev build-essential redis-server supervisor pkg-config mariadb-server python3-venv`

### Configure MariaDB

`sudo mariadb-secure-installation`

`sudo mariadb`

```text
CREATE DATABASE IF NOT EXISTS explorer CHARACTER SET utf8;
CREATE USER IF NOT EXISTS 'explorer'@'localhost' IDENTIFIED BY 'ByjTFyabRJqAfg963KPx';
GRANT ALL PRIVILEGES ON explorer.* TO 'explorer'@'localhost';

CREATE DATABASE IF NOT EXISTS signum CHARACTER SET utf8;
CREATE USER IF NOT EXISTS 'signum_user'@'localhost' IDENTIFIED BY 'tE2CIhuv7Dowt49RI1zG';
GRANT ALL PRIVILEGES ON signum.* TO 'signum_user'@'localhost';

FLUSH PRIVILEGES;
QUIT;
```

### INSTALL SIGNUM NODE:

https://github.com/signum-network/signum-node#installation

In file `node.properties`:
```properties
 DB.Url=jdbc:mariadb://localhost:3306/signum
 DB.Username=signum_user
 DB.Password=tE2CIhuv7Dowt49RI1zG
```

### Install Django and configure DB

`python3 -m venv venv`

`. venv/bin/activate`

`pip install -U pip`

`pip install -r requirements.txt`

`cp .env.example .env`

`find . -path -maxdepth 3 "*/migrations/*.py" -not -name "__init__.py" -delete`

`find . -path -maxdepth 3 "*/migrations/*.pyc"  -delete`

`python manage.py makemigrations`

`python manage.py migrate`

`gunicorn config.wsgi -c gunicorn.conf.py`

For update SIGNA PRICE:

`python3 manage.py tasks`

For update PEERS:

`python3 manage.py peers`

NOTE:

DB "java_wallet" is node DB

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
