bot.py does a search for up to 15 tweets that request an award. Then get_medal_text parses their tweet and returns a tuple or the user's Twitter handle and the text to go on the medal.

draw_medal takes the tuple as input and creates a medal image (using ImageMagick).

TODO:
Draw medals on Heroku!
Delete all tweets (for development)