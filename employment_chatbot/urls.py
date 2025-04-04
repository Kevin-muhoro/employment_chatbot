from django.urls import path
from chatbot.views import whatsapp_webhook

urlpatterns = [
    path('whatsapp/', whatsapp_webhook, name='whatsapp_webhook'),
]