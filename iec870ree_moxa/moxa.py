from iec870ree.protocol import PhysicalLayer
from iec870ree.ip import Ip
import threading
import six
if six.PY2:
    import Queue as queue
else:
    import queue
import time
import logging
import socket

logger = logging.getLogger('reeprotocol.moxa')


class ModemException(Exception):
    pass


DEFAULT_INIT_STRING = "ATZ:2;ATH0:3;AT+CBST=7,0,1:3"

class Moxa(PhysicalLayer):
    CONNECTED_WORDS = ["CONNECT", "REL ASYNC"]
    NO_CONNECT_WORDS = ["NO CARRIER", "BUSY", "NO DIALTONE",'NO ANSWER']

    def __init__(self, phone_number, ip_layer, init_str=None):
        assert isinstance(ip_layer, Ip)
        self.phone_number = phone_number
        self.ip = ip_layer
        self.init_string = DEFAULT_INIT_STRING if init_str is None else init_str
        self.ip.thread = threading.Thread(target=self.read_port)
        self.modem_connected = False
        self.data_mode = False

    @property
    def connected(self):
        return self.ip.connected

    @property
    def queue(self):
        return self.ip.queue

    def connect(self):
        if (self.connected):
            return

        try:
            self.ip.connect()
            self.initialize_modem()
        except Exception as e:
            self.disconnect()
            raise ConnectionError(e)

    def initialize_modem(self):
        self.writeat("+++", no_r=True)
        time.sleep(3)

        split_write_sleep = self.init_string.split(';')
        for x in split_write_sleep:
            init_text, init_sleep = x.split(':')
            if not init_text.strip() or not init_sleep.strip():
                raise "Init modem string has some empty values."
            self.writeat(init_text)
            time.sleep(init_sleep)

        self.writeat("ATD" + str(self.phone_number))
        self.waitforconnect()
        time.sleep(self.ip.waiting)

    def waitforconnect(self):
        max_tries = 80
        for i in range(max_tries):
            try:
                i = self.queue.get(False, 1)
                logger.debug("got message> {}".format(i))
                for word in self.CONNECTED_WORDS:

                    if word in i:
                        logger.debug("---- CONNECTION SUCCEEDED ----")
                        self.data_mode = True
                        self.queue.task_done()
                        time.sleep(5)  # everything smooth in read thread
                        return
                for word in self.NO_CONNECT_WORDS:
                    if word in i:
                        logger.debug("--- NOT CONNECTED ---")
                        raise ConnectionError("Connection not stablished: {}".format(word))
                self.queue.task_done()
            except queue.Empty:
                logger.debug("nothing yet...")
                time.sleep(1)
        raise ConnectionError("Error Waiting for connection")

    def disconnect(self):
        if not self.connected:
            return

        try:
            if self.data_mode:
                self.writeat("+++", no_r=True)
                time.sleep(3)
            self.writeat("ATH0")
            time.sleep(3)
            self.ip.disconnect()
        finally:
            self.data_mode = False

    def send_byte(self, bt):
        if not self.data_mode:
            raise ModemException("modem not in datamode")
        self.write(bytes([bt]))

    def send_bytes(self, bt):
        if not self.data_mode:
            raise ModemException("modem not in datamode")
        self.write(bt)

    def get_byte(self, timeout=60):
        if not self.data_mode:
            raise ModemException("modem not in datamode")
        return self.queue.get(True, timeout)

    def writeat(self, value, no_r=False):
        logger.info("sending command " + value)
        sufix = "\r"
        if no_r:
            sufix = ''
        self.write((value + sufix).encode("ascii"))

    def write(self, value):
        if not self.connected:
            raise ModemException("modem not connected")
        logger.debug("->" + ":".join("%02x" % b for b in value))
        self.ip.connection.send(value)

    def read_port(self):
        logger.info("read thread Starting")
        buffer = bytearray()
        self.ip.connection.settimeout(10.0)
        while self.connected:
            logger.debug("iterate read thread")
            try:
                response = self.ip.connection.recv(1)
            except socket.timeout as e:
                continue
            except Exception as e:
                continue
            if not response:
                logger.debug("<- no response")
                continue
            logger.debug("<-" + ":".join("%02x" % b for b in response))
            for b in response:
                # if not self.data_mode and (b == 0x0A or b == 0x0D):
                if not self.data_mode:
                    # answer with the line
                    buffer.append(b)
                    if (b == 0x0A):
                        logger.info("R-" + buffer.decode("ascii"))
                        self.queue.put(buffer.decode("ascii"))
                        del buffer[:]
                else:
                    self.queue.put(b)

        logger.info("read thread END")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.disconnect()
