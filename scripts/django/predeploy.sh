#!/bin/bash

cd /app

python3 manage.py collectstatic --noinput
