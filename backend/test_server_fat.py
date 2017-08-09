import json
import os
import pytest
import socket
import socketserver
import threading
import time
from collections import deque
from serve_the_servants import TheServant
from database import DatabaseHandler


request_results = deque()


@pytest.fixture()
def requests():
    jspush1 = json.dumps({'query': 'location_push', 'location': {'latitude': 1, 'longitude': 1, 'username': 'Johnny', 'uniqueID': 12874}}) + '\n'
    jspush2 = json.dumps({'query': 'location_push', 'location': {'latitude': -14.43, 'longitude': 25.2, 'username': 'John', 'uniqueID': 15322}}) + '\n'
    jspush3 = json.dumps({'query': 'location_push', 'location': {'latitude': 17.5, 'longitude': 51.13, 'username': 'George', 'uniqueID': 10573}}) + '\n'
    jspull = json.dumps({'query': 'location_pull', 'usernames': ['Johnny', 'John', 'George']}) + '\n'
    requests_list = deque([jspush1, jspush2, jspush3, jspull])
    return requests_list


def sendRequests(requests):
    global request_results
    for req in requests:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 5001))
        client.send(bytearray(req, 'utf-8'))
        request_results.append(client.recv(4096))
        client.close()


@pytest.fixture(scope="module")
def server(request):
    db_path = os.path.join(os.getenv("TMP"), "test_database.db")
    DatabaseHandler.db_name = db_path
    db = DatabaseHandler()
    db.connect()
    db.db.insert("users", "uniqueID", "12874", "username", "Johnny", "password", "123456789")
    db.db.insert("users", "uniqueID", "15322", "username", "John", "password", "123456789")
    db.db.insert("users", "uniqueID", "10573", "username", "George", "password", "123456789")
    db.close()
    server = socketserver.TCPServer(("", 5001), TheServant)

    def cleanup():
        os.remove(db_path)

    request.addfinalizer(cleanup)
    return server


@pytest.fixture()
def serverServeForever(server):

    def server_task():
        server.serve_forever()

    return server_task


def test_server_fat(server, serverServeForever, requests):
    js_pull_response = b'{"ok": true, "locations": [{"username": "Johnny", "longitude": 1.0, "latitude": 1.0},' \
                       b' {"username": "John", "longitude": 25.2, "latitude": -14.43}, {"username": "George", "longitude": 51.13, "latitude": 17.5}]}'
    server_thread = threading.Thread(target=serverServeForever, name="TestServerThread")
    request_thread = threading.Thread(target=sendRequests, name="TestRequests", args=[requests])
    server_thread.setDaemon(True)
    request_thread.setDaemon(True)
    server_thread.start()
    time.sleep(1)
    request_thread.start()
    request_thread.join()
    server.shutdown()
    server_thread.join()
    assert request_results.pop() == js_pull_response
