from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.forcereply import ForceReply

from socket import socket
from database import Database

import socket
import json
import key_extractor

class FriendLocationBot:
    def __init__(self, telegram_token, google_key):
        self.backend_address = "localhost"
        self.backend_port = 5000
        self.buffer_size = 4096

        self.base_url = "https://maps.googleapis.com/maps/api/staticmap"
        self.key = google_key

        self.areas = {
            "berlin": [13.082634, 13.766688, 52.337776, 52.676643],
            "tu": [13.319462, 13.331812, 52.509221, 52.517618]
        }

        self.updater = Updater(token=telegram_token)
        dispatcher = self.updater.dispatcher

        dispatcher.add_handler(CommandHandler("me", self.register_user))
        dispatcher.add_handler(CommandHandler("out", self.unregister_user))
        dispatcher.add_handler(CommandHandler("now", self.give_locations))
        dispatcher.add_handler(CommandHandler("help", self.start))
        dispatcher.add_handler(MessageHandler(Filters.location, self.get_location))
        dispatcher.add_handler(MessageHandler(Filters.status_update, self.start))

    def run(self):
        self.the_database = Database()
        self.the_database.connect()
        self.updater.start_polling()
        self.updater.idle()
        self.the_database.close()

    def start(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
            text=("Hi. I'm the Friend Location Bot."
                " The following commands are available:\n\n"
                "- /me Register yourself in this group. This means"
                "that others in the group will be able to get your location.\n"
                "- /out Unregister yourself out of this group. Others"
                "in the group will not be able to get your location.\n"
                "- /now Get a picture showing the locations of all registered users"
                "in this group\n"
                "- /help Show this message :)"))

    def register_user(self, bot, update):
        user = update.message.from_user
        first_name = user.first_name
        chat_id = update.message.chat_id

        username = user.username
        if username == "":
            username = first_name

        if update.message.chat.type == "group":
            self.the_database.register_user(user.id, username, chat_id)
        
            bot.sendMessage(chat_id=chat_id, 
                text="Registered user %s" % username)
        else:
            bot.sendMessage(chat_id=chat_id, text="I only work for groups")

    def unregister_user(self, bot, update):
        user = update.message.from_user
        first_name = user.first_name
        chat_id = update.message.chat_id

        username = user.username
        if username is None:
            username = first_name

        self.the_database.unregister_user(user.id, chat_id)

        bot.sendMessage(chat_id=chat_id, text="Unregistered user %s" % username)

    def get_location(self, bot, update):
        message = update.message
        user = message.from_user

        username = user.username
        if username == "":
            username = user.first_name

        longitude = message.location.longitude
        latitude  = message.location.latitude

        min_long = self.areas["berlin"][0]
        max_long = self.areas["berlin"][1]
        min_lat = self.areas["berlin"][2]
        max_lat = self.areas["berlin"][3]

        if (longitude < min_long or longitude > max_long
            or latitude < min_lat or latitude > max_lat):
            text = """I didn't add the location you provided because it is outside of Berlin.
                Please give me a location in Berlin"""

            bot.sendMessage(chat_id=update.message.chat_id, 
                reply_to_message_id=update.message.message_id,
                text=text)

            return

        location_object = {
            "username": username,
            "longitude" : longitude,
            "latitude"  : latitude
        }

        query = {"query" : "location_push", "location" : location_object}

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.backend_address, self.backend_port))
                s.send(bytearray(json.dumps(query) + "\n", "utf-8"))
                response = json.loads(str(s.recv(self.buffer_size), encoding="utf-8"))
                if response["ok"] == True:
                    text = "Updated location of " + user.first_name
                    text += " to " + str(longitude)
                    text += ", " + str(latitude)
                    bot.sendMessage(chat_id=message.chat_id, text=text)
                else:
                    bot.sendMessage(chat_id=message.chat_id,
                        text="Failed to update location of " + location_object["username"])
            except:
                # For now
                pass

    def give_locations(self, bot, update):
        args = update.message.text.split(" ")

        location_array = []
        available_locations = []

        usernames = self.the_database.fetch_users(update.message.chat_id)
        query = {"query" : "location_pull", "usernames" : usernames}

        # Pull locations from The Backend
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.backend_address, self.backend_port))
                s.send(bytearray(json.dumps(query) + "\n", "utf-8"))
                response = json.loads(str(s.recv(self.buffer_size), encoding="utf-8"))
                location_array = response["locations"]
            except:
                # For now
                pass

        if len(args) > 1:
            if args[1].lower() in self.areas.keys():
                area = self.areas[args[1].lower()]
                
                min_long = area[0]
                max_long = area[1]
                min_lat = area[2]
                max_lat = area[3]

                for loc in location_array:
                    longitude = loc["longitude"]
                    latitude = loc["latitude"]

                    if (longitude >= min_long and longitude <= max_long
                        and latitude >= min_lat and latitude <= max_lat):
                        available_locations.append(loc)

                if len(available_locations) == 0:
                    bot.sendMessage(chat_id=update.message.chat_id,
                        reply_to_message_id=update.message.message_id,
                        text="None of your friends are currently in this area")
                    return            
            else:
                bot.sendMessage(chat_id=update.message.chat_id,
                    reply_to_message_id=update.message.message_id,
                    text="I don't know this area")
                return
        else:
            available_locations = location_array

        url = self.construct_url(available_locations)
        bot.sendPhoto(chat_id=update.message.chat_id, photo=url)

        # Apology to Luis
        if "luis" in update.message.from_user.first_name.lower():
            bot.sendMessage(chat_id=update.message.chat_id,
                reply_to_message_id=update.message.message_id,
                text="Sorry for being rude to you Luis. Will you forgive me?")

    def construct_url(self, locations):
        center = self.calculate_center(locations)
        url = "%s?size=1024x1024&center=%f,%f&key=%s&" % (self.base_url,
            center[0], center[1], self.key)

        # Add all the longs and lats for each location object
        for location in locations:
            url += ("markers=icon:https://chart.googleapis.com/chart"
                    "?chst=d_bubble_text_small%%26chld=bbT%%257C"
                    "%s%%257CB8EDFF%%257C000000%%7C%f,%f&") % (location["username"],
                    location["latitude"], location["longitude"])

        return url

    def calculate_center(self, locations):
        maxY = max([location["longitude"] for location in locations])
        minY = min([location["longitude"] for location in locations])
        maxX = max([location["latitude"] for location in locations])
        minX = min([location["latitude"] for location in locations])
        
        centerY = (maxY + minY) / 2
        centerX = (maxX + minX) / 2
        
        return (centerX, centerY)

if __name__ == "__main__":
    flb = FriendLocationBot(key_extractor.get_key("telegram"),
        key_extractor.get_key("google"))
    flb.run()
