import json
import socket
import socketserver
import threading

import os
import pytest
from collections import deque
from database import DatabaseHandler
from server.serve_the_servants import TheServant

request_results = deque()


@pytest.fixture()
def requests():
    jspush1 = json.dumps({'query': 'location_push', 'location': {'latitude': 1, 'longitude': 1, 'username': 'Johnny', 'uniqueID': 12874}}) + '\n'
    jspush2 = json.dumps({'query': 'location_push', 'location': {'latitude': -14.26, 'longitude': 26.8, 'username': 'John', 'uniqueID': 15322}}) + '\n'
    jspush4 = json.dumps({'query': 'location_push', 'location': {'latitude': -13.55, 'longitude': 27.33, 'username': 'John', 'uniqueID': 15322}}) + '\n'
    jspush5 = json.dumps({'query': 'location_push', 'location': {'latitude': -14.43, 'longitude': 25.2, 'username': 'John', 'uniqueID': 15322}}) + '\n'
    jspush3 = json.dumps({'query': 'location_push', 'location': {'latitude': 17.5, 'longitude': 51.13, 'username': 'George', 'uniqueID': 10573}}) + '\n'
    jspull = json.dumps({'query': 'location_pull', 'usernames': ['Johnny', 'John', 'George']}) + '\n'
    requests_list = deque([jspush1, jspush2, jspush3, jspush4, jspush5, jspull])
    return requests_list


def sendRequests(requests):
    global request_results
    for req in requests:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 5001))
        client.send(bytearray(req, 'utf-8'))
        request_results.append(client.recv(4096))
        client.close()


def populateDatabase():
    db = DatabaseHandler()
    db.connect()
    db.db.insert("users", "uniqueID", "12874", "username", "Johnny", "password", "123456789")
    db.db.insert("users", "uniqueID", "15322", "username", "John", "password", "123456789")
    db.db.insert("users", "uniqueID", "10573", "username", "George", "password", "123456789")
    db.close()


@pytest.fixture(scope="module")
def server(request):
    db_path = os.path.join(os.getenv("TMP"), "test_database.db")
    DatabaseHandler.db_name = db_path
    populateDatabase()
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
    js_pull_response = b'{"ok": true, "locations": [{"username": "Johnny", "latitude": 1.0, "longitude": 1.0},' \
                       b' {"username": "John", "latitude": -14.43, "longitude": 25.2}, {"username": "George", "latitude": 17.5, "longitude": 51.13}]}'
    server_thread = threading.Thread(target=serverServeForever, name="TestServerThread")
    server_thread.setDaemon(True)
    server_thread.start()
    sendRequests(requests)
    server.shutdown()
    server_thread.join()
    print(js_pull_response)
    assert request_results.pop() == js_pull_response
