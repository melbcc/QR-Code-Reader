from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic


class RootView(generic.TemplateView):
    template_name = 'index.html'


# ---------- Configure
class ConfigLocationView(generic.TemplateView):
    template_name = 'config-location.html'


class ConfigEventsView(generic.TemplateView):
    template_name = 'config-events.html'


# ---------- Scanner
class ScannerView(generic.TemplateView):
    template_name = 'scanner.html'
