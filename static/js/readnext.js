
var GU_CONTENT_API = 'http://content.guardianapis.com/search';

var feeds = [
  {
    'title': 'News',
    'url': '?section=news&page-size=3&format=json&show-fields=thumbnail'
  }
];

// build component markup

var i, n = feeds.length, feed;
for (i = 0; i < n; i++) {
  feed = feeds[i];
  console.log(GU_CONTENT_API + feed.url);
  
  // ajax call to GU_CONTENT_API + feed.url
  
  // build list markup
  
  // add markup to component
  
}

// draw component on the page