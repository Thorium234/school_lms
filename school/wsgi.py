import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment before Django
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings')
application = get_wsgi_application()
