FROM python:3.9.16

RUN apt update && apt install vim -y
RUN pip install -r requirements.txt

WORKDIR /app
COPY . /app

ENV GOOGLE_APPLICATION_CREDENTIALS=slack_ai

EXPOSE 80

CMD ["python", "main.py"]