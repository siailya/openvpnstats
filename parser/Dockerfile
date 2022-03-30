FROM python:3.8.13-buster

COPY main.py main.py
COPY OVPNInterface.py OVPNInterface.py
COPY requirements.txt requirements.txt


RUN pip install -r requirements.txt

EXPOSE 5555

CMD [ "python3", "-m", "main" ]