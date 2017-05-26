# WDYWAM
## What Do You Want, A Medal?

This Twitter bot searches for tweets containing phrases like “I should get an award for...”, parses the tweets into third-person phrasing, and replies to them with a drawing of an appropriate medal.

### Under the hood

`bot` does a search for up to 15 tweets that request an award. Then `get_medal_text` parses the tweet and returns a tuple of the user's Twitter handle and the text to go on the medal.

`draw_medal` takes the tuple as input and creates an appropriate medal image (using ImageMagick).
