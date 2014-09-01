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
    @on_error_callback: A callable object to
    call if the json provided is invalid (bad-formed).
    @on_invalid_callback: A callable object to
    call if the json provided does not match the
    given schema.
    @attach_to_request: Flag to indicate if the deserialized JSON
    should be attached to the request.REQUEST_ATTR (default: 'json_valid')
    to avoid an extra json.loads call. (DEFAULT: False)
    """
    DEFAULT_CALLBACKS = {
        'on_error': lambda request, error: HttpResponse('Error', status=400),
        'on_invalid': lambda request, errors: HttpResponse('Fail', status=400)
    }
    REQUEST_ATTR = 'json_valid'

    def __init__(self, schema, get_data_callable,
        on_error_callback=None, on_invalid_callback=None,
        attach_to_request=False):

        self.schema = schema
        self.get_data_callable = get_data_callable
        if on_error_callback is None:
            on_error_callback = JSONValidator.DEFAULT_CALLBACKS['on_error']
        if on_invalid_callback is None:
            on_invalid_callback = JSONValidator.DEFAULT_CALLBACKS['on_invalid']
        self.on_error = on_error_callback
        self.on_invalid = on_invalid_callback
        self.attach_to_request = attach_to_request

    def __call__(self, view):
        functools.wraps(view)
        def wrapper(request, *args, **kwargs):
            try:
                raw_data = self.get_data_callable(request)
                data = json.loads(raw_data)
            except Exception as err:
                logger.debug("on_error %s: %s", view.__name__, err)
                return self.on_error(request, err)
            # JSON version 4
            validator = jsonschema.Draft4Validator(self.schema)
            # validate data
            errors = [error.message for error in validator.iter_errors(data)]
            if errors:
                logger.debug("on_invalid: %s", view.__name__)
                return self.on_invalid(request, errors)

            if self.attach_to_request:
                setattr(request, JSONValidator.REQUEST_ATTR, data)
            return view(request, *args, **kwargs)

        return wrapper

# shortcut
json_validator = JSONValidator

