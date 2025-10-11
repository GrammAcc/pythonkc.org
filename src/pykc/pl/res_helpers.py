from quart import (
    Response,
    jsonify,
)

from pykc.pl.validation.contracts import SanitizeResult


def success(payload: str | None = None) -> Response:
    if payload is None:
        return Response("200 SUCCESS", status=200)
    else:
        return Response(payload, status=200)


def created(payload: str | None = None) -> Response:
    if payload is None:
        return Response("201 CREATED", status=201)
    else:
        return Response(payload, status=201)


def not_found() -> Response:
    return Response("404 NOT FOUND", status=404)


def internal_server_error() -> Response:
    return Response("500 INTERNAL SERVER ERROR", status=500)


def bad_request(
    details: str, failed_validation: SanitizeResult | None = None, **kwargs
) -> Response:
    """Helper function to construct a status 400 error response with a structured JSON body.

    Intended to be compliant with problem details as defined in
    [RFC7807(https://www.rfc-editor.org/rfc/rfc7807)

    Args:
        details:
            Specific error information. MUST NOT include any sensitive information that can't be
            exposed to the browser console.
        failed_validation:
            Contains details of the field-level validations for this request.
            Must not contain any sensitive information that can't be exposed to the browser console.
        kwargs:
            Any additional key-value pairs to be included in the error response object.
            The values must be json-serializable. Also MUST NOT include any sensitive info.
    """

    if failed_validation is not None:
        err_dict = {
            "title": "Validation error",
            "status": 400,
            "detail": details,
            "errors": {k: v for k, v in failed_validation.errors},
        }
    else:
        err_dict = {
            "title": "Validation error",
            "status": 400,
            "detail": details,
        }

    err_dict.update(kwargs)
    res = jsonify(err_dict)
    res.status_code = 400
    res.content_type = "application/problem+json"
    return res


def unauthorized() -> Response:
    """Helper function to construct a status 401 error response with no debugging details.

    For security reasons, this function should be used instead of constructing
    responses with arbitrary data at the error site.
    """

    return Response("401 UNAUTHORIZED", status=401)


def forbidden() -> Response:
    """Helper function to construct a status 403 error response with no debugging details.

    For security reasons, this function should be used instead of constructing
    responses with arbitrary data at the error site.
    """

    return Response("403 FORBIDDEN", status=403)
