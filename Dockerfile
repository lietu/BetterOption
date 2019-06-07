FROM python:3.7-alpine3.9

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PATH=/usr/local/bin:$PATH

ADD . /src
WORKDIR /src

RUN chmod +x *.sh \
 && sh docker_setup.sh

# Sleep forever, terminate quickly when asked to
CMD exec /bin/sh -c "trap : TERM INT; (while true; do sleep 1000; done) & wait"
