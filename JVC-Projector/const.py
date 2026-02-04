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
CMD_LASER_TIME = b"IFLT"  # Light source time (lamp/laser hours)
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
    b"6": "HDMI 1",
    b"7": "HDMI 2",
}

INPUT_CODES = {
    "HDMI 1": b"6",
    "HDMI 2": b"7",
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

# JVC internal model codes to friendly names
# Model code is the part after " -- " in the raw response (e.g., "ILAFPJ -- B8A1" -> "B8A1")
# Based on pyjvcprojector specifications
MODEL_MAP = {
    # 2024 Models (CS20241)
    "B8A1": "DLA-NZ900",      # Also RS4200, N1188, V900R
    "B8A2": "DLA-NZ800",      # Also RS3200, N988, V800R
    # 2024 Models (CS20242)
    "D8A1": "DLA-NZ700",      # Also RS2200, N899, N888, N800, Z7
    "D8A2": "DLA-NZ500",      # Also RS1200, N799, N788, N700, Z5
    # 2022 Models (CS20221)
    "B5A1": "DLA-NZ9",        # Also RS4100, N11, V90R
    "B5A2": "DLA-NZ8",        # Also RS3100, N98, V80R
    "B5A3": "DLA-NZ7",        # Also RS2100, N88, V70R
    "B5B1": "DLA-NP5",        # Also RS1100, N78, V50
    # 2019 Models (CS20191)
    "B2A1": "DLA-NX9",        # Also RS3000, NX11, V9R
    "A2B1": "DLA-NX9",        # Alternate code
    "B2A2": "DLA-NX7",        # Also RS2000, N7, N8, V7
    "A2B2": "DLA-NX7",        # Alternate code
    "B2A3": "DLA-NX5",        # Also RS1000, N5, N6, V5
    "A2B3": "DLA-NX5",        # Alternate code
    # 2017 Models (CS20172)
    "A0A0": "DLA-Z1",         # Also RS4500
    # 2017 Models (CS20171)
    "XHR1": "DLA-X570R",      # Also RS420
    "XHR3": "DLA-X770R",      # Also X970, X970R, RS520, RS620
    # 2016 Models (CS20161)
    "XHP1": "DLA-X550R",      # Also X5000, XC5890R, RS400
    "XHP2": "DLA-XC6890",     # Also XC6890R
    "XHP3": "DLA-X750R",      # Also X7000, XC7890R, RS500, X950R, X9000, RS600, PX1
    # 2014 Models (CS20141)
    "XHK1": "DLA-X500R",      # Also XC5880R, RS49
    "XHK2": "DLA-RS4910",
    "XHK3": "DLA-X700R",      # Also X7880R, XC7880R, RS57, X900R, RS67, RS6710
    # 2013 Models (CS20131)
    "XHG1": "DLA-X35",        # Also XC3800, RS46, RS4810
    "XHH1": "DLA-X55R",       # Also XC5800R, RS48
    "XHH4": "DLA-X75R",       # Also XC7800R, RS56, X95R, XC9800R, RS66
    # 2012 Models (CS20121)
    "XHE": "DLA-X30",         # Also XC388, RS45, RS4800
    "XHF": "DLA-X70R",        # Also XC788R, RS55, X90R, XC988R, RS65
}

PLATFORMS = ["remote", "select", "sensor", "switch"]
