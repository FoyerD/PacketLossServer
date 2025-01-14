import struct
MAGIC_COOKIE = 0xabcddcba
OFFER_TYPE = 0x2

def make_offer(udp_port, tcp_port):
    return struct.pack('!IBHH', MAGIC_COOKIE, OFFER_TYPE, udp_port, tcp_port)

