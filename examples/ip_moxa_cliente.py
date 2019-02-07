import sys
import logging

import getopt
import logging
from reeprotocol_moxa import Moxa
from iec870ree.ip import Ip
from iec870ree.protocol import LinkLayer, AppLayer
import datetime


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
        for resp in app_layer\
            .read_absolute_values(datetime.datetime(2018, 10, 1, 1, 0),
                                  datetime.datetime(2018, 10, 5, 0, 0)):
            # .read_integrated_totals(datetime.datetime(2018, 4, 1, 0, 0),
            #                         datetime.datetime(2018, 4, 2, 1, 0)):
            logging.info("read response {}".format(resp))
    except Exception:
        raise
    finally:
        app_layer.finish_session()
        physical_layer.disconnect()
        sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    argv = sys.argv[1:]
    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv,"i:hp:d:p:c:t:",
                                   ["ip=", "port=",
                                    "der=", "dir_pm=", "clave_pm=", "tlf="])
    except getopt.GetoptError:
       logging.error('wrong command')
       sys.exit(2)

    ip = None
    port = None
    der = None
    dir_pm = None
    clave_pm = None
    tlf = None
    for opt, arg in opts:
        if opt == '-h':
          logging.error("help not implemented")
          sys.exit()
        elif opt in ("-p", "--port"):
          port = int(arg)
        elif opt in ("-n", "--ip"):
          ip = arg
        elif opt in ("-d", "--der"):
          der = int(arg)
        elif opt in ("-p", "--dir_pm"):
          dir_pm = int(arg)
        elif opt in ("-c", "--clave_pm"):
          clave_pm = int(arg)
        elif opt in ("-t", "--tlf"):
          tlf = arg

    logging.info('Started {} {} {} {} {} {}'.format(ip, port, der, dir_pm,
                                                    clave_pm, tlf))
    run_example(ip, port, der, dir_pm, clave_pm, tlf)
