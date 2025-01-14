import Parser
import Colors
import socket
import threading
import time
import subprocess
import ipaddress


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
    return ipaddress.IPv4Network(ip + '/' + mask, False)


def start_listen_tcp(port):
    """Listens to incoming messages on the given port"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock
        sock.bind(('', port))
        sock.accept()

def start_tcp_thread(host, port):
    """Start a that listens to incoming messages on tcp."""
    broadcast_thread = threading.Thread(target=start_listen_tcp, args=(port))
    broadcast_thread.daemon = True  # Allow thread to exit when main program does
    try:
        broadcast_thread.start()
    except NameError:
        return None
    return broadcast_thread


def start_listen_udp(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('', port))
        while True:
            # Wait for a message from a client
            data, client_address = sock.recvfrom(Parser.PAYLOAD_SIZE)  # buffer size is 1024 bytes
            print(f"Received message from {client_address}: {data.decode('utf-8')}")

def start_udp_thread(host, port):
    """Start a that listens to incoming messages on tcp."""
    broadcast_thread = threading.Thread(target=start_listen_udp, args=(port))
    broadcast_thread.daemon = True  # Allow thread to exit when main program does
    try:
        broadcast_thread.start()
    except NameError:
        return None
    return broadcast_thread

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

def start_broadcast_thread(message, port, interval):
    """Start a thread to send broadcast messages."""
    broadcast_thread = threading.Thread(target=send_broadcast_message, args=(message, port, interval))
    broadcast_thread.daemon = True  # Allow thread to exit when main program does
    try:
        broadcast_thread.start()
    except NameError:
        return None
    return broadcast_thread



def main():
    interval = 1  # Interval in seconds

    # Start the listening threads
    tcp_thread = start_tcp_thread(SERVER_PORT_TCP)
    if(tcp_thread == None):
        print("Faild to start thread for listening on TCP port")
        return

    udp_thread = start_udp_thread(SERVER_PORT_UDP)
    if(udp_thread == None):
        print("Faild to start thread for listening on UDP port")
        return


    # Start the broadcast thread
    broadcast_thread = start_broadcast_thread(Parser.pack_offer(SERVER_PORT_UDP, SERVER_PORT_TCP), SERVER_PORT_UDP, interval)
    if(broadcast_thread == None):
        print("Faild to start thread for broadcasting")
        return
    print('Server started, listening on IP address ' + Colors.blue_str(HOST))
    broadcast_thread.join()

    



if __name__ == "__main__":
    SERVER_PORT_UDP = 3434
    SERVER_PORT_TCP = 4343
    HOSTNAME = socket.gethostname()
    HOST = socket.gethostbyname(HOSTNAME)
    MASK = get_subnet_mask(HOST)   
    main()