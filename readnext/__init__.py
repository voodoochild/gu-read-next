from flask import Flask

CONTENT_API = 'http://content.guardianapis.com/search'
ITEMS_PER_FEED = 10     # how many items to retrieve per feed
ITEMS_TO_DISPLAY = 1    # how many items to show in the component per feed

app = Flask(__name__)
app.config.from_object(__name__)

import readnext.views
