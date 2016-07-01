from flask import Flask
from flask_api import status
from datetime import datetime, timedelta
import logging
import requests
import yaml
import pytz
import redis


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

def make_request(uri, **querystring_params):
  headers = {"X-Client-Key": config['apikey_appfigures']}
  auth =(config['username_appfigures'], config['password_appfigures'])
  return requests.get(config['url_appfigures'] + uri.lstrip("/"),
                        auth=auth,
                        params=querystring_params,
                        headers=headers)


@app_api.route("/downloads_by_store")
def get_downloads_by_store():
    """
    Get number of downloads of all our apps each day.
    :return: json
    """
    content = None
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    content =  {'google_play': '233875' , 'ios_store': '491488' }


    """
    try:
        if (datetime.now - timedelta(hours=1)) > last_cache_update:
            try:
                dl_response = make_request("/reports/sales/?group_by=store")

                if dl_response.status_code == 200:
                    content =  {'google_play': dl_response.json()['google_play']['downloads'],
                             'ios_store': dl_response.json()['apple:ios']['downloads']}
                    status_code = status.HTTP_200_OK
                    cache_connexion = redis.Redis(connection_pool=pool)
                    cache_connexion.set('dlbyapp', content)
                    last_cache_update = datetime.now()
            except Exception as e:
                content = str(e)
        else:
            cache_connexion = redis.Redis(connection_pool=pool)
            content = cache_connexion.get('dlbyapp')
    except Exception as e:
        content = str(e)
    """

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

    # Set connection to Redis cache db
    """pool = redis.ConnectionPool(host=config['host_relis'], port=config['port_relis'], db=0)
    last_cache_update = datetime.now()"""

    # Create access log for api call
app_api.run(port=config['port'])