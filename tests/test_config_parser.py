import pytest
from awr2944_dca.mmws.config_parser import parse_ar1_call, AR1ParseError

def test_parse_simple_call():
    cmd = "ar1.ProfileConfig(0, 77.0, 256)"
    res = parse_ar1_call(cmd)
    assert res["name"] == "ProfileConfig"
    assert res["arg_count"] == 3
    assert res["args"] == [0, 77.0, 256]
    assert res["raw"] == cmd

def test_parse_no_ar1_prefix():
    cmd = "RfInit()"
    res = parse_ar1_call(cmd)
    assert res["name"] == "RfInit"
    assert res["arg_count"] == 0
    assert res["args"] == []
    
def test_parse_hex():
    cmd = "ar1.RfLdoBypassConfig(0x0)"
    res = parse_ar1_call(cmd)
    assert res["args"] == [0]
    
    cmd2 = "ar1.TestHex(0xFF, 0x1A)"
    res2 = parse_ar1_call(cmd2)
    assert res2["args"] == [255, 26]

def test_parse_whitespace():
    cmd = "  ar1.ChanNAdcConfig( 1 ,  1 ,0  )  "
    res = parse_ar1_call(cmd)
    assert res["name"] == "ChanNAdcConfig"
    assert res["args"] == [1, 1, 0]

def test_parse_invalid_args():
    with pytest.raises(AR1ParseError):
        parse_ar1_call("ar1.Test(1, abc)")
        
    with pytest.raises(AR1ParseError):
        parse_ar1_call("ar1.Test(1, )")

def test_parse_malformed():
    with pytest.raises(AR1ParseError):
        parse_ar1_call("ar1.Test(1, 2")  # Missing )
        
    with pytest.raises(AR1ParseError):
        parse_ar1_call("ar1.Test")  # Missing (

    with pytest.raises(AR1ParseError):
        parse_ar1_call("()")  # Empty function name
