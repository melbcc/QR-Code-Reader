from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic


class TestView(generic.TemplateView):
    template_name = 'test.html'


class ConfigView(generic.TemplateView):
    template_name = 'config.html'


class ScannerView(generic.TemplateView):
    template_name = 'scanner.html'
