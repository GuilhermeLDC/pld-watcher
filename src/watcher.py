import boto3
import json
import logging
import os
import requests
from datetime import datetime, timedelta

URL_BASE = "https://www.ccee.org.br"

PLD_ROUTE = (
    "/portal/faces/oracle/webcenter/portalapp/pages/publico"
    "/oquefazemos/produtos/precos/lista_preco_horario.jspx"
)

PERIODO_TEMPLATE = "{since} - {until}"

headers = {
    "Cookie": (
        "portal=MtyJu6DsHJJ_H1lcWM44Pv8APkO2cVVCWPGYboVPqw5YsGNhLu-g"
        "!-1336158421!137072944; _ga=GA1.3.1591060531.1612578152;"
        " _gid=GA1.3.544342237.1612886862; OAMAuthnHintCookie=0@1612918080; "
        "OAMAuthnCookie_www.ccee.org.br:443=db69a65ffa9741bb2aa33ce1069d3c61e3"
        "97bb2a%7EdcDn3hTpbVzC9%2BqncTP1HxT9a9l%2FHMKf9HUScGgctv%2BLNdL5WY6pjd5tm05"
        "%2BGC6me%2F%2BvmwOBLM8E6d9lksLEZYY9%2F3LrPNeZNMAn2orYbjCAh9zGO8wkJ4J4Y1w5P"
        "gqJMGlC3nDcPOLZ2rXh7SR1tlvzrIo8lQufUploiS2aKud4%2Bx6TFFtO93u3dCKPWrNt6XnzAc"
        "JefCKK%2B%2FURhqVTBx%2Bgcy8e3NJDyM3609jxZSMBERH02SiyDeTiB6UBdZgyzlbC%2FMPJlR"
        "sxPQbCnwRhv%2BEgC2AGR7e%2FnI9JFvLLv8KlsSgGFEWFPKfTzJ8QcT7TviJbqPxcE0%2FMge8h"
        "cJDeSmOtu7OouJ8MHy6ZwUeYIxAdeeMjxP6JJVGhrpO0%2F8x65HlRWtVYCbO2AY60y5E8gw%3D"
        "%3D; _vis_opt_s=3%7C; _vis_opt_test_cookie=1; JSESSIONID=_u-JvB6HNYNn3hDC-VzC"
        "-2zxXMaMAWpixkqOLqec7UPczFU_mnI9!-1932641016!742771088"
    ),
    "Host": "www.ccee.org.br",
    "Origin": "https://www.ccee.org.br",
}


logger = logging.getLogger()
logger.setLevel(logging.INFO)

SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")


def handler(event, context={}):
    bucket = event.get("bucket", "watcher-energy")
    until = event.get("until")
    until = datetime.strptime(until, "%d/%m/%Y") if until else datetime.today()
    since = event.get("since")
    since = datetime.strptime(since, "%d/%m/%Y") if since else until - timedelta(days=1)

    # Roda meia noite e coleta tudo do dia anterior.
    since_file = since.strftime("%d_%m_%Y") + "__" + until.strftime("%d_%m_%Y")
    until = until.strftime("%d/%m/%Y")
    since = since.strftime("%d/%m/%Y")

    payload = {"periodo": PERIODO_TEMPLATE.format(until=until, since=since)}

    response = requests.post(URL_BASE + PLD_ROUTE, data=payload, headers=headers)

    if response.status_code == 200:
        logger.info("Salvando html ... ")

        file_name = f"pld_{since_file}.html"
        client = boto3.client("s3")
        client.put_object(Body=response.text, Bucket=bucket, Key=file_name)

    else:
        logger.warning("Erro na chamada ... ")
        client_sns = boto3.client("sns")
        client_sns.publish(TopicArn=SNS_TOPIC_ARN, Message="Falha em observar pld ... ")


if __name__ == "__main__":
    event = {"since": "10/02/2021", "until": "14/02/2021"}
    handler(event)
