import json
import socket
import time


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 5000))
# s.connect(("localhost", 80))
# jspull = json.dumps({'query':'location_push', 'location': {'latitude': 2,'longitude': 3, 'username': 'Johnny', 'uniqueID': 12874}})
# jspull +='\n'
# s.send(bytearray(jspull,'utf-8') )
# print(s.recv(4096))
# time.sleep(5)
# jspull = json.dumps({'query':'location_push', 'location': {'latitude': 76,'longitude': 34, 'username': 'John', 'uniqueID': 15322}})
# jspull +='\n'
# s.send(bytearray(jspull,'utf-8') )
# print(s.recv(4096))
# time.sleep(5)
# jspull = json.dumps({'query':'location_push', 'location': {'latitude': 76,'longitude': 34, 'username': 'Goerge', 'uniqueID': 10573}})
# jspull +='\n'
# s.send(bytearray(jspull,'utf-8') )
# print(s.recv(4096))
# time.sleep(5)

jspull = json.dumps({'query':'location_pull','usernames': ['Johnny', 'John', 'Goerge']} )
jspull +='\n'
s.send(bytearray(jspull,'utf-8'))
print(s.recv(4096))

#js = json.dumps{'2':2},fp=s)
##s.send(bytearray(js,'utf-8'))
#s.send(bytearray("putoooo",'utf-8'))
s.close()


