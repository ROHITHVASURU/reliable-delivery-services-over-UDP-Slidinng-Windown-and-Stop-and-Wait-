import socket
import os
import time
import sys

class RReceiveUDP:
    def __init__(self):
        # Initialize variables and settings
        self.filename = None
        self.local_port = 5000  # Default local port number
        self.mode = 0  # Default mode (stop-and-wait)
        self.mode_parameter = 256  # Default mode parameter (window size for sliding window)
        self.timeout = 1000  # Default timeout value in milliseconds
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', self.local_port))
        self.packet_size = 500  # Max packet size after considering UDP header size (1500 - 20 - 8)

    def get_filename(self):
        return self.filename

    def get_local_port(self):
        return self.local_port

    def get_mode(self):
        return self.mode

    def get_mode_parameter(self):
        return self.mode_parameter

    def get_timeout(self):
        return self.timeout

    def set_filename(self, fname):
        self.filename = fname

    def set_local_port(self, port):
        self.local_port = port
        # Re-bind the socket to the new port
        self.socket.bind(('localhost', self.local_port))

    def set_mode(self, mode):
        self.mode = mode

    def set_mode_parameter(self, parameter):
        self.mode_parameter = parameter

    def set_timeout(self, timeout):
        self.timeout = timeout

    def receive_file(self):
        if not self.filename:
            print("Filename not specified.")
            return False

        try:
            with open(self.filename, 'wb') as file:
                seq_num = 0

                if self.mode == 0:  # Stop-and-wait
                    print("mode : stop-and-wait")
                    while True:
                        data, addr = self.socket.recvfrom(self.packet_size)
                        if data == b"EndTransmission":
                            break
                        parts = data.decode().split(':')
                        data = ':'.join(parts[1:])
                        data = data.encode()

                        # Simulate sending ACK back to sender
                        ack = str(seq_num).encode()

                        self.socket.sendto(ack, addr)
                        print(f"Sent ACK for packet {seq_num} to {addr}")

                        file.write(data)
                        seq_num += 1

                elif self.mode == 1:  # Sliding window
                    print("mode: sliding window")
                    expected_seq_num = 0
                    window_size = self.mode_parameter
                    received_packets = {}

                    max_prints = 5  # Set the maximum number of times to print received data
                    print_count = 0

                    while True:
                        data, addr = self.socket.recvfrom(self.packet_size)
                        if data == b"EndTransmission":
                            break

                        parts = data.decode().split(':')
                        if len(parts) >= 2:
                            seq_num_str = parts[0]
                            try:
                                seq_num = int(seq_num_str)
                                payload = ':'.join(parts[1:])  # Reconstruct payload after the sequence number
                                
                                if seq_num == expected_seq_num:
                                    received_packets[seq_num] = payload
                                    while expected_seq_num in received_packets:
                                        file.write(received_packets[expected_seq_num].encode())  # Encode payload before writing
                                        del received_packets[expected_seq_num]
                                        expected_seq_num += 1
                                    
                                    # Send cumulative ACK for the last correctly received packet
                                    ack = str(seq_num).encode()
                                    self.socket.sendto(ack, addr)
                                    print(f"Sent ACK for packet {seq_num} to {addr}")
                                else:
                                    # Send ACK for the last correctly received packet
                                    ack = str(expected_seq_num - 1).encode()
                                    self.socket.sendto(ack, addr)
                                    print(f"Sent ACK for packet {expected_seq_num - 1} to {addr}")
                            except ValueError:
                                print(f"Invalid sequence number format: {seq_num_str}")
                                
                        else:
                            print("Invalid data format, sequence number not found")

                        # Check if maximum print count is reached
                        if print_count < max_prints:
                            #print(f"Received data: {data}")
                            print_count += 1

                    print("File reception completed.")
                    return True

        except Exception as e:
            print(f"File reception failed: {e}")
            return False


if __name__ == "__main__":
    # Receiver (RReceiveUDP)
    #input_file = input()
    receiver = RReceiveUDP()
    print("\nex usage: python3 receiver_udp.py mode(0 0r 1) send_filename.txt\n")
    receiver.set_filename("received_file.txt")  # Set the filename for received file
    receiver.set_mode(0)  # Set the mode (0 for stop-and-wait, 1 for sliding window)
    if len(sys.argv) == 2 :
        receiver.set_mode(int(sys.argv[1]))
    elif len(sys.argv) == 3 :
        receiver.set_mode(int(sys.argv[1]))
        receiver.set_filename(sys.argv[2])

    elif len(sys.argv) > 3 : 
        print("Use any of following options to run the program")
        print("1. python3 receive_udp.py ")
        print("2. python3 receive_udp.py mode(0 or 1)")
        print("3. python3 receive_udp.py mode(0 or 1) and filename(ex;-readme.txt)\n ")
    receiver.receive_file()
