# ICPC_Challenges
judges algorithm tasks under ICPC rules

## Deploy

clone project into CTFd/CTFd/plugins/ **without** changing the project name

paste the following into CTFd/docker-compose.yml:

```yml
version: '3.5'

services:
  ctfd:
    build: .
    user: root
    restart: always
    ports:
      - "127.0.0.1:8000:8000"
    environment:
      - JUDGE_ADDR=judger
      - JUDGE_PORT=5000
      - JUDGE_TOKEN=mssc7f-t0ken_judg3r

      - UPLOAD_FOLDER=/var/uploads
      - DATABASE_URL=mysql+pymysql://root:NrlLbVn8UDa4g6h@ctfd_db/ctfd
      - REDIS_URL=redis://cache:6379
      - WORKERS=5
      - SECRET_KEY=&R3f!~0OVvnd^1023oijk#
      - LOG_FOLDER=/var/log/CTFd
      - ACCESS_LOG=-
      - ERROR_LOG=-
    volumes:
      - .data/CTFd/logs:/var/log/CTFd
      - .data/CTFd/uploads:/var/uploads
      - .:/opt/CTFd:ro
    depends_on:
      - ctfd_db
    networks:
      default:
      internal:

  ctfd_db:
    image: mariadb:10.4
    restart: always
    environment:
      - MYSQL_ROOT_PASSWORD=NrlLbVn8UDa4g6h
      - MYSQL_DATABASE=ctfd
    volumes:
      - .data/mysql:/var/lib/mysql
    networks:
      internal:
    # This command is required to set important mariadb defaults
    command: [mysqld, --character-set-server=utf8mb4, --collation-server=utf8mb4_unicode_ci, --wait_timeout=28800, --log-warnings=0]

  judger:
    image: frankli0324/judge_server:local
    environment:
      - JUDGE_DATADIR=/opt/data
      - JUDGE_BASEDIR=/opt/judger
      - JUDGE_TOKEN=mssc7f-t0ken_judg3r
      - DATABASE_URL=mysql+pymysql://root:grCS5LWYQR2zDVH@judger_db/judge?charset=utf8mb4
    volumes:
      - .data/CTFd/uploads:/opt/data
    depends_on:
      - judger_db
    networks:
      internal:

  judger_db:
    image: mariadb:10.4
    restart: always
    environment:
      - MYSQL_ROOT_PASSWORD=grCS5LWYQR2zDVH
      - MYSQL_DATABASE=judge
    volumes:
      - .data/mysql_judger:/var/lib/mysql
    networks:
      internal:
    # This command is required to set important mariadb defaults
    command: [mysqld, --character-set-server=utf8mb4, --collation-server=utf8mb4_unicode_ci, --wait_timeout=28800, --log-warnings=0]

  cache:
    image: redis:4
    restart: always
    volumes:
      - .data/redis:/data
    networks:
      internal:

networks:
  default:
  internal:
    internal: true
```

paste the following into CTFd/Dockerfile

```dockerfile
FROM python:3.7.3-alpine

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories
RUN apk update && \
    apk add linux-headers libffi-dev gcc make musl-dev python3-dev mysql-client git openssl-dev
RUN adduser -D -u 1001 -s /bin/bash ctfd

WORKDIR /opt/CTFd
RUN mkdir -p /opt/CTFd /var/log/CTFd /var/uploads

COPY requirements.txt .

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . /opt/CTFd

RUN for d in CTFd/plugins/*; do \
      if [ -f "$d/requirements.txt" ]; then \
        pip install -r $d/requirements.txt; \
      fi; \
    done;

RUN chmod +x /opt/CTFd/docker-entrypoint.sh
RUN chown -R 1001:1001 /opt/CTFd
RUN chown -R 1001:1001 /var/log/CTFd /var/uploads

USER 1001
EXPOSE 8000
ENTRYPOINT ["/opt/CTFd/docker-entrypoint.sh"]
```
