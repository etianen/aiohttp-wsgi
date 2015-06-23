import pytest

from aiohttp.web import Application


def on_finish_callback(app):
    assert isinstance(app, Application)


@pytest.mark.parametrize("on_finish", [[on_finish_callback]])
def test_static_miss(response):
    assert response.status == 200
