from django.test import Client, TestCase

# Create your tests here.
from .models import Resource


class TestResources(TestCase):
    def test_call_resources(self):
        client = Client()
        breakpoint()
        a = Resource.objects.create(name="res a", description="this is res a")
        b = Resource.objects.create(name="res b", description="this is res b")

        response = client.get(f"/resources/")
        breakpoint()
