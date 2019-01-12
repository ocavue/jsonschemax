from urllib.parse import urljoin, urlsplit


"""
https://tools.ietf.org/html/rfc3986#appendix-A

   URI           = scheme ":" hier-part [ "?" query ] [ "#" fragment ]

   hier-part     = "//" authority path-abempty
                 / path-absolute
                 / path-rootless
                 / path-empty

   URI-reference = URI / relative-ref

   absolute-URI  = scheme ":" hier-part [ "?" query ]

   relative-ref  = relative-part [ "?" query ] [ "#" fragment ]

   relative-part = "//" authority path-abempty
                 / path-absolute
                 / path-noscheme
                 / path-empty
"""


def is_uri(string):
    scheme, netloc, path, query, fragment, = urlsplit(string)
    return bool(scheme)


def is_abs_uri(string):
    scheme, netloc, path, query, fragment, = urlsplit(string)
    return bool(scheme) and not fragment


def resolve_id(base_uri, uri_reference):
    assert is_uri(base_uri) or not base_uri
    return urljoin(base_uri, uri_reference)
