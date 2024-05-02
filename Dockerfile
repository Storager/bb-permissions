FROM python:3.12
ADD requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
WORKDIR /app
COPY ./scripts /app/
ENTRYPOINT [ "/usr/local/bin/python", "./bb_permissions.py" ]