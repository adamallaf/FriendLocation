import socketserver, json
from backend import LocationPoint
from database import Database

# Class for the bad request errors, in order to handle exceptions 
class BadRequestError(Exception):
    def __init__(self, error_message):
        self.error_message = error_message

class TheServant(socketserver.StreamRequestHandler):
    def setup(self):
        socketserver.StreamRequestHandler.setup(self)
        self.the_database = Database()
        self.the_database.connect()

    def finish(self):
        socketserver.StreamRequestHandler.finish(self)
        self.the_database.close()

    # handle requests
    def handle(self):
        try:
            print("Incoming connection...")
            self._getReq()
        except BadRequestError as e:
            print(e.error_message)

    # send a response. Takes a json object as paramter

    def _getReq(self):
        # List of supported requests, each term in the dictionary matches to a
        # method (this is our proper handler for each type of request)
        SUPPORTED_REQUESTS = {"location_push" : self.do_push, "location_pull": self.do_pull}
        # parse the request
        req = self.rfile.readline().strip().decode('utf-8')
        try:
            # Try to load the request and execute the method defined by it
            json_object = json.loads(req)
            print("JSON parsed")
            SUPPORTED_REQUESTS[json_object['query']](json_object)
        except ValueError:
             raise BadRequestError("Not JSON")
        except KeyError:
            raise BadRequestError("Bad Formatted Request")
                
    def _sendResponse(self, json_response):
        self.wfile.write(bytearray(json_response, 'utf-8'))

    # Insert a location object into the database
    def do_push(self, json_object):
        print("Trying push...")
        try:
            # Try to parse the location object
            location = json_object["location"]
        except KeyError:
            # In case one of the necessary formats is not found
            raise BadRequestError("No location field inside request")
        else:
            # Create the location Object
            try:
                username = location["username"]
                longitude = location["longitude"]
                latitude = location["latitude"]
            except KeyError:
                raise BadRequestError("Bad formatted location Object") 
                json_response = json.dumps({'ok': False})
            else: 
                # Create a location Object
                location_object = LocationPoint(username, longitude, latitude)

                # insert the object into the database
                self.the_database.push(location_object)
                print("Added the following ", location_object.username)
                # Generate and send the JSON response
                json_response = json.dumps({'ok': True})
            self._sendResponse(json_response)

    # Handle the pull requests
    def do_pull(self, json_object):
        try:
            # Fetch the location for each user
            usernames = json_object["usernames"]
        except KeyError:
            raise BadRequestError("No field \"usernames\"")
        else:
            # Get the matches from the database
            results = self.the_database.pull(usernames)
            # Generate the JSON response
            json_response = json.dumps({'ok': True, 'locations' : results})
            # Send the response
            self._sendResponse(json_response)

server = socketserver.TCPServer(("", 5000), TheServant)
server.serve_forever()
