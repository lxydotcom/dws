def init_app(app, db):
  from .ui import models
  from .ui import views

  from .core import views

  from .utils import views  