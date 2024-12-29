import socket
import os
import time
import sys

class RSendUDP:
    def __init__(self):
        # Initialize variables and settings
        self.filename = None
        self.local_port = 12987  # Default local port number
        self.mode = 0  # Default mode (stop-and-wait)
        self.mode_parameter = 256  # Default mode parameter (window size for sliding window)
        self.receiver = ('localhost', 5000)  # Default receiver address and port
        self.timeout = 1000  # Default timeout value in milliseconds
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', self.local_port))
        self.packet_size = 500  # Max packet size 

    def send_file(self):
        if not self.filename:
            print("Filename not specified.")
            return False

        try:
            with open(self.filename, 'rb') as file:
                seq_num = 0
                bytes_sent = 0  # Track the total bytes sent
                start_time = time.time()  # Track start time for transmission

                while True:
                    data = file.read(self.packet_size)
                    if not data:
                        self.socket.sendto(b"EndTransmission", self.receiver)
                        break
                    
                    packet = f"{seq_num}:{data.decode()}"  # Format the packet with sequence number
                    packet = packet.encode()  # Convert to bytes for transmission
                    
                    resend_attempts = 0
                    max_resend_attempts = 5  # Maximum resend attempts for a packet

                    # Sending loop for a single packet
                    while resend_attempts < max_resend_attempts:
                        if resend_attempts > 0:
                            print(f"Resending packet {seq_num}...")
                        try:
                            self.socket.sendto(packet, self.receiver)
                            print(f"Sent packet {seq_num} with {len(data)} bytes")
                            bytes_sent += len(data)

                            ack, addr = self.socket.recvfrom(1024)
                            ack_num = int(ack.decode())
                            if ack_num == seq_num:
                                print(f"Received ACK: {ack_num} from {addr}")
                                seq_num += 1  # Increment sequence number for the next packet
                                break
                        except socket.timeout:
                            print(f"Timeout occurred for packet {seq_num}. Resending...")
                        resend_attempts += 1

                    if resend_attempts == max_resend_attempts:
                        print(f"Max resend attempts reached for packet {seq_num}. Skipping...")
                        seq_num += 1  # Move to the next packet after reaching max resend attempts

                end_time = time.time()
                transmission_duration = end_time - start_time

                print(f"\nFile transmission completed. Sent {seq_num} packets.")
                print(f"Total bytes sent: {bytes_sent} bytes.")
                print(f"Transmission duration: {transmission_duration:.2f} seconds.")

                return True

                
        except KeyboardInterrupt:
            print("\nTransmission interrupted. Closing the sender.")
            self.socket.close()
            return False

        except FileNotFoundError:
            print("File not found.")
            return False


    def get_mode(self):
        return self.mode

    def get_mode_parameter(self):
        return self.mode_parameter

    def get_receiver(self):
        return self.receiver

    def get_timeout(self):
        return self.timeout

    def set_filename(self, filename):
        self.filename = filename

    def set_local_port(self, port):
        self.local_port = port
        # Re-bind the socket to the new port
        self.socket.bind(('localhost', self.local_port))

    def set_mode(self, mode):
        self.mode = mode

    def set_mode_parameter(self, parameter):
        self.mode_parameter = parameter

    def set_receiver(self, receiver):
        self.receiver = receiver

    def set_timeout(self, timeout):
        self.timeout = timeout

    def get_filename(self):
        return self.filename

    def get_local_port(self):
        return self.local_port

    def get_file_size(self):
        try:
            # Get the current working directory
            current_directory = os.getcwd()

            # Join the directory with the file name
            file_path = os.path.join(current_directory, sender.get_filename())

            # Get the size of the file
            size = os.path.getsize(file_path)
            return size

        except OSError as e:
            # Handle errors, like file not existing
            print(f"Error: {e}")
            return None
    def get_local_ip(self):
        if self.socket:
            return f"{self.socket.getsockname()[0]}:{self.socket.getsockname()[1]}"
        return "Not Connected"


if __name__ == "__main__":
    # Sender (RSendUDP)
    sender = RSendUDP()
    
    print("\nex usage: python3 send_udp.py mode(0 0r 1) send_filename.txt\n")


    sender.set_filename("README.txt")  # Set the filename to be sent
    sender.set_mode(0)  # Set the mode (0 for stop-and-wait, 1 for sliding window)
    
    if len(sys.argv) == 2 :
        sender.set_mode(sys.argv[1])
    elif len(sys.argv) == 3 :
        sender.set_mode(sys.argv[1])
        sender.set_filename(sys.argv[2])
    elif len(sys.argv) == 5:
        sender.set_mode(sys.argv[1])
        sender.set_filename(sys.argv[2])
        sender.set_receiver((sys.argv[3],int(sys.argv[4])))

    elif len(sys.argv) > 5: 
        print("Use any of following options to run the program")
        print("1. python3 send_udp.py ")
        print("2. python3 send_udp.py mode(0 or 1)")
        print("3. python3 send_udp.py mode(0 or 1) and filename(ex;-readme.txt)\n ")
        print("4. python3 send_udp.py mode(0 or 1) and filename(ex;-readme.txt) receiver_adress receiver_port\n ")

    print(f"Sending {sender.get_filename()} from {sender.get_local_ip()} to {socket.gethostbyname(sender.get_receiver()[0])}:{sender.get_receiver()[1]} with {sender.get_file_size()} bytes \n")

    sender.send_file()

    
