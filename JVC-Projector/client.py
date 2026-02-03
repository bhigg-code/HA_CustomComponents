"""JVC Projector client for network communication."""
import asyncio
import hashlib
import logging
import struct
from typing import Optional

from .const import (
    PJOK, PJREQ, PJACK, HEAD_OP, HEAD_REF, HEAD_RES, HEAD_ACK, END,
    CMD_POWER, CMD_INPUT, CMD_PICTURE_MODE, CMD_MODEL, CMD_LASER_TIME,
    CMD_SOFTWARE_VERSION, POWER_STATES, INPUT_SOURCES, PICTURE_MODES,
    POWER_ON, POWER_OFF, INPUT_CODES, PICTURE_MODE_CODES, DEFAULT_TIMEOUT
)

_LOGGER = logging.getLogger(__name__)

AUTH_SALT = "JVCKWPJ"


class JvcProjectorClient:
    """Client for communicating with JVC projectors."""

    def __init__(self, host: str, port: int = 20554, timeout: float = DEFAULT_TIMEOUT, password: str = ""):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._password = password
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()

    @property
    def host(self) -> str:
        return self._host

    async def connect(self) -> bool:
        """Establish connection to the projector."""
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=self._timeout
            )
            
            # Wait for greeting
            response = await asyncio.wait_for(
                self._reader.read(5),
                timeout=self._timeout
            )
            
            if response != PJOK:
                _LOGGER.error(f"Unexpected greeting: {response}")
                await self.disconnect()
                return False
            
            # Send handshake request
            if self._password:
                # Send with password padding
                auth_data = struct.pack(f"{max(16, len(self._password))}s", self._password.encode())
                self._writer.write(PJREQ + auth_data)
            else:
                self._writer.write(PJREQ)
            await self._writer.drain()
            
            # Wait for acknowledgment
            response = await asyncio.wait_for(
                self._reader.read(10),
                timeout=self._timeout
            )
            
            if response.startswith(PJACK):
                _LOGGER.debug("Connected to JVC projector at %s", self._host)
                return True
            elif response.startswith(b"PJNAK"):
                # Check if there's an auth challenge
                if len(response) > 5:
                    challenge = response[5:]
                    _LOGGER.debug(f"Auth challenge received: {challenge}")
                    # Try with password hash
                    if self._password:
                        auth_hash = hashlib.sha256(f"{self._password}{AUTH_SALT}".encode()).hexdigest().encode()
                        self._writer.write(auth_hash)
                        await self._writer.drain()
                        
                        response = await asyncio.wait_for(
                            self._reader.read(10),
                            timeout=self._timeout
                        )
                        if response.startswith(PJACK):
                            _LOGGER.debug("Authenticated successfully")
                            return True
                
                _LOGGER.error("Authentication failed - check password")
                await self.disconnect()
                return False
            else:
                _LOGGER.error(f"Handshake failed: {response}")
                await self.disconnect()
                return False
            
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as e:
            _LOGGER.error(f"Connection failed: {e}")
            return False

    async def disconnect(self):
        """Close the connection."""
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass
        self._reader = None
        self._writer = None

    async def _send_command(self, header: bytes, cmd: bytes, param: bytes = b"") -> Optional[bytes]:
        """Send a command and return the response."""
        async with self._lock:
            try:
                if not self._writer or self._writer.is_closing():
                    if not await self.connect():
                        return None
                
                # Build command
                message = header + cmd + param + END
                _LOGGER.debug(f"Sending: {message.hex()}")
                
                self._writer.write(message)
                await self._writer.drain()
                
                # Read acknowledgment
                ack = await asyncio.wait_for(
                    self._reader.read(100),
                    timeout=self._timeout
                )
                _LOGGER.debug(f"Received: {ack.hex()}")
                
                # Parse response
                if HEAD_ACK in ack:
                    # For operation commands, just ack
                    return b"OK"
                elif HEAD_RES in ack:
                    # Extract response data
                    idx = ack.find(HEAD_RES)
                    if idx >= 0:
                        # Response format: HEAD_RES + cmd + data + END
                        data = ack[idx + len(HEAD_RES):]
                        # Remove command code and END
                        if END in data:
                            data = data[:data.find(END)]
                        if len(data) > len(cmd):
                            return data[len(cmd):]
                        return data
                return ack
                
            except (asyncio.TimeoutError, OSError) as e:
                _LOGGER.error(f"Command failed: {e}")
                await self.disconnect()
                return None

    async def get_power_state(self) -> Optional[str]:
        """Get current power state."""
        response = await self._send_command(HEAD_REF, CMD_POWER)
        if response and response in POWER_STATES:
            return POWER_STATES[response]
        return None

    async def power_on(self) -> bool:
        """Turn projector on."""
        response = await self._send_command(HEAD_OP, CMD_POWER, POWER_ON)
        return response == b"OK"

    async def power_off(self) -> bool:
        """Turn projector off."""
        response = await self._send_command(HEAD_OP, CMD_POWER, POWER_OFF)
        return response == b"OK"

    async def get_input(self) -> Optional[str]:
        """Get current input source."""
        response = await self._send_command(HEAD_REF, CMD_INPUT)
        if response and response in INPUT_SOURCES:
            return INPUT_SOURCES[response]
        return None

    async def set_input(self, input_name: str) -> bool:
        """Set input source."""
        if input_name in INPUT_CODES:
            response = await self._send_command(HEAD_OP, CMD_INPUT, INPUT_CODES[input_name])
            return response == b"OK"
        return False

    async def get_picture_mode(self) -> Optional[str]:
        """Get current picture mode."""
        response = await self._send_command(HEAD_REF, CMD_PICTURE_MODE)
        if response and response in PICTURE_MODES:
            return PICTURE_MODES[response]
        return None

    async def set_picture_mode(self, mode: str) -> bool:
        """Set picture mode."""
        if mode in PICTURE_MODE_CODES:
            response = await self._send_command(HEAD_OP, CMD_PICTURE_MODE, PICTURE_MODE_CODES[mode])
            return response == b"OK"
        return False

    async def get_model(self) -> Optional[str]:
        """Get projector model."""
        response = await self._send_command(HEAD_REF, CMD_MODEL)
        if response:
            return response.decode("utf-8", errors="ignore").strip()
        return None

    async def get_laser_hours(self) -> Optional[int]:
        """Get laser/lamp hours."""
        response = await self._send_command(HEAD_REF, CMD_LASER_TIME)
        if response:
            try:
                return int(response.decode("utf-8", errors="ignore").strip())
            except (ValueError, AttributeError):
                pass
        return None

    async def get_software_version(self) -> Optional[str]:
        """Get software version."""
        response = await self._send_command(HEAD_REF, CMD_SOFTWARE_VERSION)
        if response:
            return response.decode("utf-8", errors="ignore").strip()
        return None

    async def get_all_status(self) -> dict:
        """Get all status in one call."""
        result = {
            "power": None,
            "input": None,
            "picture_mode": None,
            "model": None,
            "laser_hours": None,
            "software_version": None,
        }
        
        result["power"] = await self.get_power_state()
        
        # Only query other status if powered on
        if result["power"] == "on":
            result["input"] = await self.get_input()
            result["picture_mode"] = await self.get_picture_mode()
        
        # These can be queried anytime
        result["model"] = await self.get_model()
        result["laser_hours"] = await self.get_laser_hours()
        result["software_version"] = await self.get_software_version()
        
        await self.disconnect()
        return result
