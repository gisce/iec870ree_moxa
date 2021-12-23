import sys
import logging

import getopt
import logging
from iec870ree_moxa import Moxa
from iec870ree.ip import Ip
from iec870ree.protocol import LinkLayer, AppLayer
import datetime

import click

try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse


def run_example(ip, port, der, dir_pm, clave_pm, tlf):
    try:
        ip_layer = Ip((ip, port))
        # Enviar comandes AT (modem)
        physical_layer = Moxa(str(tlf), ip_layer)
        link_layer = LinkLayer(der, dir_pm)
        link_layer.initialize(physical_layer)
        app_layer = AppLayer()
        app_layer.initialize(link_layer)

        physical_layer.connect()
        link_layer.link_state_request(retries=0)
        link_layer.remote_link_reposition(retries=0)
        logging.info("before authentication")
        resp = app_layer.authenticate(clave_pm)
        logging.info("CLIENTE authenticate response {}".format(resp))
        logging.info("before read")
        resp = app_layer.get_info()
        logging.info("read response {}".format(resp))
        resp = app_layer.read_datetime()
        logging.info("read response read_datetime {}".format(resp.content))
        now = datetime.datetime.now()
        meter_date = resp.content.tiempo.datetime
        diff = (now - meter_date).total_seconds()
        logging.info("NOW {}".format(now))
        logging.info("METER DATETIME {}".format(meter_date))
        logging.info("DIFF {}".format(diff))
    except Exception:
        raise
    finally:
        app_layer.finish_session()
        physical_layer.disconnect()
        sys.exit(1)


def get_connection(url):
    url = urlparse(url)
    # PATH is TM connection params in format TELF,DER,PM,PWD
    telf, der, pm, pwd = url.path.replace('/', '').split(',')
    host = url.hostname
    port = url.port

    logging.info('Started {} {} {} {} {} {}'.format(host, port, telf, der, pm, pwd))
    return {'host': url.hostname, 'port': url.port, 'telf': telf, 'der': der, 'dir_pm': pm, 'pwd': pwd}


@click.command()
@click.option('-u', '--url',
              help='URL to connect to moxa (server:port/TELF,DER,PM,PASS)',
              type=str, default='iecmoxa://127.0.0.1:950/97221384,1,1,1', show_default=True)
def connect_moxa(url):
    logging.basicConfig(level=logging.INFO)
    conn_data = get_connection(url)

    run_example(
        conn_data['host'],
        int(conn_data['port']),
        int(conn_data['der']),
        int(conn_data['dir_pm']),
        int(conn_data['pwd']),
        conn_data['telf']
    )


if __name__ == "__main__":
    connect_moxa()
