FROM python:3.9


ADD . /srv/json2qgs

RUN pip3 install --no-cache-dir -r /srv/json2qgs/requirements.txt \
    && chmod -R u+x /srv/json2qgs/* \
    && chown -R 1001:0 /srv/json2qgs

ENV LC_ALL C.UTF-8

# switch to non-root for openshift usage
USER 1001

CMD [ "/bin/bash" ]
