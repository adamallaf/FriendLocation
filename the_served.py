import socket,json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost",80))
#jspull = json.dumps({'query':'location_push', 'location': {'latitude': 2,'longitude': 3, 'username': 'chavezgt'}})
jspull = json.dumps({'query':'location_pull', 'usernames':['chavezgt']})
#js = json.dumps{'2':2},fp=s)
##s.send(bytearray(js,'utf-8'))
s.send(bytearray(jspull,'utf-8'))
#s.send(bytearray("putoooo",'utf-8'))
s.close()


