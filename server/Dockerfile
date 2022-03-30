FROM node:16.14-alpine3.14 AS builder

WORKDIR /usr/app/client
COPY ./client /usr/app/client

RUN npm i
RUN npm run build

FROM python:3.10.4-alpine3.14

COPY app.py app.py
COPY requirements.txt requirements.txt
COPY --from=builder /usr/app/client/dist /client/dist

RUN pip install -r requirements.txt

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0" ]