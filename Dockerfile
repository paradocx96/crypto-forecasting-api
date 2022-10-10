FROM python:3.9

WORKDIR /crypto-forecasting-api

ENV FLASK_ENV=development

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]