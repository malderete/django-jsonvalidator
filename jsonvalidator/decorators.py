import functools
import json
import jsonschema
import logging

from django.http import HttpResponse

logger = logging.getLogger("jsonvalidator.decorators")


class JSONValidator(object):
    """
    Validate a JSON object using  a
    fixed schema.

    @schema: JSON Schema to validate against.
    @get_data_callable: A callable object that
    receives a request and returns the data
    to compare against the schema.
    @load_json: Flag to indicates that the library should load the JSON.
    @on_error_callback: A callable object to
    call if the json provided is invalid (bad-formed).
    @on_invalid_callback: A callable object to
    call if the json provided does not match the
    given schema.
    """
    DEFAULT_CALLBACKS = {
        'on_error': lambda request, errors: HttpResponse('Error', status=400),
        'on_invalid': lambda request, errors: HttpResponse('Fail', status=400)
    }

    def __init__(self, schema, get_data_callable, load_json=True,
        on_error_callback=None, on_invalid_callback=None):

        self.schema = schema
        self.get_data_callable = get_data_callable
        self.load_json = load_json
        if on_error_callback is None:
            on_error_callback = JSONValidator.DEFAULT_CALLBACKS['on_error']
        if on_invalid_callback is None:
            on_invalid_callback = JSONValidator.DEFAULT_CALLBACKS['on_invalid']
        self.on_error = on_error_callback
        self.on_invalid = on_invalid_callback

    def __call__(self, view):
        functools.wraps(view)
        def wrapper(request, *args, **kwargs):
            try:
                data = self.get_data_callable(request)
                if self.load_json:
                    data = json.loads(data)
            except Exception:
                logger.debug("on_error: %s", view.__name__)
                return self.on_error(request)
            # JSON version 4
            validator = jsonschema.Draft4Validator(self.schema)
            # validate data
            errors = [error.message for error in validator.iter_errors(data)]
            if errors:
                logger.debug("on_invalid: %s", view.__name__)
                return self.on_invalid(request, errors)
            return view(request, *args, **kwargs)

        return wrapper

# shortcut
json_validator = JSONValidator
