import json
import pytest
import socket
import socketserver
import threading
import time
from collections import deque
from serve_the_servants import TheServant
from database import DatabaseHandler


request_result = []


@pytest.fixture()
def requests():
    jspush1 = json.dumps({'query': 'location_push', 'location': {'latitude': 1, 'longitude': 1, 'username': 'Johnny', 'uniqueID': 12874}}) + '\n'
    jspush2 = json.dumps({'query': 'location_push', 'location': {'latitude': -14.43, 'longitude': 25.2, 'username': 'John', 'uniqueID': 15322}}) + '\n'
    jspush3 = json.dumps({'query': 'location_push', 'location': {'latitude': 17.5, 'longitude': 51.13, 'username': 'George', 'uniqueID': 10573}}) + '\n'
    jspull = json.dumps({'query': 'location_pull', 'usernames': ['Johnny', 'John', 'George']}) + '\n'
    requests_list = deque([jspush1, jspush2, jspush3, jspull])
    return requests_list


def request(requests):
    global request_result
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5001))
    client.send(bytearray(requests.popleft(), 'utf-8'))
    request_result.append(client.recv(4096))
    client.close()
    time.sleep(2)
    if len(requests) >= 1:
        request(requests)


@pytest.fixture(scope="module")
def server():
    DatabaseHandler.db_name = "test_database1.db"
    db = DatabaseHandler()
    db.connect()
    db.db.insert("users", "uniqueID", "12874", "username", "Johnny", "password", "123456789")
    db.db.insert("users", "uniqueID", "15322", "username", "John", "password", "123456789")
    db.db.insert("users", "uniqueID", "10573", "username", "George", "password", "123456789")
    db.close()
    server = socketserver.TCPServer(("", 5001), TheServant)
    return server


@pytest.fixture()
def serverServeForever(server):

    def server_task():
        server.serve_forever()

    return server_task


def test_server_fat(server, serverServeForever, requests):
    server_thread = threading.Thread(target=serverServeForever, name="TestServerThread")
    request_thread = threading.Thread(target=request, name="TestRequests", args=[(requests)])
    server_thread.setDaemon(True)
    request_thread.setDaemon(True)
    server_thread.start()
    time.sleep(2)
    request_thread.start()
    request_thread.join()
    server.shutdown()
    server_thread.join()
    print(request_result)
