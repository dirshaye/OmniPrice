from __future__ import annotations

import httpx

from omniprice.workers.scrape_consumer import _classify_failure


def test_classify_failure_validation_error():
    failure_type, error_class = _classify_failure(ValueError("bad payload"))
    assert failure_type == "permanent"
    assert error_class == "validation_error"


def test_classify_failure_http_404_is_permanent():
    request = httpx.Request("GET", "https://example.com/product")
    response = httpx.Response(404, request=request)
    exc = httpx.HTTPStatusError("404", request=request, response=response)
    failure_type, error_class = _classify_failure(exc)
    assert failure_type == "permanent"
    assert error_class == "http_404"


def test_classify_failure_http_503_is_transient():
    request = httpx.Request("GET", "https://example.com/product")
    response = httpx.Response(503, request=request)
    exc = httpx.HTTPStatusError("503", request=request, response=response)
    failure_type, error_class = _classify_failure(exc)
    assert failure_type == "transient"
    assert error_class == "http_503"
