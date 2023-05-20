import os
import sys
virtual_env = os.path.expanduser('/home/host1576434/virtualenv/')
activate_this = os.path.join(virtual_env,'bin/activate_this.py')
#execfile(activate_this, dict(__file__=activate_this))
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})
sys.path.append('/home/host1576434/gudweb.ru/htdocs/www/')
sys.path.append('/home/host1576434/gudweb.ru/mdsite/')
sys.path.append('/home/host1576434/gudweb.ru/mdsite/lib/')
#print >> sys.stderr, sys.path
os.environ['DJANGO_SETTINGS_MODULE'] = 'mdsite.settings'
import django.core.handlers.wsgi
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()