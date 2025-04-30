import socket

class ProtocolHandler:
    @staticmethod
    def encode_command(command):
        length = len(command)
        return f"{length:03d} {command}"
    def validate_length(key, value):
        """Verify whether the key value length meets the protocol requirements"""
        if len(key) > 999 or len(value) > 999:
            return False, f"ERR {key} invalid length"
        if (len(key) + 1 + len(value)) > 970:
            return False, f"ERR {key} invalid length"
        return True, ""

    @staticmethod
    def parse_request(data_buffer):
        """Analyze the message header and extract the complete message"""
        if len(data_buffer) < 4 or not data_buffer[:3].isdigit():
            return None, data_buffer

        msg_length = int(data_buffer[:3])
        if len(data_buffer) < 4 + msg_length:
            return None, data_buffer

        full_msg = data_buffer[4:4+msg_length].decode('utf-8').strip()
        remaining_buffer = data_buffer[4+msg_length:]
        return full_msg, remaining_buffer

    @staticmethod
    def generate_response(response_str):
        """Generate response with length prefix"""
        return f"{len(response_str):03d} {response_str}".encode('utf-8')