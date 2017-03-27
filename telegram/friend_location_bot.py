from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.forcereply import ForceReply

from socket import socket

import socket
import json
import key_extractor

class FriendLocationBot:
    def __init__(self, telegramToken, googleKey):
        self.backend_addr = "archoniii.ddns.net"
        self.backend_port = 30000
        self.buffer_size = 4096

        self.baseUrl = "https://maps.googleapis.com/maps/api/staticmap"
        self.key = googleKey

        self.areas = {
            "berlin": [13.082634, 13.766688, 52.337776, 52.676643],
            "tu": [13.319462, 13.331812, 52.509221, 52.517618]
        }

        self.locationArray = []

        start_handler = CommandHandler('start', self.start)
        loc_handler = CommandHandler('me', self.askLoc)
        makemap_handler = CommandHandler('now', self.giveLocs)
        locadd_handler = MessageHandler(Filters.location, self.getLoc)

        self.updater = Updater(token=telegramToken)
        dispatcher = self.updater.dispatcher

        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(loc_handler)
        dispatcher.add_handler(locadd_handler)
        dispatcher.add_handler(makemap_handler)

    def run(self):
        self.updater.start_polling()

    def start(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
            text="Ok, I'll need to gather all of your locations, if you want"
            + " to participate, send me the command /me")
        self.locationArray = []

    def askLoc(self, bot, update):
        user = update.message.from_user.first_name
        
        bot.sendMessage(chat_id=update.message.chat_id, 
            reply_markup=ForceReply(force_reply=True, selective = True),
            reply_to_message_id=update.message.message_id,
            text="Send me your location, " + user)

    def getLoc(self, bot, update):
        userName = update.message.from_user.first_name
        userId  = update.message.from_user.id
        longitude = update.message.location.longitude
        latitude  = update.message.location.latitude

        minLong = self.areas["berlin"][0]
        maxLong = self.areas["berlin"][1]
        minLat = self.areas["berlin"][2]
        maxLat = self.areas["berlin"][3]

        if (longitude < minLong or longitude > maxLong
            or latitude < minLat or latitude > maxLat):
            text = "I didn't add the location you provided because it is outside of Berlin."
            text += " Please give me a location in Berlin"

            bot.sendMessage(chat_id=update.message.chat_id, 
                reply_to_message_id=update.message.message_id,
                text=text)

            return

        locObj = {
            "id" : userId,
            "userName": userName,
            "longitude" : longitude,
            "latitude"  : latitude
        }

        upD = [obj for obj in self.locationArray if obj["id"] == locObj["id"]]
            
        if len(upD) == 0:
            self.locationArray.append(locObj)
            
            text = "Added " + locObj["userName"]
            text += " at location " + str(locObj["longitude"])
            text += ", " + str(locObj["latitude"])
        else:
            upD[0]["latitude"] = locObj["latitude"]
            upD[0]["longitude"] = locObj["longitude"]
 
            text = "Updated location of " + upD[0]["userName"]
            text += " to " + str(upD[0]["latitude"])
            text += ", " + str(upD[0]["longitude"])

        bot.sendMessage(chat_id=update.message.chat_id, text=text)

    def giveLocs(self, bot, update):
        args = update.message.text.split(" ")

        availableLocs = []

        if len(args) > 1:
            if args[1].lower() in self.areas.keys():
                area = self.areas[args[1].lower()]
                
                minLong = area[0]
                maxLong = area[1]
                minLat = area[2]
                maxLat = area[3]

                for loc in self.locationArray:
                    longitude = loc["longitude"]
                    latitude = loc["latitude"]

                    if (longitude >= minLong and longitude <= maxLong
                        and latitude >= minLat and latitude <= maxLat):
                        availableLocs.append(loc)

                if len(availableLocs) == 0:
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
            availableLocs = self.locationArray

        url = self.constructUrl(availableLocs)
        bot.sendPhoto(chat_id=update.message.chat_id, photo=url)

        # Apology to Luis
        if "luis" in update.message.from_user.first_name.lower():
            bot.sendMessage(chat_id=update.message.chat_id,
                reply_to_message_id=update.message.message_id,
                text="Sorry for being rude to you Luis. Will you forgive me?")

    # Unused altervative to giveLocs for use with The Backend
    def giveLocs2(self, bot, update):
        args = update.message.text.split(" ")

        availableLocs = []

        # Pull locations from The Backend
        with socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # We need to figure out how to populate "usernames"
            query = {"query" : "location_pull", "usernames" : []}

            try:
                s.connect((self.backend_addr, self.backend_port))
                s.send(bytearray(json.dumps(query), "utf-8"))
                response = json.loads(s.recv(self.buffer_size))
                availableLocs = response["locations"]
            except:
                # For now
                pass

        if len(availableLocs) == 0:
            bot.sendMessage(chat_id=update.message.chat_id, 
                reply_to_message_id=update.message.message_id,
                text="None of your friends are currently in this area")    
            return

        url = self.constructUrl(availableLocs)
        bot.sendPhoto(chat_id=update.message.chat_id, photo=url)

    def constructUrl(self, locations):
        url = self.baseUrl + '?'
        url += 'size=1024x1024&'
        center = self.calculateCenter(locations)
        url += 'center='
        url += str(center[0])
        url += ','
        url += str(center[1])
        url += '&'
        url += 'key=' + self.key
        url += '&'

        # Add all the longs and lats for each location object
        for obj in locations:
            url += 'markers=icon:https://chart.googleapis.com/chart?chst=d_bubble_text_small%26chld=bbT%257C'
            url += str(obj["userName"])
            url += '%257CB8EDFF%257C000000'
            url += '%7C'
            url += str(obj["latitude"])
            url += ','
            url += str(obj["longitude"])
            url += '&'

        return url

    def calculateCenter(self, locations):
        maxY = max([obj["longitude"] for obj in locations])
        minY = min([obj["longitude"] for obj in locations])
        maxX = max([obj["latitude"] for obj in locations])
        minX = min([obj["latitude"] for obj in locations])
        
        centerY = (maxY + minY) / 2
        centerX = (maxX + minX) / 2
        
        return (centerX, centerY)

if __name__ == "__main__":
    flb = FriendLocationBot(key_extractor.getKey("telegram"),
        key_extractor.getKey("google"))
    flb.run()
