FROM python:alpine

LABEL product.name         = fritzbox_exporter
LABEL product.maintainer   = "Mirco T"
LABEL product.default_port = 8765

EXPOSE 8765

## install build dependencies
RUN apk add --no-cache libxml2 libxslt
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libxml2-dev libxslt-dev

## install requirements
WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN python3 -m pip --no-cache-dir install -r requirements.txt

## cmd
CMD ["python3", "-m", "fritzbox_exporter"]