from timeit import default_timer as timer
from dateutil import parser
import threading
import datetime
import socket
import time


def sendTime(slave_client):
    while True:
        slave_client.send(str(datetime.datetime.now()).encode())
        print("Time sent!\n\n")
        time.sleep(5)


def receiveTime(slave_client):
    while True:
        sync_time = parser.parse(slave_client.recv(1024).decode())

        # String to time
        str_time = datetime.datetime.strftime(sync_time, '%H:%M:%S')

        print("Sync time:", str_time)


def initSlaveClient(port=8000):
    slave_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    slave_client.connect(('localhost', port))

    slave_thread = threading.Thread(target=receiveTime, args=(slave_client,))
    slave_thread.start()

    print("Receiveng time from server...")
    receive_time_thread = threading.Thread(
        target=sendTime, args=(slave_client,))
    receive_time_thread.start()


if __name__ == '__main__':
    initSlaveClient()
