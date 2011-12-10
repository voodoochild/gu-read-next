from flask import Flask, make_response, render_template, abort, redirect, url_for, request
import requests
import random
import simplejson
import feedparser

CONTENT_API = 'http://content.guardianapis.com/search'
ITEMS_PER_FEED = 10     # how many items to retrieve per feed
ITEMS_TO_DISPLAY = 1    # how many items to show in the component per feed

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/', methods=['GET'])
def index():
    """Index view. Currently just redirects to the only available component."""
    return redirect(url_for('readnext'))

@app.route('/readnext', methods=['GET'])
def readnext():
    """Display four feeds at random."""
    feeds = []
    api = ContentApi(feeds)
    rss = RssFeeds(feeds)
    
    api.add_feed('News', 'news')
    api.add_feed('Comment', 'commentisfree')
    api.add_feed('Sport', 'sport')
    api.add_feed('Music', 'music')
    api.add_feed('Film', 'film')
    api.add_feed('Culture', 'culture')
    api.add_feed('Environment', 'environment')
    api.add_feed('TV', 'tv-and-radio')
    api.add_feed('Life &amp; Style', 'lifeandstyle')
    
    if not feeds:
        abort(404)
    random.shuffle(feeds)
    response = make_response(render_template('component.html', feeds=feeds[:4]))
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
            random.shuffle(feed)
            limit = app.config['ITEMS_TO_DISPLAY']
            self.feeds.append({'title': title, 'feed': feed[:limit]})
    
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


class ContentApi(DataGrabber):
    """Methods to request and process Content API data."""
    API_PARAMS = '%s?section=%s&page-size=%s&format=json&show-fields=thumbnail'
    
    def add_feed(self, title, key):
        """Add an API feed using a set of predetermined parameters."""
        url =  self.API_PARAMS % (
            app.config['CONTENT_API'], key, app.config['ITEMS_PER_FEED'])
        feed = self.process_data(self.get_data(url))
        if feed:
            random.shuffle(feed)
            limit = app.config['ITEMS_TO_DISPLAY']
            self.feeds.append({'title': title, 'feed': feed[:limit]})

    def process_data(self, data):
        """Process Content API JSON data."""
        if data:
            json_data = simplejson.loads(data)
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


class RssFeeds(DataGrabber):
    """Methods to request and process Guardian RSS feed data."""
    
    def process_data(self, data):
        """Process Guardian RSS feed data."""
        if data:
            rss_data = feedparser.parse(data)
            items = []
            i = 0
            for entry in rss_data.entries:
                if i < app.config['ITEMS_PER_FEED']:
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
        
        try:
            for media in data['media_content']:
                if media['width'] == u'140' and media['height'] == u'84':
                    article['thumbnail'] = media['url']
        except KeyError:
            pass
        return article


if __name__ == "__main__":
    app.run(debug=True)
