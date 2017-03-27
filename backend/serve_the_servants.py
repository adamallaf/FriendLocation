import socketserver, json
from backend import LocationPoint, Database

# Class for the bad request errors, in order to handle exceptions 
class BadRequestError(Exception):
    def __init__(self, typ):
        self.typ = typ

class TheServant(socketserver.StreamRequestHandler):
    the_database = Database()

    # handle requests
    def handle(self):
        try:
            print("incoming connection ")
            self._getReq()
        except BadRequestError as e:
            print(e.typ)

    # send a response. Takes a json object as paramter

    def _getReq(self):
        # List of supported requests, each term in the dictionary matches to a
        # method (this is our proper handler for each type of request)
        SUPPORTED_REQUESTS = {"location_push" : self.do_push, "location_pull": self.do_pull}
        # parse the request
        req = self.rfile.readline().strip().decode('utf-8')
        try:
            # Try to load the request and execute the method defined by it
            jsonObj = json.loads(req)
            print("json parsed")
            SUPPORTED_REQUESTS[jsonObj['query']](jsonObj)
        except json.decoder.JSONDecodeError:
            raise BadRequestError("Not JSON")
        except KeyError:
            raise BadRequestError("Bad Formatted Request")
                
    def _sendResponse(self, jsResp):
        self.wfile.write(bytearray(jsResp, 'utf-8'))

    # Insert a location object into the database
    def do_push(self, jsonObj):
        print("trying push")
        try:
            # try to parse the location Object
            location = jsonObj["location"]

        except KeyError:
            #in case one of the necessary formats is not found
            raise BadRequestError("No location field inside request")
        else:
            # create the location Object
            try:
                username = location["username"]
                longitude = location["longitude"]
                latitude = location["latitude"]
            except KeyError:
                raise BadRequestError("Bad formatted location Object") 
                jsonResp = json.dumps({'ok':False})
            else: 
                # create a location Object
                locObj = LocationPoint(username, longitude, latitude)

                # insert the object into the database
                self.the_database.insert(locObj)
                print("added the following ", locObj.username)
                # generate and send the json response
                jsonResp = json.dumps({'ok':True})
            self._sendResponse(jsonResp)

    # Handle the pull requests
    def do_pull(self, jsonObj):
        try:
            #fetch the location for each user
            usernames = jsonObj["usernames"]
        except KeyError:
            raise BadRequestError("No field usernames")
        else:
            # initialize an empty list with the results
            results = []
            # get the matches from the database
            for uname in usernames:
                results.append(self.the_database.query_username(uname).to_json())
            # in case 1 element was not found
            if None in results:
                jsonResp = json.dumps({'ok': False})
            else:
                # generate the json response
                jsonResp = json.dumps({'ok': True, 'locations' : results})
                # send the response
                self._sendResponse(jsonResp)

server = socketserver.TCPServer(("0.0.0.0", 5000), TheServant)
server.serve_forever()
