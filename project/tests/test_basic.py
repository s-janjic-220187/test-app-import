import sys
import os
import json
import pytest
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app import app

def test_landing_page():
    with app.test_client() as client:
        resp = client.get('/')
        assert resp.status_code == 200
        assert b"Welcome" in resp.data

def test_users_page():
    with app.test_client() as client:
        resp = client.get('/users')
        assert resp.status_code == 200
        assert b"User" in resp.data

def test_events_page():
    with app.test_client() as client:
        resp = client.get('/events')
        assert resp.status_code == 200
        assert b"Rodjendani" in resp.data or b"Event" in resp.data

def test_import_page():
    with app.test_client() as client:
        resp = client.get('/import')
        assert resp.status_code == 200
        assert b"Import Users" in resp.data

def test_log_page():
    with app.test_client() as client:
        resp = client.get('/log')
        assert resp.status_code == 200
        assert b"Log" in resp.data

def test_test_page():
    with app.test_client() as client:
        resp = client.get('/test')
        assert resp.status_code == 200
        assert b"Test" in resp.data or b"Automated" in resp.data

def test_api_events_get():
    with app.test_client() as client:
        resp = client.get('/api/events')
        assert resp.status_code == 200
        assert resp.is_json

def test_api_events_post_missing_data():
    with app.test_client() as client:
        resp = client.post('/api/events', json={})
        assert resp.status_code in (400, 500)

def test_api_user_get():
    with app.test_client() as client:
        resp = client.get('/api/user/1')
        assert resp.status_code in (200, 404)

def test_log_page_heading():
    with app.test_client() as client:
        resp = client.get('/log')
        assert b"Real-Time App Log" in resp.data
