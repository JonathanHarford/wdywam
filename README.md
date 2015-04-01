bot.py does a search for up to 15 tweets that request an award. Then get_medal_text parses their tweet and returns a tuple or the user's Twitter handle and the text to go on the medal.

draw_medal takes the tuple as input and creates a medal image (using ImageMagick).

TODO:
Track id of last tweet responded to in order to ensure we don't respond more than once to same tweet
Upload medal to imgur UNDER WDYWAM ACCOUNT
Respond to @wdywam tweets with imgur link.