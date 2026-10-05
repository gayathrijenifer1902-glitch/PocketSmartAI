import os, tempfile, uuid
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(tempfile.gettempdir(), f'pocketsmart_test_{uuid.uuid4().hex}.db')
os.environ['SECRET_KEY'] = 'this-is-a-long-enough-test-secret-key-32'
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def auth():
    client.delete = getattr(client, 'delete', None)
    email='test@example.com'; client.post('/register',json={'email':email,'name':'Test','password':'password123'})
    return client.post('/login',json={'email':email,'password':'password123'}).json()['access_token']
def test_health():
    with TestClient(app) as c: assert c.get('/health').json()['status']=='ok'
def test_authenticated_planners_and_history():
    with TestClient(app) as c:
        c.post('/register',json={'email':'planner@example.com','name':'Planner','password':'password123'})
        token=c.post('/login',json={'email':'planner@example.com','password':'password123'}).json()['access_token']; h={'Authorization':'Bearer '+token}
        r=c.post('/generate-home',headers=h,json={'budget':50000,'rooms':['Bedroom'],'style':'minimal'}); assert r.status_code==200 and r.json()['source']=='fallback'
        assert c.post('/generate-party',headers=h,json={'budget':10000,'guests':10,'event_type':'Birthday'}).status_code==200
        assert c.post('/generate-jewelry',headers=h,json={'budget':5000,'occasion':'Wedding'}).status_code==200
        assert len(c.get('/history',headers=h).json())==3
def test_rejects_invalid_budget():
    with TestClient(app) as c: assert c.post('/generate-home',json={'budget':0,'rooms':['x']}).status_code in (401,422)
