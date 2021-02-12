FROM python:3.7

WORKDIR /AWS_Covid

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./app ./app

CMD ["python" , "./app/application.py"]