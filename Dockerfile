FROM python:3.9-slim
COPY requirements.txt /bot/requirements.txt
WORKDIR /bot
RUN pip install -r requirements.txt
COPY . /bot
CMD ["python3", "main.py"]