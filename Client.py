import Parser
import socket
import Colors
from Server import start_thread
from Parser import CLIENT_PORT_UDP
import datetime
from tqdm import tqdm

# ---------------------helper functions-----------------------
def get_user_choices():
    data_size = input("Please enter size of data to download (in bytes): ")
    if(not data_size.strip().isdigit()): return None, 0, 0
    
    num_udp = input(f"Please enter number of {Colors.yellow_str('[UDP]')} connections to establish: ")
    if(not num_udp.strip().isdigit()): return 0, None, 0
    
    num_tcp = input(f"Please enter number of {Colors.red_str('[TCP]')} connections to establish: ")
    if(not num_tcp.strip().isdigit()): return 0, 0, None
    
    return int(data_size), int(num_udp), int(num_tcp)

# ---------------------thread functions-----------------------
def listen_offers(sock, data_size, num_udp, num_tcp):
    try:
        threads = []
        # Wait for a message from a client
        data, server_address = sock.recvfrom(Parser.OFFER_HEADER_SIZE)  # buffer size is 1024 bytes
        server_ip = server_address[0]
        if(len(data) != Parser.OFFER_HEADER_SIZE):
            #print(Colors.red_str(f"Error: size of request msg is not {Parser.REQUEST_HEADER_SIZE}"))
            return
        cookie, msg_type, server_udp_port, server_tcp_port = Parser.unpack_offer(data)
        if(cookie != Parser.MAGIC_COOKIE or msg_type != Parser.OFFER_TYPE):
            #print(Colors.red_str(f"Error: THE MAGIC COOKIE IS WRONG! ITS {cookie} != {Parser.MAGIC_COOKIE}"))
            return
        print(f"Received offer from {Colors.purple_str(str(server_address))}")
        
        for i in range(num_udp):
            threads.append(start_thread(download_udp, ((server_ip, server_udp_port), data_size)))
        for i in range(num_tcp):
            threads.append(start_thread(download_udp, ((server_ip, server_tcp_port), data_size)))
                
    except NameError:
        print(Colors.red_str(NameError))
    finally:
        return threads
        
def download_udp(dest_addr, data_size):
    count_recieved = 0
    num_segs = -1
    expected_seg = 0
    num_missed = 0
    start_time = 0
    curr_segment = 0;
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(1)
        sock.sendto(Parser.pack_request(data_size), dest_addr)
        start_time = datetime.datetime.now()
        for i in tqdm(range(data_size // (Parser.PAYLOAD_SIZE + Parser.PAYLOAD_HEADER_SIZE) + 1)):
            try:
                data, client_address = sock.recvfrom(Parser.PAYLOAD_SIZE + Parser.PAYLOAD_HEADER_SIZE)
            except socket.timeout:
                break
            except NameError:
                continue
            if(len(data) < Parser.PAYLOAD_HEADER_SIZE):
                #print(Colors.red_str(f"Error: size of payload msg is not {Parser.PAYLOAD_HEADER_SIZE + data_size - count_recieved}"))
                continue
            cookie, msg_type, segment_count, curr_segment, payload = Parser.unpack_payload_tcp(data)
            if(cookie != Parser.MAGIC_COOKIE or msg_type != Parser.PAYLOAD_TYPE):
                #print(Colors.red_str(f"Error: THE MAGIC COOKIE IS WRONG! ITS {cookie} != {Parser.MAGIC_COOKIE}"))
                continue
            
            num_segs = segment_count
            num_missed += curr_segment - expected_seg
            expected_seg = curr_segment + 1
            count_recieved += len(payload)
            if(curr_segment + 1 == num_segs):
                #print(f"{str(sock.getsockname)} recived {Colors.green_str(str(curr_segment+1))}/{Colors.green_str(str(num_segs))}")
                pass
            else:
                #print(f"{str(sock.getsockname)}recived {Colors.red_str(str(curr_segment+1))}/{Colors.green_str(str(num_segs))}")
                pass
    print(data_size - count_recieved)
    print(f"{str(sock.getsockname)} finished with rate of {str(count_recieved / (datetime.datetime.now()-start_time).total_seconds() + 0.000001)}[B/s]")
        
def download_tcp(dest_addt, data_size):
    pass

# ---------------------main function---------------------
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.bind(('', CLIENT_PORT_UDP))
        while True:
            data_size, num_udp, num_tcp = get_user_choices()
            if(data_size == None):
                print(Colors.red_str("Size is not a number"))
                return
            elif(num_udp == None):
                print(Colors.red_str("Number of UDP connections is not a num"))
            elif(num_tcp == None):
                print(Colors.red_str("Number of TCP connections is not a num"))
            if(num_tcp + num_udp <= 0): continue
            print(f"Client started, listening for offer requests on {Colors.blue_str(f'({HOST},{CLIENT_PORT_UDP})')}...")
            threads = listen_offers(sock, data_size, num_udp, num_tcp)
            for thread in threads:
                thread.join()
    
        


# -------main condition---------
if __name__ == "__main__":
    HOSTNAME = socket.gethostname()
    HOST = socket.gethostbyname(HOSTNAME)
    main()
# -------end of file-------