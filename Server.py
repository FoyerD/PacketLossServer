import Parser
import Colors
import socket
from math import ceil
import threading
import time
import subprocess
import ipaddress
from Parser import SERVER_PORT_TCP, SERVER_PORT_UDP, CLIENT_PORT_UDP

DATA_TO_SEND = 'SKIBIDI_DATA' #IMSORRY
NUM_QUEUED_TCP = 5


# ---------------------helper functions-----------------------
def data_generator(data_to_send, num_bytes, size_part):
    '''cyclic data generator
    :param data_to_send: str, data to cycle
    :param num_bytes: number of total bytes to send
    :param size_part: the size of each part to yield'''
    data_len = len(data_to_send)
    curr_data = ''
    i = 0
    while num_bytes > 0:
        while len(curr_data) < size_part and num_bytes > 0:
            curr_data += data_to_send[i % data_len]
            i += 1
            num_bytes -= 1
        yield curr_data
        curr_data = ''

def get_subnet_mask(ip):
    """Usess the ipconfig command and subproccess to return the subnet mask of the network of ip"""
    proc = subprocess.Popen('ipconfig',stdout=subprocess.PIPE)
    while True:
        line = proc.stdout.readline()
        if ip.encode() in line:
            break
    mask = proc.stdout.readline().rstrip().split(b':')[-1].replace(b' ',b'').decode()
    return mask

def get_broadcast_addr(ip, mask):
    """Returns the broadcast addr given an ip addr and subnetmask"""
    return str(ipaddress.IPv4Interface(ip + '/' + mask).network.broadcast_address)

def start_thread(func, args):
    """Generic method to start a thread"""
    thread = threading.Thread(target=func, args=args)
    thread.daemon = True  # Allow thread to exit when main program does
    try:
        thread.start()
    except NameError:
        #print(Colors.red_str(NameError))
        return None
    return thread


# ---------------------thread functions-----------------------
def listen_tcp(sock):
    """Listens to incoming messages on the given port"""
    try:
        while True:
            # Wait for a connection from a client
            sock.listen(NUM_QUEUED_TCP)
            connection, client_addr = sock.accept()
            print(f"Received {Colors.red_str('[TCP]')} request from {Colors.blue_str(str(client_addr))}")
            start_thread(tcp_upload, (connection,))   

    except NameError as e:
        print(Colors.red_str(str(e)))

def listen_udp(sock):
    try:
        while True:
            # Wait for a message from a client
            data, client_address = sock.recvfrom(Parser.REQUEST_HEADER_SIZE)  # buffer size is 1024 bytes
            if(len(data) != Parser.REQUEST_HEADER_SIZE):
                #print(Colors.red_str(f"Error: size of request msg is not {Parser.REQUEST_HEADER_SIZE}"))
                continue
            cookie, msg_type, file_size = Parser.unpack_request(data)
            if(cookie != Parser.MAGIC_COOKIE or msg_type != Parser.REQUEST_TYPE):
                #print(Colors.red_str(f"Error: THE MAGIC COOKIE IS WRONG! ITS {cookie} != {Parser.MAGIC_COOKIE}"))
                continue
            print(f"Received {Colors.yellow_str('[UDP]')} request from {Colors.blue_str(str(client_address))}")
            start_thread(udp_upload, (sock, client_address, file_size))
    except NameError as e:
        print(Colors.red_str(e))

def udp_upload(sock, dest_addr, size):
    try:
        seg_count = ceil(size / Parser.PAYLOAD_SIZE)
        for i, segment in enumerate(data_generator(DATA_TO_SEND, size, Parser.PAYLOAD_SIZE)):
            sock.sendto(Parser.pack_payload_udp(seg_count, i, segment), dest_addr)
    except NameError as e:
        print(Colors.red_str(e))

def tcp_upload(sock,):
    try:
        buffer = ''
        file_size = 0
        data = ''
        
        while(data != b'\n'):
            data = sock.recv(1)  
            if(data == b'\n'):
                file_size = int(buffer)
            else:
                buffer = buffer + data.decode()
        
        seg_count = ceil(file_size / len(DATA_TO_SEND))
        whole_data = (DATA_TO_SEND * seg_count)[:file_size]
        sock.sendall(whole_data.encode())
    except NameError as e:
        print(Colors.red_str(e))

def send_broadcast_message(message, port, interval):
    """Constantly sends message on udp through te given port every interval seconds"""
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Allow the socket to send broadcast messages
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    while True:
        # Send the broadcast message
        try:
            sock.sendto(message, (get_broadcast_addr(HOST, MASK), port))
        except NameError:
            print(NameError)
        time.sleep(interval)



# ---------------------main function---------------------
def main():
    interval = 1  # Interval in seconds

    # Start the listening threads
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind(('', SERVER_PORT_TCP))
    tcp_thread = start_thread(listen_tcp, (tcp_sock, ))
    if(tcp_thread == None):
        print("Faild to start thread for listening on TCP port")
        return

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('', SERVER_PORT_UDP))
    udp_thread = start_thread(listen_udp, (udp_sock, ))
    if(udp_thread == None):
        print("Faild to start thread for listening on UDP port")
        return


    # Start the broadcast thread
    broadcast_thread = start_thread(send_broadcast_message, (Parser.pack_offer(SERVER_PORT_UDP, SERVER_PORT_TCP), CLIENT_PORT_UDP, interval))
    if(broadcast_thread == None):
        print("Faild to start thread for broadcasting")
        return
    print(f'Server started, listening on IP address {Colors.purple_str(HOST)}')
    broadcast_thread.join()
    
    tcp_sock.close()
    udp_sock.close()

    


# -------main condition---------
if __name__ == "__main__":
    HOSTNAME = socket.gethostname()
    HOST = socket.gethostbyname(HOSTNAME)
    MASK = get_subnet_mask(HOST)   
    main()
# -------end of file-------