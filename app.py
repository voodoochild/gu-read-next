from flask import Flask, render_template, abort
import random
import json

CONTENT_API = 'http://content.guardianapis.com/search'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/readnext', methods=['GET'])
def index():
    """Index view."""
    feeds = []
    add_feed(feeds, 'Latest news', 'news')
    add_feed(feeds, 'Latest comment', 'commentisfree')
    add_feed(feeds, 'Latest sport', 'sport')
    add_feed(feeds, 'Latest music', 'music')
    random.shuffle(feeds)
    if not feeds:
        abort(404)
    return render_template('index.html', feeds=feeds)

def add_feed(feeds, title, section):
    """Adds a feed to be obtained and outputted."""
    feed = process_json(get_articles_for_section(section))
    if feed:
        feeds.append({'title': title, 'articles': feed})

def get_articles_for_section(section):
    """Shortcut method to preconfigure most of the API parameters."""
    url = '?section=%s&page-size=3&format=json&show-fields=thumbnail'
    return call_content_api(url % section)

def call_content_api(url):
    """Attempts to retrieve data from the Content API."""
    try:
        from google.appengine.api import urlfetch
        r = urlfetch.fetch(app.config['CONTENT_API'] + url, method=urlfetch.GET)
        if r.status_code == 200:
            return r.content
    except ImportError:
        pass # not running on app engine
    try:
        import requests
        r = requests.get(app.config['CONTENT_API'] + url)
        if r.status_code == 200:
            return r.content
    except ImportError:
        pass
    return False

def process_json(data):
    """Process JSON so that it can be used by the template context."""
    if data:
        data = json.loads(data)
        results = []
        for result in data['response']['results']:
            results.append(build_article_dict(result))
        return results
    return False

def build_article_dict(json):
    """Parses supplied JSON to build a dictionary for an article."""
    article = {
        'title': json['webTitle'],
        'url': json['webUrl'],
    }
    try:
        article['thumbnail'] = json['fields']['thumbnail']
    except KeyError:
        pass
    return article

if __name__ == "__main__":
    app.run(debug=True)
