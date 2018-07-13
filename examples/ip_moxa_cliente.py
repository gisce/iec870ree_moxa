import sys
import logging

import getopt
import logging
from reeprotocol_moxa import Moxa
from reeprotocol.ip import Ip
from reeprotocol.protocol import LinkLayer, AppLayer
import reeprotocol.protocol
import datetime

def run_example(ip, port, der, dir_pm, clave_pm):
    ip_layer = Ip((ip, port))
    # Enviar comandes AT (modem)
    physical_layer = Moxa('696569962', ip_layer)
    link_layer = LinkLayer(der, dir_pm)
    link_layer.initialize(physical_layer)
    app_layer = AppLayer()
    app_layer.initialize(link_layer)

    physical_layer.connect()
    link_layer.link_state_request()
    link_layer.remote_link_reposition()
    logging.info("before authentication")
    resp = app_layer.authenticate(clave_pm)
    logging.info("CLIENTE authenticate response {}".format(resp))
    logging.info("before read")
    for resp in app_layer\
        .read_integrated_totals(datetime.datetime(2018, 4, 1, 0, 0),
                                datetime.datetime(2018, 4, 2, 1, 0)):
        logging.info("read response {}".format(resp))
    physical_layer.disconnect()
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    argv = sys.argv[1:]
    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv,"i:hp:d:p:c:",
                                   ["ip=", "port=",
                                    "der=", "dir_pm=", "clave_pm="])
    except getopt.GetoptError:
       logging.error('wrong command')
       sys.exit(2)

    ip = None
    port = None
    der = None
    dir_pm = None
    clave_pm = None
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

    logging.info('Started {} {} {} {} {}'.format(ip, port,
                                                 der, dir_pm, clave_pm))
    run_example(ip, port, der, dir_pm, clave_pm)
