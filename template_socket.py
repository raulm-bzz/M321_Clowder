""" Socket-controller for the TemplateBot """
from raulsbot import RaulsBot
import selectors
import socket
import traceback
from client_message import ClientMessage
from server_message import ServerMessage



def main():
    """
    main function for the socket-controller
    :return:
    """
    bot = RaulsBot("RaulsBot")

    item = {'action': 'MEOW', 'ip': '192.168.99.155', 'name': 'RaulsBot', 'type': 'bot'}
    print(f'registering service: {item["type"]} {item["ip"]}')
    new_port = send_request(item)
    new_port = int(new_port)

    sel = selectors.DefaultSelector()


    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((OWN, new_port))
    lsock.listen()
    print(f'Listening on {(OWN, new_port)}')
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(sel, key.fileobj)
                else:
                    message = key.data
                    try:
                        message.process_events(mask)
                        message.response = bot.request(message) #muss JSON zurück geben


                    except Exception:
                        print(
                            f'Main: Error: Exception for {message.ipaddr}:\n'
                            f'{traceback.format_exc()}'
                        )
                        message._close()
    except KeyboardInterrupt:
        print('Caught keyboard interrupt, exiting')
    finally:
        sel.close()


    # register the bot with the clowder => you get a port number
    # open a socket with the port number
        # listen for incoming connections from the arena
        # analyse the incoming connections
        # call the relevant bot method depending on the action
        # send the response back to the arena

#OWN = '192.168.99.155'
#HOST = "192.168.99.208"

OWN = '127.0.0.1'
HOST = '127.0.0.1'

PORT = 65432
def send_request(action):
    global new_port
    sel = selectors.DefaultSelector()
    request = create_request(action)
    start_connection(sel, HOST, PORT, request)

    try:
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                    new_port = str(message.response)
                    new_port = new_port[2:-1]
                except Exception:
                    print(
                        f'Main: Error: Exception for {message.ipaddr}:\n'
                        f'{traceback.format_exc()}'
                    )
                    message._close()
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print('Caught keyboard interrupt, exiting')
    finally:
        print(f'-----------\n{new_port}\n-----------')
        sel.close()
        return new_port




def create_request(action_item):
    return dict(
        type='text/json',
        encoding='utf-8',
        content=action_item,
    )
def start_connection(sel, host, port, request):
    addr = (host, port)
    print(f'Starting connection to {addr}')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = ClientMessage(sel, sock, addr, request)
    sel.register(sock, events, data=message)


def accept_wrapper(sel, sock):
    conn, addr = sock.accept()
    print(f'Accepted connection from {addr}')
    conn.setblocking(False)
    message = ServerMessage(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)


if __name__ == '__main__':
    main()