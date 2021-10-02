import os
import urllib.parse as urlparse
import logging
from time import time, sleep

import psycopg2

def parse_database_url(url):
	if url is None:
		raise Exception(f"Expected a valid DATABASE_URL but received {url}")
	parsed_url = urlparse.urlparse(url)

	return {
		"dbname": parsed_url.path[1:],
		"user": parsed_url.username,
		"password": parsed_url.password,
		"host": parsed_url.hostname,
		"port": parsed_url.port
	}

check_timeout = os.getenv("POSTGRES_CHECK_TIMEOUT", 60)
check_interval = os.getenv("POSTGRES_CHECK_INTERVAL", 1)
interval_unit = "second" if check_interval == 1 else "seconds"

config = parse_database_url(os.getenv("DATABASE_URL"))

start_time = time()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def pg_isready(config):
    while time() - start_time < check_timeout:
        try:
            conn = psycopg2.connect(**config)
            logger.info("Postgres is ready! ✨ 💅")
            conn.close()
            return True
        except psycopg2.OperationalError:
            logger.info(f"Postgres isn't ready. Waiting for {check_interval} {interval_unit}...")
            sleep(check_interval)

    logger.error(f"We could not connect to Postgres within {check_timeout} seconds.")
    return False


pg_isready(config)
