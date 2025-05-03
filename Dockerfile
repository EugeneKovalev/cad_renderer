FROM python:3.9.14-alpine3.16

RUN apk add --no-cache \
# installs gcc which is required for Cairo
    build-base \
# installs Cairo stuffcurl
    cairo-dev cairo cairo-tools

COPY ./requirements.txt /var/tmp/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /var/tmp/requirements.txt

WORKDIR /app

# ✅ This copies all your app code (including run.py) into /app
COPY . .

# Optional but recommended: set the default command
CMD ["python", "run.py"]
