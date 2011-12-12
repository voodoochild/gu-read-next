What do you want to read next?
==============================

This is a 'fail fast' experimental component that aims to provide links to recent and interesting articles for readers.

**To run the project locally with virtualenv:**

  `$ pip install virtualenv`
  
  `$ virtualenv venv/ --no-site-packages`
  
  `$ venv/bin/pip install -r requirements.txt`
  
  `$ venv/bin/python runserver.py`

**To run the project locally with App Engine:**

_Extract the various python libs in lib/ to the document root, e.g._

  `$ tar xzf lib/Flask-0.8.tar.gz`
  
  `$ mv Flask-0.8/flask/ .`
  
  `$ rm -rf Flask-0.8/`

_Then run it:_

  `$ dev_appserver.py .`