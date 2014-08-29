import json

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .decorators import json_validator


JSON_SCHEMA = {
    "type" : "object",
    "required": [
        'status', 'card_type', 'request_type', 'products',
        'payment_type', 'total_value', 'distributor_id', 'address_id',
        'cash_value'
    ],
    "properties" : {
        "status" : {"type" : "string"},
        "card_type" : {"type" : "string"},
        "request_type" : {"type" : "string"},
        "payment_type" : {"type" : "string"},
        "total_value": {"type" : "string"},
        "address_id": {"type" : "string"},
        "distributor_id": {"type" : "string"},
        "cash_value": {"type" : "string"},
        "products": {
            "type" : "array",
            "items" : {
                "type" : "object",
                "required": [
                    "price","product_distributor_id", "quantity"
                ],
                "properties" : {
                    "price" : {"type" : "string"},
                    "product_distributor_id" : {"type" : "string"},
                    "quantity" : {"type" : "string"},
                }
            }
        },
    }
}

# Utils
get_from_body = lambda r: r.body
get_from_form_field = lambda r: r.POST.get('c_data')


@json_validator(JSON_SCHEMA, get_from_body)
def test_for_post_view(request):
    return HttpResponse('OK')


@json_validator(JSON_SCHEMA, get_from_form_field)
def test_for_post_form_view(request):
    return HttpResponse('OK')


@json_validator(JSON_SCHEMA, get_from_form_field,
                attach_to_request=True)
def test_for_post_form_view_attach_to(request):
    data = json.dumps(request.json_valid)
    return HttpResponse(data, status=200, content_type='application/json')


def on_error_callback(request, err):
    return HttpResponse("Invalid JSON", status=400)

def on_invalid_callback(request, errors):
    data = json.dumps(dict(errors=errors))
    return HttpResponse(data, status=200, content_type='application/json')


@json_validator(JSON_SCHEMA, get_from_form_field,
    on_error_callback=on_error_callback)
def test_for_on_error_callback(request):
    return "Never get here"


@json_validator(JSON_SCHEMA, get_from_form_field,
    on_invalid_callback=on_invalid_callback)
def test_for_on_invalid_callback(request):
    return "Never get here"


class JsonSchemaTests(TestCase):
    def setUp(self):
        self.content_type="application/json"
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        # Data to test
        self.valid_data = {
            "status": "A",
            "card_type": "A",
            "request_type": "C",
            "products": [
                {
                    "price": "1.50",
                    "product_distributor_id": "449",
                    "quantity": "1"
                }
            ],
            "payment_type": "D",
            "total_value": "1000",
            "address_id": "624",
            "distributor_id": "107",
            "cash_value": "100"
        }

        self.invalid_data = {
            "card_type": "A",
            "products": [
                {
                    "price": "1.50",
                    "product_distributor_id": "449",
                    "quantity": "1"
                }
            ],
            "payment_type": "D",
            "total_value": "1000",
            "address_id": "624",
            "distributor_id": "107",
            "cash_value": "100"
        }

    def test_body_post_valid_schema(self):
        data = json.dumps(self.valid_data)
        request = self.factory.post('/', data, content_type=self.content_type)
        response = test_for_post_view(request)
        self.assertEquals(response.status_code, 200)

    def test_body_post_invalid_schema(self):
        data = json.dumps(self.invalid_data)
        request = self.factory.post('/', data, content_type=self.content_type)
        response = test_for_post_view(request)
        self.assertEquals(response.status_code, 400)

    def test_form_post_valid_schema(self):
        data = json.dumps(self.valid_data)
        request = self.factory.post('/', dict(c_data=data))
        response = test_for_post_form_view(request)
        self.assertEquals(response.status_code, 200)

    def test_form_post_invalid_schema(self):
        data = json.dumps(self.invalid_data)
        request = self.factory.post('/', dict(c_data=data))
        response = test_for_post_form_view(request)
        self.assertEquals(response.status_code, 400)

    def test_custom_on_invalid_callback(self):
        data = json.dumps(self.invalid_data)
        request = self.factory.post('/', dict(c_data=data))
        response = test_for_on_invalid_callback(request)
        response_json = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response_json['errors']), 2)

    def test_custom_on_error_callback(self):
        data = "[{}, 23234345]#123234fsdgdg45]"
        request = self.factory.post('/', dict(c_data=data))
        response = test_for_on_error_callback(request)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.content, "Invalid JSON")

    def test_attach_to_request(self):
        data = json.dumps(self.valid_data)
        request = self.factory.post('/', dict(c_data=data))
        response = test_for_post_form_view_attach_to(request)
        response_json = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(isinstance(response_json, dict), True)
