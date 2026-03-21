from django.apps import AppConfig


class TextilesConfig(AppConfig):
    # Keep the old app label so Django continues to associate the existing
    # migration history (django_migrations.app) and model tables with this app.
    # The Python module path is renamed to `textiles`, but the DB identity stays stable.
    name = 'textiles'
    label = 'grocery'
