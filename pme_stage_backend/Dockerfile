# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

CMD [ "flask", "run", "--host=0.0.0.0", "--port=5000"]