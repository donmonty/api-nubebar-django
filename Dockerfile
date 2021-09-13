FROM python:3.9-alpine3.13
LABEL maintainer="Nubebar"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./app /app
COPY ./scripts /scripts

WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    apk add --update --no-cache postgresql-client jpeg-dev
#RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-deps \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN /py/bin/pip install -r /requirements.txt && \
    apk del .tmp-deps && \
    adduser --disabled-password --no-create-home app && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R app:app /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts
#RUN pip install -r /requirements.txt
#RUN apk del .tmp-build-deps

RUN apk update && \
    apk upgrade && \
    apk add --no-cache libstdc++ && \
    apk add --no-cache --virtual=build_deps g++ gfortran && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    /py/bin/pip install --no-cache-dir pandas && \
    rm /usr/include/xlocale.h && \
    apk del build_deps

ENV PATH="/scripts:/py/bin:$PATH"
USER app

CMD ["run.sh"]
#RUN mkdir /app
#WORKDIR /app
#COPY ./app /app

#RUN adduser -D user
#USER user
