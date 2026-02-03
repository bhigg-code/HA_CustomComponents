DOMAIN = "jvc_projector"
DEFAULT_PORT = 20554
DEFAULT_TIMEOUT = 5.0

# JVC Protocol constants
PJOK = b"PJ_OK"
PJNG = b"PJ_NG"
PJREQ = b"PJREQ"
PJACK = b"PJACK"

UNIT_ID = b"\x89\x01"
HEAD_OP = b"!" + UNIT_ID   # Operation command header
HEAD_REF = b"?" + UNIT_ID  # Reference/query command header
HEAD_RES = b"@" + UNIT_ID  # Response header
HEAD_ACK = b"\x06" + UNIT_ID  # Acknowledgment header
END = b"\n"

# Command codes
CMD_POWER = b"PW"
CMD_INPUT = b"IP"
CMD_PICTURE_MODE = b"PMPM"
CMD_MODEL = b"MD"
CMD_LASER_TIME = b"PMLT"
CMD_SOFTWARE_VERSION = b"IFSV"

# Power states
POWER_OFF = b"0"
POWER_ON = b"1"
POWER_COOLING = b"2"
POWER_WARMING = b"3"

POWER_STATES = {
    b"0": "off",
    b"1": "on",
    b"2": "cooling",
    b"3": "warming",
}

# Input sources
INPUT_SOURCES = {
    b"0": "HDMI 1",
    b"1": "HDMI 2",
}

INPUT_CODES = {
    "HDMI 1": b"0",
    "HDMI 2": b"1",
}

# Picture modes (NZ series)
PICTURE_MODES = {
    b"00": "Film",
    b"01": "Cinema",
    b"02": "Natural",
    b"03": "HDR10",
    b"04": "THX",
    b"06": "Frame Adapt HDR",
    b"0B": "User 1",
    b"0C": "User 2",
    b"0D": "User 3",
    b"0E": "User 4",
    b"0F": "User 5",
    b"10": "User 6",
    b"14": "HLG",
    b"15": "HDR10+",
    b"16": "Pana PQ",
}

PICTURE_MODE_CODES = {v: k for k, v in PICTURE_MODES.items()}

PLATFORMS = ["remote", "select", "sensor"]
