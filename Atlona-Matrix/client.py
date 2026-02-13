import socket
import logging
import time

_LOGGER = logging.getLogger(__name__)


class AtlonaClient:
    """Optimized Atlona client that connects via the Telnet Broker service.
    
    Optimizations:
    - Static info (model, hostname, version) fetched separately, cached by coordinator
    - Single 'Status' command returns both video and audio routing
    - Output power states polled less frequently
    """
    
    def __init__(self, host: str, port: int = 2323, timeout: float = 5.0):
        self.host = host
        self.port = port
        self._timeout = timeout

    def _send_to_broker(self, command: str) -> str:
        """Send a command to the broker and get response."""
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self._timeout)
            s.connect((self.host, self.port))
            
            if not command.endswith("\n"):
                command += "\n"
            s.sendall(command.encode())
            
            chunks = []
            s.settimeout(1.0)
            while True:
                try:
                    data = s.recv(4096)
                    if not data:
                        break
                    chunks.append(data)
                except socket.timeout:
                    break
            
            decoded = b''.join(chunks).decode("utf-8", errors="ignore").strip()
            
            if decoded.startswith("ERROR:"):
                _LOGGER.warning(f"Broker error: {decoded}")
                return ""
            
            _LOGGER.debug(f"Broker response for '{command.strip()}': {repr(decoded)}")
            return decoded
            
        except socket.timeout:
            _LOGGER.warning(f"Broker timeout for command: {command.strip()}")
            return ""
        except Exception as e:
            _LOGGER.warning(f"Broker send error: {e}")
            return ""
        finally:
            if s:
                try:
                    s.close()
                except:
                    pass

    def send_command(self, command: str) -> str:
        """Send a single command to Atlona via broker."""
        cmd = command.strip()
        if cmd.endswith("\r\n"):
            cmd = cmd[:-2]
        elif cmd.endswith("\n"):
            cmd = cmd[:-1]
        return self._send_to_broker(cmd)

    def get_static_info(self) -> dict:
        """Get static device info (call once, cache result).
        
        Returns model, hostname, version - these don't change during operation.
        3 commands total.
        """
        return {
            "model": self._send_to_broker("Type"),
            "hostname": self._send_to_broker("show_host_name"),
            "version": self._send_to_broker("Version"),
        }

    def get_routing_status(self) -> dict:
        """Get current routing and power status.
        
        Uses single 'Status' command for both video and audio routing.
        2 commands total (Status + PWSTA).
        """
        return {
            "status_raw": self._send_to_broker("Status"),  # Returns both V and A
            "power": self._send_to_broker("PWSTA"),
        }

    def get_output_power_states(self) -> str:
        """Get output power states for all outputs.
        
        10 commands (one per output). Call less frequently.
        """
        output_power_lines = []
        for i in range(1, 11):
            resp = self._send_to_broker(f"x{i}$ sta")
            if resp:
                output_power_lines.append(resp)
        return "\n".join(output_power_lines)

    def get_all_status(self):
        """Legacy method for compatibility - fetches everything.
        
        Use get_routing_status() + cached static info instead.
        """
        result = {
            "power": "",
            "hostname": "",
            "model": "",
            "version": "",
            "video_raw": "",
            "audio_raw": "",
            "output_power_raw": "",
        }
        
        try:
            result["power"] = self._send_to_broker("PWSTA")
            result["model"] = self._send_to_broker("Type")
            result["hostname"] = self._send_to_broker("show_host_name")
            result["version"] = self._send_to_broker("Version")
            
            # Use single Status command
            status = self._send_to_broker("Status")
            lines = status.split("\n")
            if len(lines) >= 2:
                result["video_raw"] = lines[0]
                result["audio_raw"] = lines[1]
            elif len(lines) == 1:
                result["video_raw"] = lines[0]
            
            output_power_lines = []
            for i in range(1, 11):
                resp = self._send_to_broker(f"x{i}$ sta")
                if resp:
                    output_power_lines.append(resp)
            result["output_power_raw"] = "\n".join(output_power_lines)
            
            return result
            
        except Exception as e:
            _LOGGER.error(f"Atlona get_all_status error: {e}")
            return result

    def set_output_power(self, output_id: int, power: bool) -> str:
        """Set output power state."""
        cmd = "on" if power else "off"
        return self.send_command(f"x{output_id}$ {cmd}")

    def set_route(self, output_id: int, input_id: str) -> str:
        """Set video/audio routing."""
        clean_input = input_id.replace("x", "").replace("V", "")
        return self.send_command(f"x{clean_input}AVx{output_id}")
    
    def check_broker_status(self) -> dict:
        """Check broker connection status."""
        import json
        resp = self._send_to_broker("BROKER:STATUS")
        try:
            return json.loads(resp)
        except:
            return {"connected": False, "error": resp}
    
    def wait_for_connection(self, timeout: float = 30.0) -> bool:
        """Wait for broker to be connected to Atlona."""
        old_timeout = self._timeout
        self._timeout = timeout
        try:
            resp = self._send_to_broker("BROKER:WAIT")
            return "OK" in resp
        finally:
            self._timeout = old_timeout
