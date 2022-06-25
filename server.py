# Berkeley algorithm for clock synchronization

from functools import reduce
from dateutil import parser
import threading
import datetime
import socket
import time

# Object to store client IP and Clock data
client_data = {}


def receiveClockTime(connector, address):
    # Receive the clock time from the client
    while True:
        clock_time_string = connector.recv(1024).decode()
        clock_time = parser.parse(clock_time_string)
        clock_time_difference = datetime.datetime.now() - clock_time

        client_data[address] = {
            'clock_time': clock_time,
            'clock_time_difference': clock_time_difference,
            "connector": connector
        }

        print("Client data updated:", str(address), '\n\n')
        time.sleep(5)


def makeConnection(master_server):
    while True:
        master_slave_connector, address = master_server.accept()
        slave_address = str(address[0] + ":" + str(address[1]))

        print(slave_address, "connected")

        receiveClockTime(master_slave_connector, slave_address)


def getAverage():
    current_client = client_data.copy()

    time_difference_list = []
    for client_addr, client in current_client.items():
        time_difference_list.append(client['clock_time_difference'])

    clock_differences_sum = sum(time_difference_list, datetime.timedelta(0, 0))

    average_clock_difference = clock_differences_sum / \
        len(time_difference_list)

    return average_clock_difference


def syncClocks():
    while True:
        print("Num of clients", len(client_data))

        if len(client_data) > 0:
            average_clock_difference = getAverage()

            for client_addr, client in client_data.items():
                try:
                    time_sync = datetime.datetime.now() + average_clock_difference
                    client['connector'].send(str(time_sync).encode())
                except:
                    print("Error sending time to client")
        else:
            print("No clients connected")

        time.sleep(5)


def initMasterDaemon(port=8000):
    master_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master_server.bind(('', port))
    master_server.listen(5)

    current_thread = threading.Thread(
        target=makeConnection, args=(master_server,))
    current_thread.start()

    sync_thread = threading.Thread(target=syncClocks, args=())
    sync_thread.start()


if __name__ == '__main__':
    initMasterDaemon()
