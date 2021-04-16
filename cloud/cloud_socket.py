import socketserver
import tqdm
import os

SEPARATOR = "<SEPARATOR>"
# receive 4096 bytes each time
BUFFER_SIZE = 4096

# device's IP address
server_host = "0.0.0.0"
server_post = 5001


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # receive the file infos
        # receive using client socket, not server socket

        received = self.request.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        # convert to integer
        filesize = int(filesize)

        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                # read bytes from the socket (receive)
                bytes_read = self.request.recv(BUFFER_SIZE)
                if not bytes_read:
                    # nothing is received
                    # file transmitting is done
                    progress.close()
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))


class Cloud:
    def __init__(self):
        # Create the server, binding to localhost on port 9999
        with socketserver.TCPServer((server_host, server_post), MyTCPHandler) as server:
            print(f"[Cloud] Listening as {server_host}:{server_post}")

            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()
