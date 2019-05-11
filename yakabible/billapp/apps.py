from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BillappConfig(AppConfig):
    name = 'billapp'

    def ready(self):
        import billapp.signals

