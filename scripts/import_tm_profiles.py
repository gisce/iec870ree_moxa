import sys
import getopt
import logging

from iec870ree_moxa import Moxa
from iec870ree_moxa.moxa import ModemException
from iec870ree.ip import Ip
from iec870ree.protocol import LinkLayer, AppLayer
from datetime import datetime
from pyreemote.telemeasure import parse_profiles


def run_example(ip, port, der, dir_pm, clave_pm, tlf, meter, df_str, dt_str):
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
        link_layer.remote_link_reposition()
        logging.info("before authentication")
        resp = app_layer.authenticate(clave_pm)
        logging.info("CLIENTE authenticate response {}".format(resp))
        logging.info("before read")
        resp = app_layer.get_info()
        logging.info("read response {}".format(resp))
        values = []
        logging.info("Gathering data...")
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        df = datetime.strptime(df_str, '%Y-%m-%d %H:%M:%S')
        for resp in app_layer.read_incremental_values(df, dt, register='profiles'):
            values.append(resp.content.valores)
            logging.info("read response {}".format(resp))
        result = parse_profiles(values, meter, df_str, dt_str)
        logging.info(result)
        return result
        # To create the profiles use create_requested_profiles method with the
        # result
    except Exception as e:
        logging.info(e)
        raise e
    finally:
        app_layer.finish_session()
        physical_layer.disconnect()
        sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    argv = sys.argv[1:]
    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv, "i:hp:d:p:c:t:m:df:dt:", [
            "ip=", "port=", "der=", "dir_pm=", "clave_pm=", "tlf=", "meter=",
            "from_d=", "to_d="])
    except getopt.GetoptError:
       logging.error('wrong command')
       sys.exit(2)

    ip = None
    port = None
    der = None
    dir_pm = None
    clave_pm = None
    tlf = None
    meter = None
    from_d = None
    to_d = None
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
        elif opt in ("-r", "--dir_pm"):
          dir_pm = int(arg)
        elif opt in ("-c", "--clave_pm"):
          clave_pm = int(arg)
        elif opt in ("-t", "--tlf"):
          tlf = arg
        elif opt in ("-m", "--meter"):
          meter = arg
        elif opt in ("-i", "--inici"):
          from_d = arg
        elif opt in ("-f", "--final"):
          to_d = arg

    logging.info('Started {} {} {} {} {} {}'.format(ip, port, der, dir_pm,
                                                    clave_pm, tlf, meter,
                                                    from_d, to_d))
    try:
        run_example(ip, port, der, dir_pm, clave_pm, tlf, meter, from_d, to_d)
    except ModemException as e:
        logging.info('Modem Exception: {}'.format(e))
