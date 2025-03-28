from config.app_factory import create_app
from config.settings import Settings

app = create_app(Settings())
