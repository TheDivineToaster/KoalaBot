import json
import requests
import time
from discord.ext import commands


# The weather information is a class so that all the commands can be neatly contained inside it
# the class is imported as a "cog" in the main bot
# if you'd like to know more about how that works here is a link
# https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html
class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # The commands decorator is used in discord.py for command creation
    # ctx is the context, used for things like sending messages etc
    @commands.command()
    async def current(self, ctx, *searchTerms: str):
        """Gets the current weather for a searched location in Imperial Units

        :param self: The class
        :param ctx: context
        :param *searchTerms: a search terms tuple of any amount of strings
        """


        # taking the user search terms tuple and making it a space delimeted string
        # used in the api call to nominatim
        userSearch = ''
        for i in searchTerms:
            userSearch += " "
            userSearch += i

        # using nominatim for geocoding search api to GET latitude and longitude
        # more robust search than using openweathermap's search api used below for the weather data
        # takes any amount of search terms and gives back the latitude and longitude
        # that it believes is the best
        nominatumUrl = f'https://nominatim.openstreetmap.org/search?format=json&q={userSearch}'
        nomData = requests.get(nominatumUrl)

        # load the data returned into a JSON
        njson = json.loads(nomData.text)

        try:
            # parsing the loaded JSON for the latitude and longitude information
            # for the code I assume that the first result in the search is the best
            lat = njson[0]['lat']
            lon = njson[0]['lon']
        except:
            # if the search failed use the context to send a discord message indicating such
            await ctx.send('No data found for this search')

        # making api call to GET weather with the latitude and logitude from nominatum search
        # using imperial format as a default, as a future possiblity I may give the user the option for
        # metric units but the code does not currently support it
        openWeatherapiKey = 'OPEN_WEATHER_API_KEY'
        openWeatherUrl = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=imperial&appid={openWeatherapiKey}'
        weather = requests.get(openWeatherUrl)

        # loading the weather data into a JSON
        wjson= json.loads(weather.text)

        # return a discord message with the data to the user 
        # Example: 
        # "In Wichita the condition is moderate rain and it feels like 56°"
        await ctx.send(f"In {wjson['name']} the condition is {wjson['weather'][0]['description']} and it feels like {wjson['main']['feels_like']}°")

    @commands.command()
    async def sun(self, ctx, *searchTerms: str):
        """Gets the sunrise and sunset for a given location and sends a message
        indicating this to the user

        :param self: the class
        :param ctx: the context
        :param *searchTerms: a search terms tuple of any amount of strings
        """

        # same strategy as above, just using space seperators for the search terms that the
        # user has passed into the function for the GET api call
        userSearch = ''
        for i in searchTerms:
            userSearch += " "
            userSearch += i
        
        # using nominatim for geocoding search api to GET latitude and longitude
        # again, more robust search than using openweathermap's search api used below for the weather data
        # takes any amount of search terms and gives back the latitude and longitude
        # that it believes is the best
        nominatumUrl = f'https://nominatim.openstreetmap.org/search?format=json&q={userSearch}'
        nomData = requests.get(nominatumUrl)

        # load the data returned into a JSON
        njson = json.loads(nomData.text)

        try:
            # parsing the loaded JSON for the latitude and longitude information
            # same as code for weather, we assume first result is the best
            lat = njson[0]['lat']
            lon = njson[0]['lon']
        except:
            # send a message to the chat if the data isn't loaded
            await ctx.send('No data found for this search')

        # now making the api call to GET sunrise and sunset with the latitude and logitude from nominatum search
        openWeatherapiKey = 'OPEN_WEATHER_API_KEY'
        openWeatherUrl = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=imperial&appid={openWeatherapiKey}'
        weather = requests.get(openWeatherUrl)

        # loading the results into a JSON file
        wjson= json.loads(weather.text)

        # now we send the sunrise and sunset information to the user as requested
        # it accounts for the local timezone for the request and converts it using time.gmttime and time.strftime to format for the string
        # Example:
        # "In Kansas City today (03/28/24) the sunrise is at 7:08 AM and the sunset is at 7:39 PM"
        await ctx.send(
            f"In {wjson['name']} today ({time.strftime('%x',time.gmtime(wjson['dt'] + wjson['timezone']))}) "
            f"the sunrise is at {time.strftime('%I:%M %p',time.gmtime(wjson['sys']['sunrise'] + wjson['timezone']))} "
            f"and the sunset it at {time.strftime('%I:%M %p',time.gmtime(wjson['sys']['sunset'] + wjson['timezone']))}"
        )