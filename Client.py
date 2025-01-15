import Parser
import socket
import Colors
from Server import start_thread

CLIENT_PORT_UDP = 34342

# ---------------------helper functions-----------------------
def get_user_choices():
    data_size = input("Please enter size of data to download (in bytes): ")
    if(not data_size.strip().isdigit()): return None, 0, 0
    
    num_udp = input(f"Please enter number of {Colors.yellow_str('[UDP]')} connections to establish: ")
    if(not num_udp.strip().isdigit()): return 0, None, 0
    
    num_tcp = input(f"Please enter number of {Colors.red_str('[TCP]')} connections to establish: ")
    if(not num_tcp.strip().isdigit()): return 0, 0, None
    
    return data_size, num_udp, num_tcp

# ---------------------thread functions-----------------------
def listen_offers(port, data_size, num_udp, num_tcp):
    try:
        threads = []
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock: 
            sock.bind(('', port))
            # Wait for a message from a client
            data, server_address = sock.recvfrom(Parser.OFFER_HEADER_SIZE)  # buffer size is 1024 bytes
            if(len(data) != Parser.OFFER_HEADER_SIZE):
                #print(Colors.red_str(f"Error: size of request msg is not {Parser.REQUEST_HEADER_SIZE}"))
                return
            cookie, msg_type, file_size = Parser.unpack_request(data)
            if(cookie != Parser.MAGIC_COOKIE or msg_type != Parser.OFFER_TYPE):
                #print(Colors.red_str(f"Error: THE MAGIC COOKIE IS WRONG! ITS {cookie} != {Parser.MAGIC_COOKIE}"))
                return
            print(f"Received offer from {Colors.purple_str(str(server_address))}")
            
            for i in range(num_udp):
                threads.append(start_thread(download_udp, (sock, server_address, data_size)))
            for i in range(num_tcp):
                threads.append(start_thread(download_udp, (server_address, data_size)))
                
    except NameError:
        print(Colors.red_str(NameError))
        
def download_udp(sock, dest_addr, data_size):
    count_recieved = 0
    num_segs = -1
    expected_seg = 0
    num_missed = 0
    
    sock.sendto(Parser.pack_request(data_size), dest_addr)
    while(count_recieved < data_size):
        data, client_address = sock.recvfrom(Parser.PAYLOAD_SIZE)
        if(len(data) != Parser.PAYLOAD_HEADER_SIZE + data_size - count_recieved):
            #print(Colors.red_str(f"Error: size of payload msg is not {Parser.PAYLOAD_HEADER_SIZE + data_size - count_recieved}"))
            continue
        cookie, msg_type, segment_count, curr_segment, payload = Parser.unpack_payload_tcp(data)
        if(cookie != Parser.MAGIC_COOKIE or msg_type != Parser.PAYLOAD_FORMAT):
            #print(Colors.red_str(f"Error: THE MAGIC COOKIE IS WRONG! ITS {cookie} != {Parser.MAGIC_COOKIE}"))
            continue
        
        num_segs = segment_count
        num_missed += curr_segment - expected_seg
        expected_seg = curr_segment + 1
        print(f"recived {curr_segment-1}/{num_segs}")
        
def download_tcp(dest_addt, data_size):
    pass

# ---------------------main function---------------------
def main():
    while True:
        data_size, num_udp, num_tcp = get_user_choices()
        if(data_size == None):
            print(Colors.red_str("Size is not a number"))
            return
        elif(num_udp == None):
            print(Colors.red_str("Number of UDP connections is not a num"))
        elif(num_tcp == None):
            print(Colors.red_str("Number of TCP connections is not a num"))
        
        threads = listen_offers(CLIENT_PORT_UDP, data_size, num_udp, num_tcp)
        for thread in threads:
            thread.join()
    
        


# -------main condition---------
if __name__ == "__main__":
    HOSTNAME = socket.gethostname()
    HOST = socket.gethostbyname(HOSTNAME)
    main()
# -------end of file-------