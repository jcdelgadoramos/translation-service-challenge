# Translation Service Challenge

This project has been created by José Carlos Delgado as part of the application process for Aspire Technology.

The goal is to create a microservice providing a JSON API to work with word definitions/translations taken from Google Translate



## Completed tasks

 - Use of the following required technologies: Python 3, FastAPI in async mode, NoSQL database (Google Firestore).
 - Detail endpoint (as `/lookup/{source_lang}/{target_lang}/{word}` returning translations.
 - List endpoint (as `/list/{language}/?word=str&limit=10&page=1&desc=true` supporting pagination (`page` param, default = 1), sorting (`desc` param, default = true),  and filtering (`word` param). Added `limit` param.
 - Deletion endpoint (as `/delete/{language}/{word}/`). 
 - Dockerfile

## Pending tasks

 - docker-compose setup
 - Definitions, synonyms and example management. Requires targeting a different Google Cloud Translate client (currently working with v2)

## Wishlist

 - ~~Not restricted to a single source/target language~~ (done)
 - Unit tests
 - Firebase database name should be added as a configuration tool
 - GCP deployment

## Setup

 1. Requires a Google Cloud project with enabled Cloud Firestore API and Cloud Translation API, with an enabled Service Account that has been granted the Firebase Rules System and Cloud Translation API Admin roles at Permissions in the IAM Admin.
 2. A JSON key must be generated for the Service Account that will be used. This key should be stored somewhere in the host, whose location should be exported (in Linux, this would be done as `export GOOGLE_APPLICATION_CREDENTIALS="/home/user/location/of/credentials.json"`
 3. A native mode Firebase database named as `translation-service-challenge-db` should be created.
 4. `pip install -r requirements.txt`
 5. `fastapi dev main.py`. Project should be available at [localhost](http://127.0.0.1:8000)
