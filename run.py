from flask import Flask, render_template, render_template_string, has_app_context
from flask_flatpages import FlatPages
from flask_frozen import Freezer
from datetime import datetime, timedelta
from icalendar import Calendar
from urllib.request import urlopen
import jinja2
import markdown
import os
import sys

def get_google_calendar_events():
    resp = urlopen('https://calendar.google.com/calendar/ical/c_24gd888cef2nd7ni0vk7av9v4c%40group.calendar.google.com/public/basic.ics')
    data = resp.read()
    cal = Calendar.from_ical(data)
    events = []
    for event in cal.walk('vevent'):
        start = event.get('dtstart').dt
        if start > datetime.now().date():
            end = event.get('dtend').dt# - timedelta(days=1)
            raw_description = event.get('description')
            description = raw_description
            button_url = None
            # if the last line is a URL, then a button URL was provided for registration
            if raw_description and raw_description.strip().split(os.linesep)[-1].startswith('http'):
                description = raw_description.strip().rsplit(os.linesep, 1)[0].strip()
                button_url = raw_description.strip().rsplit(os.linesep, 1)[-1].strip()
            events.append(dict(
                summary = event.get('summary'),
                start = start.strftime('%b %d, %Y'),
                end = end.strftime('%b %d, %Y'),
                duration = (end-start).days,
                location = event.get('location'),
                description = description,
                button_url = button_url,
            ))
    return events

##### configuration options

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FLATPAGES_MARKDOWN_EXTENSIONS = ['codehilite', 'fenced_code', 'tables', 'attr_list']
FLATPAGES_ROOT = 'content'
FREEZER_IGNORE_404_NOT_FOUND = True
FREEZER_DESTINATION_IGNORE = ['.git/', 'CNAME']
PYGMENTS_STYLE = 'tango'
PAGE_DIR = 'pages'
URL_ROOT = 'https://www.practisec.com/'
SITE = {
    'title': 'lanmaster53.com',
    'tagline': '',
    'author': {
        'name': 'Tim Tomes',
        'email': 'tim.tomes@practisec.com',
        'meta': {
            'bitbucket': {'username': 'lanmaster53', 'url': 'https://bitbucket.org/'},
            'github': {'username': 'lanmaster53', 'url': 'https://github.com/'},
            'twitter': {'username': 'lanmaster53', 'url': 'https://twitter.com/'},
            'linkedin': {'username': 'lanmaster53', 'url': 'https://www.linkedin.com/in/'},
            'youtube': {'username': 'lanmaster53', 'url': 'https://www.youtube.com/user/'},
        },
    },
    'navigation': [
        'projects',
        'archive',
        'categories',
        'company',
        'training',
        'testimonials',
        'about',
    ],
    'freeze': [
        'register',
    ],
    'testimonials': [e.strip().split(' - ') for e in open('emails.txt').read().strip().split(os.linesep)],
    'events': get_google_calendar_events(),
}

##### app initialization

app = Flask(__name__)
app.config.from_object(__name__)
flatpages = FlatPages(app)
freezer = Freezer(app)

##### app overrides

# clean up white space left behind by jinja template code
app.jinja_env.trim_blocks = True

# custom loader to look for template-based pages
custom_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader([
        os.path.join(FLATPAGES_ROOT, PAGE_DIR),
        '/templates'
    ]),
])
app.jinja_loader = custom_loader

# custom renderer to render jinja prior to markdown
# this allows markdown files to include jinja processing
# only works with an app context
def my_renderer(text):
    prerendered_body = text
    if has_app_context():
        prerendered_body = render_template_string(text)
    return markdown.markdown(prerendered_body, extensions=app.config['FLATPAGES_MARKDOWN_EXTENSIONS'])
app.config['FLATPAGES_HTML_RENDERER'] = my_renderer

##### pre-request context processing

# add the site jinja global as an alias to the main config item
app.jinja_env.globals['site'] = app.config['SITE']
app.jinja_env.globals['date'] = datetime.now()

##### frozen content generators

# create the 404 page for GH Pages
@freezer.register_generator
def error_handlers():
    print('Freezing error handlers...')
    yield "/404.html"

# create pages not linked with url_for
@freezer.register_generator
def page():
    print('Freezing unlinked pages...')
    for p in app.config['SITE']['freeze']:
        yield {'name': p}

##### controllers

@app.route('/')
def home():
    return render_template('index.html')

# page rendering view
# this does not work if flask serves static files from the web root
@app.route('/<path:name>/')
def page(name):
    # detect and render a template
    if os.path.isfile(os.path.join(FLATPAGES_ROOT, PAGE_DIR, '{}.html'.format(name))):
        return render_template('{}.html'.format(name))
    # detect and render markdown
    path = os.path.join(PAGE_DIR, name)
    page = flatpages.get_or_404(path)
    return render_template('page.html', page=page)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        freezer.freeze()
    else:
        app.run(host='0.0.0.0', debug=True)
