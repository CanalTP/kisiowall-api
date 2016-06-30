from flask import Flask
import logging

app_api = Flask(__name__)

@app_api.route("/")
def hello():
    logging.info("GET /")
    return "Hello World !"


def api_logging(lvl=logging.INFO):
    log_file_name = "kisiowall-api.log"
    log_format = '[%(levelname)s] - %(asctime)s - %(message)s'
    log_date_format = '%m-%d-%Y %H:%M:%S'

    logging.basicConfig(format=log_format, level=lvl, datefmt=log_date_format, filename=log_file_name, filemode='a')


if __name__ == "__main__":
    # Enable logs
    api_logging()
    app_api.run()
