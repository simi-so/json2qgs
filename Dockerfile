FROM python:3.9


ADD . /srv/json2qgs

RUN pip3 install --no-cache-dir -r /srv/json2qgs/requirements.txt \
    && chmod -R u+x /srv/json2qgs/* \
    && chown -R 1001:0 /srv/json2qgs

RUN apt-get update && apt-get -y install locales

RUN localedef -c -i de_CH -f UTF-8 de_CH.UTF-8 && \
    localedef -c -i fr_CH -f UTF-8 fr_CH.UTF-8 && \
    localedef -c -i it_CH -f UTF-8 it_CH.UTF-8

# switch to non-root for openshift usage
USER 1001

CMD [ "/bin/bash" ]
