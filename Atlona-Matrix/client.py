import socket
import logging
import time

_LOGGER = logging.getLogger(__name__)

class AtlonaClient:
    def __init__(self, host: str, port: int = 23, timeout: float = 5.0):
        self.host = host
        self.port = port
        self._timeout = timeout

    def send_command(self, command):
        """Send a command - opens new connection each time."""
        if isinstance(command, str):
            if not command.endswith("\r\n"):
                command += "\r\n"
            command = command.encode()
            
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((self.host, self.port))
            
            time.sleep(1)
            try:
                s.settimeout(0.5)
                s.recv(1024)
            except socket.timeout:
                pass
            
            s.settimeout(5)
            s.sendall(command)
            time.sleep(1)
            
            resp = s.recv(4096)
            decoded = resp.decode("utf-8", errors="ignore").strip()
            _LOGGER.debug(f"Atlona cmd response: {repr(decoded)}")
            return decoded
        except Exception as e:
            _LOGGER.warning(f"Atlona send_command error: {e}")
            return ""
        finally:
            if s:
                try:
                    s.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                try:
                    s.close()
                except:
                    pass

    def get_all_status(self):
        """Get all status in a single connection."""
        result = {
            "power": "",
            "hostname": "",
            "model": "",
            "version": "",
            "video_raw": "",
            "audio_raw": "",
            "output_power_raw": "",
        }
        
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(15)
            s.connect((self.host, self.port))
            
            time.sleep(1)
            try:
                s.settimeout(1)
                s.recv(1024)
            except socket.timeout:
                pass
            s.settimeout(5)
            
            def cmd(c):
                s.sendall((c + "\r\n").encode())
                time.sleep(0.5)
                try:
                    resp = s.recv(4096).decode("utf-8", errors="ignore").strip()
                    _LOGGER.debug(f"Atlona {c} -> {repr(resp)}")
                    return resp
                except:
                    return ""
            
            result["power"] = cmd("PWSTA")
            result["model"] = cmd("Type")
            result["hostname"] = cmd("show_host_name")
            result["version"] = cmd("Version")
            result["video_raw"] = cmd("Status V")
            result["audio_raw"] = cmd("Status A")
            
            # Get output power states for outputs 1-10
            output_power_lines = []
            for i in range(1, 11):
                resp = cmd(f"x{i}$ sta")
                if resp:
                    output_power_lines.append(resp)
            result["output_power_raw"] = "\n".join(output_power_lines)
            
            return result
            
        except Exception as e:
            _LOGGER.error(f"Atlona get_all_status error: {e}")
            return result
        finally:
            if s:
                try:
                    s.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                try:
                    s.close()
                except:
                    pass

    def set_output_power(self, output_id: int, power: bool) -> str:
        cmd = "on" if power else "off"
        return self.send_command(f"x{output_id}$ {cmd}")

    def set_route(self, output_id: int, input_id: str) -> str:
        clean_input = input_id.replace("x", "").replace("V", "")
        return self.send_command(f"x{clean_input}AVx{output_id}")
