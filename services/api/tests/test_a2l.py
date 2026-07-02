from app.ecu.a2l import parse_a2l

SAMPLE = """
/begin PROJECT DEMO "demo"
  /begin MODULE MED17_5_20 "Bosch MED17.5.20"
    /begin COMPU_METHOD DEG_FROM_RAW "" LINEAR "%3.1" "deg" -20.0 0.75
    /end COMPU_METHOD
    /begin CHARACTERISTIC KFZW "Ignition timing map" MAP 0x8010F000
      DEG_FROM_RAW 0.0 40.0 10 7
    /end CHARACTERISTIC
    /begin AXIS_PTS RPM_AXIS "" 0x8010E000 UWORD DEG_FROM_RAW 10 800.0 6000.0
    /end AXIS_PTS
  /end MODULE
/end PROJECT
"""


def test_a2l_parses_basic_shape():
    parsed = parse_a2l(SAMPLE)
    assert parsed.project == "DEMO"
    assert parsed.module == "MED17_5_20"
    assert "DEG_FROM_RAW" in parsed.conversions
    assert parsed.conversions["DEG_FROM_RAW"].conv_type == "LINEAR"
    assert parsed.conversions["DEG_FROM_RAW"].unit == "deg"
    assert parsed.conversions["DEG_FROM_RAW"].coeffs == [-20.0, 0.75]
    assert "KFZW" in parsed.characteristics
    c = parsed.characteristics["KFZW"]
    assert c.kind == "MAP"
    assert c.address_hex == "0x8010F000"
    assert "RPM_AXIS" in parsed.axes
