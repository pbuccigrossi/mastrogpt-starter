import os, requests as req
def test_reverse():
    url = os.environ.get("OPSDEV_HOST") + "/api/my/paolo/reverse"
    args = { "input": "What is the capital of Italy?"}
    res = req.post(url, json=args).json()
    assert res.get("output") == "?ylatI fo latipac eht si tahW"
