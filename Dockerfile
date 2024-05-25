# 
FROM python:3.12

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt
COPY ./credentials.json /code/credentials.json

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
ENV GOOGLE_APPLICATION_CREDENTIALS=/code/credentials.json

# 
COPY ./ /code/app

# 
CMD ["fastapi", "run", "app/main.py", "--port", "80"]