

from functools import reduce
from dateutil import parser
import threading
import datetime
import socket
import time
import numpy as np

# Object to store client IP and Clock data
client_data = {}


def receiveClockTime(connector, address):
    # Receive the clock time from the client
    while True:
        clock_time_string = connector.recv(1024).decode()
        clock_time = parser.parse(clock_time_string)
        # Calculate the difference between the client and the server
        clock_time_difference = datetime.datetime.now() - clock_time

        # Store the client data in a obj
        client_data[address] = {
            'clock_time': clock_time,
            'clock_time_difference': clock_time_difference,
            "connector": connector
        }

        time.sleep(5)


def makeConnection(master_server):
    while True:
        master_slave_connector, address = master_server.accept()
        # Get de IP and PORT of client
        slave_address = str(address[0] + ":" + str(address[1]))

        print(slave_address, "connected")

        # Create a thread to receive the clock time from the client
        current_thread = threading.Thread(
            target=receiveClockTime,
            args=(master_slave_connector,
                  slave_address, ))

        current_thread.start()


def getAverage():
    current_client = client_data.copy()  # Copy the client data

    # List of differences between the client and the server
    time_difference_list = []
    for client_addr, client in current_client.items():
        time_difference_list.append(client['clock_time_difference'])

    # Makes the sum of the differences
    clock_differences_sum = np.sum(time_difference_list)

    print(time_difference_list)  # Print the differences

    # Print the sum of the differences
    print("Clock differences sum:", clock_differences_sum, "\n")

    num_of_diff = len(time_difference_list)  # Print the number of differences

    average_clock_difference = np.abs(clock_differences_sum /
                                      (num_of_diff + 1))  # Calculate the average

    print("Average clock difference:",
          average_clock_difference, "\n")  # Print the average

    return average_clock_difference  # Return the average


def syncClocks():
    while True:
        print("Number of clients to be synchronized: " +
              str(len(client_data)))

        if len(client_data) > 0:
            average_clock_difference = getAverage()

            # For each client in the client data sends the correct time
            for client_addr, client in client_data.items():
                try:
                    time_sync = datetime.datetime.now() + average_clock_difference
                    client['connector'].send(str(time_sync).encode())
                    print(
                        f"Syncronized time is:{datetime.datetime.strftime(time_sync,'%H:%M:%S')}")
                except:
                    print("Error sending time to client")
        else:
            print("No clients connected")

        print('\n\n')

        time.sleep(5)


def initMasterDaemon(port=8000):
    master_server = socket.socket()
    master_server.setsockopt(socket.SOL_SOCKET,
                             socket.SO_REUSEADDR, 1)
    master_server.bind(('', port))
    master_server.listen(10)

    # Listening to requests
    master_thread = threading.Thread(
        target=makeConnection, args=(master_server,))
    master_thread.start()

    # Syncronize the clocks
    sync_thread = threading.Thread(target=syncClocks, args=())
    sync_thread.start()


if __name__ == '__main__':
    initMasterDaemon(port=8000)
