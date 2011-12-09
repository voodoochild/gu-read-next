from flask import Flask, make_response, render_template, abort, redirect, url_for
import requests
import random
import json
import feedparser

CONTENT_API = 'http://content.guardianapis.com/search'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/', methods=['GET'])
def index():
    """Index view. Currently just redirects to the only available component."""
    return redirect(url_for('readnext'))

@app.route('/readnext', methods=['GET'])
def readnext():
    """Read next component."""
    feeds = []
    
    # API feeds
    api = ContentApi(feeds)
    api.add_feed('Latest news', 'news')
    api.add_feed('Latest comment', 'commentisfree')
    api.add_feed('Latest sport', 'sport')
    api.add_feed('Latest music', 'music')
    
    # RSS feeds
    rss = RssFeeds(feeds)
    rss.add_feed('World lead stories', 'http://www.guardian.co.uk/world/lead/rss')
    rss.add_feed('Environment lead stories', 'http://www.guardian.co.uk/environment/lead/rss')
    
    random.shuffle(feeds)
    if not feeds:
        abort(404)
    
    response = make_response(render_template('index.html', feeds=feeds))
    return response


class DataGrabber:
    """
    Common methods required for getting and parsing data.
    
    This is here largely to act as a common interface for building classes
    for accessing different types of data from various sources.
    """
    
    def __init__(self, feeds):
        """Class constructor."""
        self.feeds = feeds
    
    def add_feed(self, title, key):
        """Add a feed to be grabbed."""
        feed = self.process_data(self.get_data(key))
        if feed:
            self.feeds.append({'title': title, 'feed': feed})
    
    def get_data(self, key):
        """Attempt to retrieve data."""
        r = requests.get(key)
        if r.status_code == 200:
            return r.content
        return False
    
    def process_data(self, data):
        """Process retrieved data."""
        pass
    
    def build_item(self, data):
        """Build a dictionary to use in the template context."""
        pass


class RssFeeds(DataGrabber):
    """Methods to request and process Guardian RSS feed data."""
    ITEMS_TO_SHOW = 3
    
    def process_data(self, data):
        """Process Guardian RSS feed data."""
        if data:
            rss_data = feedparser.parse(data)
            items = []
            i = 0
            for entry in rss_data.entries:
                if i < self.ITEMS_TO_SHOW:
                    items.append(self.build_item(entry))
                    i = i + 1
                else:
                    break
            return items
        return False
    
    def build_item(self, data):
        """Transform RSS data into a dictionary that the template can use."""
        article = {
            'title': data['title'],
            'url': data['link'],
        }

        for media in data['media_content']:
            if media['width'] == u'140' and media['height'] == u'84':
                article['thumbnail'] = media['url']
        return article


class ContentApi(DataGrabber):
    """Methods to request and process Content API data."""
    API_PARAMS = '%s?section=%s&page-size=3&format=json&show-fields=thumbnail'
    
    def add_feed(self, title, key):
        """Add an API feed using a set of predetermined parameters."""
        url =  self.API_PARAMS % (app.config['CONTENT_API'], key)
        feed = self.process_data(self.get_data(url))
        if feed:
            self.feeds.append({'title': title, 'feed': feed})

    def process_data(self, data):
        """Process Content API JSON data."""
        if data:
            json_data = json.loads(data)
            items = []
            for result in json_data['response']['results']:
                items.append(self.build_item(result))
            return items
        return False

    def build_item(self, data):
        """Transform JSON data into a dictionary that the template can use."""
        article = {
            'title': data['webTitle'],
            'url': data['webUrl'],
        }
        try:
            article['thumbnail'] = data['fields']['thumbnail']
        except KeyError:
            pass
        return article


if __name__ == "__main__":
    app.run(debug=True)
