===============
django-jsonvalidator
===============

**django-jsonvalidator** is a simple decorator that validates **JSON** data against
a fixed [SCHEMA](http://json-schema.org/).

I've copied and pasted this so often that I decided to create a reusable app.


Usage
=====

Just import the decorator::

    from jsonvalidator.decorators import json_validator

    EXPECTED_SCHEMA = {
        "type": "object",
        "required": ["foo", "bar"],
        "properties": {
            "foo": {"type": "string"},
            "bar": {"type": "string"}
        }
    }

    @json_validator(EXPECTED_SCHEMA, lambda r: r.body)
    def my_view(request):
        # Just enter here if request.body is valid against EXPECTED_SCHEMA



