from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.forcereply import ForceReply

import key_extractor
class FriendLocationBot:
    def __init__(self, telegramToken, googleKey):
        #set the necessary parameters to access the maps API
        self.baseUrl = 'https://maps.googleapis.com/maps/api/staticmap'
        self.key = googleKey

        #Define the areas known to the bot
        self.areas = {
            "berlin": LocationArea(13.082634, 13.766688, 52.337776, 52.676643),
            "tu": LocationArea(13.319462, 13.331812, 52.509221, 52.517618)
        }

    self.locationArray = []

        #define all the handlers and associate them to the respective
        #functions
        start_handler = CommandHandler('start', self.start)
        loc_handler = CommandHandler('me', self.askLoc)
        info_handler = CommandHandler('info', self.infoList)
        makemap_handler = CommandHandler('now', self.giveLocs)
        locadd_handler = MessageHandler(Filters.location, self.getLoc)


        #Create the Updater and dispatcher object
        self.updater = Updater(token=telegramToken)
        dispatcher = self.updater.dispatcher

        #Add all the handlers to the dispatcher
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(info_handler)
        dispatcher.add_handler(loc_handler)
        dispatcher.add_handler(locadd_handler)
        dispatcher.add_handler(makemap_handler)

    #start the bot and get Updates
    def run(self):
        self.updater.start_polling()

    #Function for start handler, resets the location Array to an empty list
    #command '/start'
    def start(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
            text="Ok, I'll need to gather all of your locations, if you want"
            + " to participate, send me the command /me")
        self.locationArray = []

    #Ask the user for his location as a reply command '/me'
    def askLoc(self, bot, update):
        user = update.message.from_user.first_name
        
        bot.sendMessage(chat_id=update.message.chat_id, 
            reply_markup=ForceReply(force_reply=True, selective = True),
            reply_to_message_id=update.message.message_id,
            text="Send me your location, " + user)

    #Gets the location by the user, sent after /askloc
    def getLoc(self, bot, update):
        userName = update.message.from_user.first_name
        userId  = update.message.from_user.id
        timeStamp = update.message.date
        longitude = update.message.location.longitude
        latitude  = update.message.location.latitude

        #Create a LocationPoint object with the necessary info
        locObj = LocationPoint(userName, userId, timeStamp, longitude, latitude) 

        #Checks if the point is inside the area "berlin"
        if (not(self.areas["berlin"].isInside(locObj))):
            text = "I didn't add the location you provided because it is outside of Berlin."
            text += " Please give me a location in Berlin"

            bot.sendMessage(chat_id=update.message.chat_id, 
                reply_to_message_id=update.message.message_id,
                text=text)

            return


        #Return List with the objects with the same userId
        #Check to see if the user sends his location for the first time
        #or just updates it
        upD = [obj for obj in self.locationArray if obj.userId == locObj.userId]
            
        #List is empty, create the location
        if len(upD) == 0:
            self.locationArray.append(locObj)
            
            text = "Added " + locObj.userName
            text += " at location " + str(locObj.longitude)
            text += ", " + str(locObj.latitude)
        #List is not empty, update location
        else:
            upObj = upD[0]
            upObj.moveTo(locObj.longitude, locObj.latitude)
 
            text = "Updated location of " + upObj.userName
            text += " to " + str(upObj.latitude)
            text += ", " + str(upObj.longitude)

        bot.sendMessage(chat_id=update.message.chat_id, text=text)

    def infoList(self, bot, update):
        text = "User's available \n"
        for loc in self.locationArray:
            text += loc.userName 
            text += " last seen " 
            text += str(loc.timeStamp)
            text += "\n"
        bot.sendMessage(chat_id=update.message.chat_id, text=text)


    #return the generated map with all the locations
    def giveLocs(self, bot, update):
        #Args to see if the call wants only a specific area
        args = update.message.text.split(" ")

        #Temporary list to save the locations to be returned
        availableLocs = []

        #User wants to query for a particular area
        if len(args) > 1:
            if args[1].lower() in self.areas.keys():
                area = self.areas[args[1].lower()]
                
                #Checks one by one if the locations are inside of the area
                for loc in self.locationArray:
                    if area.isInside(loc):
                        availableLocs.append(loc)

                #List is empty, user has no friends
                if len(availableLocs) == 0:
                    bot.sendMessage(chat_id=update.message.chat_id, 
                        reply_to_message_id=update.message.message_id,
                        text="None of your friends are currently in this area")    
                    return            
            else:
                #User is retarded or on drugs: Area doesn't exist
                bot.sendMessage(chat_id=update.message.chat_id, 
                    reply_to_message_id=update.message.message_id,
                    text="I don't know this area")
                return
        else:
            #Simply return all the locations
            availableLocs = self.locationArray
            if(not(availableLocs)):
                bot.sendMessage(chat_id=update.message.chat_id, 
                    reply_to_message_id=update.message.message_id,
                    text="You have no friends, or they just simply haven't " +
                    "added their location"
                    )
                return
        #Construct the Url to send to google Maps API in exchange for the map
        url = self.constructUrl(availableLocs)
        bot.sendPhoto(chat_id=update.message.chat_id, photo=url)

        # Apologize to Luis
        if "luis" in update.message.from_user.first_name.lower():
            bot.sendMessage(chat_id=update.message.chat_id,
                reply_to_message_id=update.message.message_id,
                text="Sorry for being rude to you Luis. Will you forgive me?")

    #Construct the URL for the maps API
    def constructUrl(self, locations):
        url = self.baseUrl + '?'
        url += 'size=1024x1024&'
        #center stuff
        center = self.calculateCenter(locations)
        url += 'center='
        url += str(center[0])
        url += ','
        url += str(center[1])
        url += '&'
        #key Stuff
        url += 'key=' + self.key
        url += '&'

        # Add all the longs and lats for each location object
        for obj in locations:
            #create the Icon with the user Names
            url += 'markers=icon:https://chart.googleapis.com/chart?chst=d_bubble_text_small%26chld=bbT%257C'
            url += str(obj.userName)
            url += '%257CB8EDFF%257C000000'
            url += '%7C'
            #add the location points
            url += str(obj.latitude)
            url += ','
            url += str(obj.longitude)
            url += '&'

        return url

    #self explanatory
    def calculateCenter(self, locations):
        maxY = max([obj.longitude for obj in locations])
        minY = min([obj.longitude for obj in locations])
        maxX = max([obj.latitude for obj in locations])
        minX = min([obj.latitude for obj in locations])
        
        centerY = (maxY + minY) / 2
        centerX = (maxX + minX) / 2
        
        return (centerX, centerY)

if __name__ == "__main__":
    flb = FriendLocationBot(key_extractor.getKey("telegram"),
        key_extractor.getKey("google"))
    #Big Brother is watching you
    
    a
    flb.run()
