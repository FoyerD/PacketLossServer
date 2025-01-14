import struct
#THE MAGICAL COOCKIE MADE FROM MAGICAL DOUGH MADE FROM MAGICAL FLOUR AND WATER (just nomal water not magical holy water)
MAGIC_COOKIE = 0xabcddcba

#The codes of differet messages types
OFFER_TYPE = 0x2
REQUEST_TYPE = 0x3
PAYLOAD_TYPE = 0x4

#The formats for packing/unpacking each type
OFFER_FORMAT = '!IBHH'
REQUEST_FORMAT = '!IBQ'
PAYLOAD_FORMAT = '!IBQQ'

#Sizes of each type of message
OFFER_HEADER_SIZE = 4+1+2+2
REQUEST_HEADER_SIZE = 4+1+8
PAYLOAD_HEADER_SIZE = 4+1+8+8



def pack_offer(udp_port, tcp_port):
    '''
    Returns a pakced bytes object of a offer message

    :param udp_port: the UDP port the server listens on, an unsigned int
    :param tcp_port: the TCP port the server listens on, an unsigned int
    :return: bytes object
    '''
    return struct.pack(OFFER_FORMAT, MAGIC_COOKIE, OFFER_TYPE, udp_port, tcp_port)

def pack_request(file_size):
    """Returns a paced bytes object of a request message"""
    return struct.pack(REQUEST_FORMAT, MAGIC_COOKIE, REQUEST_TYPE, file_size)

def pack_payload_tcp(segment_count, curr_segment, payload):
    '''Returns a paced bytes object of a request message'''
    return struct.pack(PAYLOAD_FORMAT, MAGIC_COOKIE, PAYLOAD_TYPE, segment_count, curr_segment) + payload.encode()

def unpack_offer(msg):
    '''Unpacks a offer msg (assumes it is correct)
    :return: (magic_cookie, offer_type, udp_port, tcp_port)
    '''
    return struct.unpack(OFFER_FORMAT, msg)

def unpack_request(msg):
    return struct.unpack(REQUEST_FORMAT, msg)

def unpack_payload_tcp(msg):
    return struct.unpack(PAYLOAD_FORMAT, msg[0:PAYLOAD_HEADER_SIZE]) + msg[PAYLOAD_HEADER_SIZE:]