import pytest
import sys

if __name__ == '__main__':
    # Example: test that the app loads the landing page
    from app import app
    with app.test_client() as client:
        resp = client.get('/')
        assert resp.status_code == 200
        assert b"Welcome" in resp.data
    print("Landing page test passed.")
