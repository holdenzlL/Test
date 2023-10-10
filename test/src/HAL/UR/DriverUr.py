from .IUr import IUr
import socket
import telnetlib
import time
import logging
import os
import threading

DEFAULT_IP = '192.168.162.128'
DEFAULT_PORT = 29999
#DEFAULT_PORT = 10770


class DriverUr(IUr, object):
    def __init__(self, pollintervall=1, delimiter=b'\n'):
        self.client_socket = None
        self.tn = None
        self.received_messages = []  # Store received messages here
        self.lock = threading.Lock()  # Create a lock for synchronization
        self.setup_logging()
        self.__mCmd = ""
        self.__mResponse = ""
        self.__mTIME_OUT_SOCKET_CONNECTION = 30  # 30 second timeout on commands

        self.command_que = []
        self.pollintervall = pollintervall
        self.host = None
        self.port = None
        self.timer = time.monotonic()
        self._on_overload = None
        self._on_message = None
        self._on_message_sent = None
        self._on_no_reply = None
        self._on_available = None
        self._on_error = None
        self.delimiter = delimiter
        self._disconnect = False
        self.last_loop_send = True
        self.run_loop = True

    def setup_logging(self):
        log_file = os.path.join(os.path.dirname(__file__), "client_log.log")
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            handlers=[
                                logging.FileHandler(log_file),
                                logging.StreamHandler()
                            ])

    def _Connect(self, host=DEFAULT_IP, port=DEFAULT_PORT):
        return_val = False
        if len(host) == 0:
            raise ValueError('Invalid host.')
        if port <= 0:
            raise ValueError('Invalid port number.')
        self.host = host
        self.port = port
        logging.info('Trying to connect to ip={} and port={}'.format(self.host, self.port))
        try:
            self.client_socket = socket.create_connection((host, port), timeout=self.__mTIME_OUT_SOCKET_CONNECTION)
            return_val = True
        except (ConnectionRefusedError, socket.gaierror, socket.timeout) as e:
            # indicate that retrying might make sense
            raise logging.error(f'can not connect to {host}:{port}, {e}') from None


        #if (self._Reconnect()) is not None:
        #    return_val = True

        return return_val

    def _Reconnect(self):
        s = None
        for res in socket.getaddrinfo(self.host, self.port, socket.AF_INET, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                s = socket.socket(af, socktype, proto)
            except socket.error as err:
                s = None
                logging.error('TcpRequestResponseClient.connect: {}'.format(err))
                continue
            try:
                s.connect(sa)
            except socket.error as err:
                s.close()
                logging.error('TcpRequestResponseClient.connect: {}'.format(err))
                s = None
                continue
            break
        if s is None:
            logging.error('TcpRequestResponseClient.connect: Could not open socket')
            return None

        s.setblocking(False)
        self.client_socket = s
        logging.info('Connected to {} on port {}'.format(self.host, self.port))
        return s

    def _Disconnect(self):
        logging.info('Disconnecting {} on port {}'.format(self.host, self.port))
        self._disconnect = True
        self._Close()

    def _Close(self):
        logging.info('Closing socket to {} on port {}'.format(self.host, self.port))
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            return
        else:
            logging.info('tcp_request_response.close(): No socket to close')
            return

    # keep a reference to socket to avoid (interpreter) shut-down problems
    def CloseSocket(self, sock, socket=socket):  # pylint: disable=redefined-outer-name
        """Do our best to close a socket."""
        if sock is None:
            return
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        try:
            sock.close()
        except socket.error:
            pass

    def Connect(self, hostname, port):
        try:
            # Create a raw socket
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # , socket.SOCK_RAW, socket.IPPROTO_RAW)

            # Connect to the server using telnet options
            self.tn = telnetlib.Telnet()
            self.tn.sock = self.client_socket
            self.tn.open(hostname, port)
            logging.info("Connected to the server (host:%s, port: %s).", hostname, port)
            return True

        except socket.error as e:
            logging.info("Error occurred:", e)
            return False

    def DoDisconnect(self):
        if self.tn:
            self.tn.close()
        self.tn = None
        logging.info("Connection closed.")

    def SendCommand(self, command):
        if self.tn:
            self.__mCmd = command
            self.__mResponse = "" #wichtig
            message = self.__mCmd + "\n"
            self.tn.write(message.encode())
            #time.sleep(0.5)
            #response = self.tn.read_until(b"\r\n").decode()
            #logging.info("Sent: %s, Received: %s", message, response.strip())
            logging.info("Sent: %s", message)

    def IsConnected(self):
        return self.tn is not None and self.tn.sock is not None

    def IsDisconnected(self):
        return not self.IsConnected()

    def ResetReceivedMessages(self):
        #with self.lock:
        self.received_messages = []
        
    def GetLastResponse(self) -> str:
        return self.__mResponse
    
    def GetReceivedMessages(self):
        #with self.lock:
        return self.received_messages

    def ReceiveMessages(self):
        return_val = True
        if self.tn and self.IsConnected():
            try:
                message = self.tn.read_until(b"\n", timeout=1)
                if message:
                    self.received_messages.append(message.decode("utf-8").strip())
                    self.__mResponse = message.decode("utf-8").strip()
                    logging.info("*****************Received: %s", message.decode("utf-8").strip())
            except EOFError:
                logging.info("ERROR DURING READING UR")
                return_val = False #needs to be reconected
            time.sleep(0.1)

        return return_val

