Moxa Physical layer
===================

Physical layer for using a `Moxa devices <https://www.moxa.com/product/SDS_SerialDevice%20Servers.htm>`_
for `reeprotocol library <https://github.com/javierdelapuente/reeprotocol>`_


Using:

.. code-block:: python

    from reeprotocol_moxa import Moxa
    from reeprotocol.ip import Ip
    from reeprotocol.protocol import LinkLayer, AppLayer
    import reeprotocol.protocol
    import datetime

    ip_layer = reeprotocol.ip.Ip(('127.0.0.1', 40001))
    physical_layer = reeprotocol.moxa.Moxa('PHONENUMBER', ip_layer)
    link_layer = reeprotocol.protocol.LinkLayer(10345, 1)
    link_layer.initialize(physical_layer)
    app_layer = reeprotocol.protocol.AppLayer()
    app_layer.initialize(link_layer)
    physical_layer.connect()
    link_layer.link_state_request()
    link_layer.remote_link_reposition()
    logging.info("before authentication")
    resp = app_layer.authenticate(1)
    logging.info("CLIENTE authenticate response {}".format(resp))
    logging.info("before read")

    start_date = datetime.datetime(2018, 4, 1, 0, 0)
    end_date = datetime.datetime(2018, 4, 2, 1, 0)

    for resp in app_layer.read_integrated_totals(start_date, end_date):
        logging.info("read response {}".format(resp))
    physical_layer.disconnect()
