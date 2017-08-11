import signal
import socketserver
from server.serve_the_servants import TheServant


def runServer():
    port = 5000
    server = socketserver.TCPServer(("", port), TheServant)

    def terminateHandler(*ignored):
        server.shutdown()
        print("Server shutdown.")

    signal.signal(signal.SIGTERM, terminateHandler)
    signal.signal(signal.SIGINT, terminateHandler)
    print("Starting server on port: {}".format(port))
    server.serve_forever()
