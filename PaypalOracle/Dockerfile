FROM python:alpine3.17
WORKDIR /oracle
COPY ./oracle /oracle
RUN apk update && apk add python3-dev gcc libc-dev
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "main.py", "${CONTRACT_ADDRESS}"]
