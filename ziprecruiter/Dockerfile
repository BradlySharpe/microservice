FROM python:3.9-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./dist/
EXPOSE 8080
CMD [ "python", "./dist/main.py" ]
