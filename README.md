# Signum Explorer

# Installation

## Prerequisites
### Linux (Debian 12)

```text
sudo apt install python3-dev default-libmysqlclient-dev build-essential redis-server pkg-config mariadb-server python3-venv wget unzip git
```

### Configure MariaDB
Creating databases for signum explorer and signum node. For the "node" database, we create two users: with one user "node_user" and with one read-only user "node_read only_user". "node_user" will be used in the signum node, and "node_read only_user" will be used in the signum explorer.

Replace "explorer_user password", 'node_user password' and 'node_readonly_user password' with their own values.

```text
sudo mariadb-secure-installation
```
```text
sudo mariadb
```

```text
CREATE DATABASE IF NOT EXISTS explorer CHARACTER SET utf8;
CREATE USER IF NOT EXISTS 'explorer_user'@'localhost' IDENTIFIED BY 'explorer_user password';
GRANT ALL PRIVILEGES ON explorer.* TO 'explorer_user'@'localhost';

CREATE DATABASE IF NOT EXISTS node CHARACTER SET utf8;
CREATE USER IF NOT EXISTS 'node_user'@'localhost' IDENTIFIED BY 'node_user password';
CREATE USER IF NOT EXISTS 'node_readonly_user'@'localhost' IDENTIFIED BY 'node_readonly_user password';
GRANT ALL PRIVILEGES ON signum.* TO 'node_user'@'localhost';
GRANT SELECT ON signum.* TO 'node_readonly_user'@'localhost';

FLUSH PRIVILEGES;
QUIT;
```

### INSTALL SIGNUM NODE:

https://github.com/signum-network/signum-node#installation

OR from root

```text
apt install openjdk-11-jre-headless
```

```text
adduser --system --no-create-home --group signum_node
```

```text
cat > /etc/systemd/system/signum-node.service << 'EOF'
[Unit]

    Description=Signum Node
    After=network.target
    Wants=network.target

[Service]

    ExecStart=/usr/bin/java -jar signum-node.jar -l
    WorkingDirectory=/opt/signum-node/
    User=signum_node
    Restart=always
    RestartSec=10

[Install]

    WantedBy=multi-user.target
EOF
```

```text
cat > /opt/update-signum.sh << 'EOF'
#!/bin/bash
if [ -z "$1" ]
    then
        echo "No parameters found. "
        exit 1
fi

cd /opt
rm -rf signum-node-v$1.zip
rm -rf signum-node-$1
wget https://github.com/signum-network/signum-node/releases/download/v$1/signum-node-v$1.zip
unzip signum-node-v$1.zip -d signum-node-$1

if [ -d "/opt/signum-node" ]; then
    cp /opt/signum-node/conf/node.properties signum-node-$1/conf/node.properties
    rm -rf /opt/signum-node_old
    mv /opt/signum-node /opt/signum-node_old
fi

mv signum-node-$1 /opt/signum-node
EOF
```

```text
systemctl enable signum-node.service
```

```text
chmod +x /opt/update-signum.sh
```

Change 3.7.2 to the current version of signum-node

```text
/opt/update-signum.sh 3.7.2
```

In file `/opt/signum-node/conf/node.properties`:
```properties
 DB.Url=jdbc:mariadb://localhost:3306/node
 DB.Username=node_user
 DB.Password="node_user password"
 DB.trimDerivedTables=false
```

```text
systemctl restart signum-node.service
```

A long synchronization procedure will begin. There is no need to wait for its completion and you can continue the installation.

### Install Django and configure DB

```text
sudo -i
cd /opt
git clone https://github.com/signum-network/signum-explorer
```

```text
cd signum-explorer
```

```text
python3 -m venv venv
```

```text
. venv/bin/activate
```

```text
pip install -U pip
```

```text
pip install -r requirements.txt
```

```text
cp .env.example .env
```

Generate SECRET_KEY:

```text
sed -i "s/NEED_SECRET_KEY/`python3 -c "import secrets; print(secrets.token_urlsafe())"`/g" .env
```

Delete old migration files and create new

```text
find . -maxdepth 3 -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -maxdepth 3 -path "*/migrations/*.pyc"  -delete
python manage.py makemigrations
```

```text
python manage.py migrate
```

Download missing static files:

```text
wget https://use.fontawesome.com/releases/v6.4.2/fontawesome-free-6.4.2-web.zip -P /tmp/
unzip /tmp/fontawesome-free-6.4.2-web.zip
mv fontawesome-free-6.4.2-web static/fontawesome-free-6.2.1-web
```

### Install Gunicorn for web access and Celery for running periodic tasks

```text
adduser --system --no-create-home --group celery
adduser --system --no-create-home --group gunicorn
```

```text
cat > /etc/tmpfiles.d/celery.conf << 'EOF'
d /run/celery 0755 celery celery -
d /var/log/celery 0755 celery celery -
EOF
```

```text
cat > /etc/tmpfiles.d/gunicorn.conf << 'EOF'
d /var/log/gunicorn 0755 gunicorn gunicorn -
EOF
```

```text
systemd-tmpfiles --create
```

```text
cat > /etc/default/gunicorn << 'EOF'
GUNICORN_BIN="/opt/signum-explorer/venv/bin/gunicorn"
WORKERS=8
LOG_FILE="/var/log/gunicorn/gunicorn.log"
BIND_HOST=127.0.0.1
BIND_PORT=5000
EOF
```

```text
cat > /etc/systemd/system/gunicorn.service << 'EOF'
[Unit]
Description=Gunicorn

[Service]
User=gunicorn
Group=gunicorn
EnvironmentFile=/etc/default/gunicorn
WorkingDirectory=/opt/signum-explorer
ExecStart=/bin/sh -c "${GUNICORN_BIN} \
    --workers=${WORKERS} \
    --log-file=${LOG_FILE} \
    --bind=${BIND_HOST}:${BIND_PORT} \
    config.wsgi:application"

[Install]
WantedBy=multi-user.target
EOF
```

```text
systemctl daemon-reload
systemctl enable --now gunicorn.service
```

```text
cat > /etc/default/celery << 'EOF'
CELERY_BIN="/opt/signum-explorer/venv/bin/celery"
CELERY_APP="config"
CELERYD_NODES="worker1"
CELERYD_PID_FILE="/run/celery/celery.pid"
CELERYD_LOG_FILE="/var/log/celery/celery.log"
CELERYD_LOG_LEVEL="debug"
CELERYD_OPTS="--time-limit=300 --concurrency=8"

CELERYBEAT_PID_FILE="/run/celery/beat.pid"
CELERYBEAT_LOG_FILE="/var/log/celery/beat.log"
CELERYBEAT_LOG_LEVEL="info"
CELERYBEAT_SCHEDULER_FILE="/run/celery/celerybeat-schedule"
EOF
```

```text
cat > /etc/systemd/system/celery.service << 'EOF'
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=celery
Group=celery
EnvironmentFile=/etc/default/celery
WorkingDirectory=/opt/signum-explorer
ExecStart=/bin/sh -c "${CELERY_BIN} -A ${CELERY_APP} multi start ${CELERYD_NODES} \
    --pidfile=${CELERYD_PID_FILE} --logfile=${CELERYD_LOG_FILE} \
    --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}"
ExecStop=/bin/sh -c "${CELERY_BIN} multi stopwait ${CELERYD_NODES} \
    --pidfile=${CELERYD_PID_FILE} --logfile=${CELERYD_LOG_FILE} \
    --loglevel=${CELERYD_LOG_LEVEL}"
ExecReload=/bin/sh -c "${CELERY_BIN} -A ${CELERY_APP} multi restart ${CELERYD_NODES} \
    --pidfile=${CELERYD_PID_FILE} --logfile=${CELERYD_LOG_FILE} \
    --loglevel=${CELERYD_LOG_LEVEL} $CELERYD_OPTS"

Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

```text
cat > /etc/systemd/system/celerybeat.service << 'EOF'
[Unit]
Description=Celery Beat Service
After=network.target

[Service]
Type=simple
User=celery
Group=celery
EnvironmentFile=/etc/default/celery
WorkingDirectory=/opt/signum-explorer
ExecStart=/bin/sh -c "${CELERY_BIN} -A ${CELERY_APP} beat  \
    --pidfile=${CELERYBEAT_PID_FILE} \
    --logfile=${CELERYBEAT_LOG_FILE} --loglevel=${CELERYBEAT_LOG_LEVEL} \
    -s ${CELERYBEAT_SCHEDULER_FILE}"
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

```text
systemctl daemon-reload
systemctl enable --now celery.service
systemctl enable --now celerybeat.service
```

### Install Nginx as proxy server

```text
apt install nginx certbot python3-certbot-nginx
```

```text
cat > /etc/nginx/conf.d/explorer.conf << 'EOF'
server {
    listen 80 default_server;
    server_name _;

    return 301 https://$host$request_uri;
}

server {
        listen 443 ssl;

        server_name CHANGE_ME;

        access_log  /var/log/nginx/explorer.log upstreamlog3 buffer=16k flush=10s;

  location / {
    proxy_pass http://127.0.0.1:5000/;
  }

  location /static {
    autoindex on;
    alias /opt/signum-explorer/static;
  }
}
EOF
```

```text
cat > /etc/nginx/conf.d/explorer.conf << 'EOF'
proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;

# Proxy Connection Settings
proxy_buffers 32 4k;
proxy_connect_timeout 240;
proxy_headers_hash_bucket_size 128;
proxy_headers_hash_max_size 1024;
proxy_http_version 1.1;
proxy_read_timeout 240;
proxy_redirect  http://  $scheme://;
proxy_send_timeout 240;

# Proxy Cache and Cookie Settings
proxy_cache_bypass $cookie_session;
proxy_no_cache $cookie_session;

# Proxy Header Settings
proxy_set_header Early-Data $ssl_early_data;
proxy_set_header Host $host;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto https;
proxy_set_header X-Real-IP $remote_addr;
EOF
```

```text
cat > /etc/nginx/nginx.conf << 'EOF'
user  nginx;
worker_processes  auto;

worker_cpu_affinity auto;
worker_rlimit_nofile 30000;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;

events {
    worker_connections  8192;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    log_format upstreamlog3 '[$time_local] $remote_addr - $remote_user - $server_name to: $upstream_addr: $request upstream_response_time $upstream_response_time msec $msec request_time $request_time';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    keepalive_timeout  65;
    server_tokens off;
    limit_req_zone $remote_addr zone=APIrLimit:10m rate=10r/s;

    gzip on;
    gzip_disable "msie6";
    gzip_comp_level 6;
    gzip_min_length 1100;
    gzip_buffers 16 8k;
    gzip_proxied any;
    gzip_types
        text/plain
        text/css
        text/js
        text/xml
        text/javascript
        application/javascript
        application/x-javascript
        application/json
        application/xml
        application/rss+xml3759204
        image/svg+xml;

    tcp_nodelay on;
    reset_timedout_connection on;

    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=all:64m inactive=2h max_size=2g;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    include /etc/nginx/conf.d/*.conf;
}
EOF
```

```text
systemctl daemon-reload
```

```text
systemctl enable --now nginx.service
```

```text
certbot --nginx
```

### About Celery and periodic tasks

In celery.py specifies three tasks:
"task_cmd" - to get price data and so on from CoinGecko
"peer_cmd_task" - to collect information about open source
"add_new_pools" - to fill in pool data

add_new_pool runs every 2 minutes. If the difference between the current block height in the Block table and the block height in the Pool table is greater than 1000 (the chunk variable), then the Pool table is filled with the value of the chunk variable so as not to heavily load the server.

It is recommended not to set chunk above 10000 (by increasing the task start interval), because the task will be executed for a long time.

<br>
<br>
<br>
<br>
<br>
## API Info
```json/SNRinfo/```                   Used to sync multiple explorers to the SNR master so they are all show the same info.<br>
```json/state/123.123.123.123```      Returns node state (ONLINE=1 UNREACHABLE=2 SYNC=3 STUCK=4 FORKED=5). <br>
```json/accounts/```                  Returns top 10 richest accounts. <br>
