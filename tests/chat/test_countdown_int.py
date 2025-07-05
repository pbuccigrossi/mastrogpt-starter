import os, requests as req

def test_countdown():
    
    url = "https://stream.openserverless.dev/web/" + os.environ.get("GITHUB_USER") + "/chat/countdown"
    respo = req.post(url, json={"input": "3"})
    res = respo.text
    
    
    '''
    envi = os.environ
    url = os.environ.get("OPSDEV_HOST") + "/api/my/chat/countdown"
    respo = req.post(url, json={"input": "3"})
    res = respo.json().get("output", "")
    '''
    
    assert res.startswith('{"output": "3...')
    assert res.find("Go!") != -1