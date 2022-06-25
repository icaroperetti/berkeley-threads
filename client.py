from timeit import default_timer as timer
from dateutil import parser
import threading
import datetime
import socket
import time


# Send the client time to the server
def sendTime(slave_client):
    while True:
        slave_client.send(str(datetime.datetime.now()).encode())
        print("Time sent!\n\n")
        time.sleep(5)

# Receive the server time


def receiveTime(slave_client):
    while True:
        sync_time = parser.parse(slave_client.recv(1024).decode())

        # String to time
        str_time = datetime.datetime.strftime(sync_time, '%H:%M:%S')

        print("New time is:", str_time)


def initSlaveClient(port=8000):
    slave_client = socket.socket()
    slave_client.connect(('localhost', port))  # Connect to the server

    # Start the time sending thread
    print("Starting time sending thread...")
    send_time_thread = threading.Thread(
        target=sendTime, args=(slave_client,))
    send_time_thread.start()

    # Start thread to receive time from server
    print("Starting to receiving " +
          "synchronized time from server\n")
    receive_time_thread = threading.Thread(
        target=receiveTime, args=(slave_client,))
    receive_time_thread.start()


if __name__ == '__main__':
    initSlaveClient()
