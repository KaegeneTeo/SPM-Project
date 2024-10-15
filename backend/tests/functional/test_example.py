import pytest
from flask import jsonify
import json
from unittest.mock import MagicMock

def test_root_route(client):
    response = client.get('/')
    assert response.status_code == 200
