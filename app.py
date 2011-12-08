from flask import Flask, render_template
import random
import requests
import json

CONTENT_API = 'http://content.guardianapis.com/search'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def index():
    """Index view."""
    feeds = []
    add_feed(feeds, 'Latest news', 'news')
    add_feed(feeds, 'Latest comment', 'commentisfree')
    add_feed(feeds, 'Latest sport', 'sport')
    add_feed(feeds, 'Latest music', 'music')
    random.shuffle(feeds)
    response = render_template('index.html', feeds=feeds)
    # set max-age http header
    return response

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
    r = requests.get(app.config['CONTENT_API'] + url)
    if r.status_code == 200:
        return r.content
    return False

def process_json(data):
    """Process JSON so that it can be used by the template context."""
    if data:
        data = json.loads(data)
        results = []
        for result in data['response']['results']:
            results.append({
                'title': result['webTitle'],
                'url': result['webUrl'],
                #'thumbnail': result['fields']['thumbnail']
            })
        return results
    
    return False

if __name__ == "__main__":
    app.run(debug=True)
