from flask import Flask
from flask_api import status
from datetime import datetime, timedelta
import logging
import requests
import yaml
import pytz


CONFIGURATION_FILE = "kisiowall-api.yaml"
config = None


app_api = Flask(__name__)


class KisioWallApiConfigLoad(Exception): pass


@app_api.route("/volume_call")
def get_volume_call():
    """
    Get volume http call per 30 minute.
    :return: json
    """
    content = None
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    datetime_24_hours_ago = datetime.now(tz=pytz.utc) - timedelta(hours=24)

    # Define data to post
    data = 'names[]=HttpDispatcher&from=%s&to=%s' % (datetime_24_hours_ago.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                                                     datetime.now(tz=pytz.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"))

    try:
        r = requests.get(config['url_newrelic'], headers=config['headers_newrelic'], params=data)

        if r.status_code == 200:
            content = r.text
            status_code = status.HTTP_200_OK

    except Exception as e:
        content = str(e)

    return content, status_code


@app_api.route("/volume_call_summarize")
def get_volume_call_summarize():
    """
    Get total http request from today 00:00:00.
    :return: json
    """
    content = None
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    datetime_24_hours_ago = datetime.now(tz=pytz.utc) - timedelta(hours=24)

    # Define data to post
    data = 'names[]=HttpDispatcher&from=%s&to=%s&summarize=true' % (datetime_24_hours_ago.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                                                                    datetime.now(tz=pytz.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"))

    try:
        r = requests.get(config['url_newrelic'], headers=config['headers_newrelic'], params=data)
        print(r.text)
        if r.status_code == 200:
            content = r.text
            status_code = status.HTTP_200_OK

    except Exception as e:
        content = str(e)

    return content, status_code


@app_api.route("/volume_errors")
def get_volume_errors():
    """
    Get volume errors from today at 00:00:00.
    :return: json
    """
    content = None
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    datetime_24_hours_ago = datetime.now(tz=pytz.utc) - timedelta(hours=24)

    # Define data to post
    data = 'names[]=Errors/all&from=%s&summarize=true' % datetime_24_hours_ago.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    try:
        r = requests.get(config['url_newrelic'], headers=config['headers_newrelic'], params=data)

        if r.status_code == 200:
            content = r.text
            status_code = status.HTTP_200_OK

    except Exception as e:
        content = str(e)

    return content, status_code


def app_logging(log_file, lvl=logging.INFO):
    """
    Write app log to file with specific format and log level
    :param log_file: File name where to write logs.
    :param lvl: Log level.
    """

    # Define format
    log_format = '[%(levelname)s] - %(asctime)s - %(message)s'
    log_date_format = '%m-%d-%Y %H:%M:%S'

    # Set logging method
    logging.basicConfig(format=log_format, level=lvl, datefmt=log_date_format, filename=log_file, filemode='a')


if __name__ == "__main__":
    # Load configuration file
    try:
        f = open(CONFIGURATION_FILE, 'r')
        config = yaml.load(f)
    except Exception as e:
        raise KisioWallApiConfigLoad(str(e))

    # Enable logs
    app_logging(config['log_file'])

    # Create access log for api call
    app_api.run(port=config['port'])
