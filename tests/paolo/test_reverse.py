import sys 
sys.path.append("packages/paolo/reverse")
import reverse

def test_reverse():
    res = reverse.reverse({"input": "What is the capital of Italy?"})
    assert res["output"] == "?ylatI fo latipac eht si tahW"
