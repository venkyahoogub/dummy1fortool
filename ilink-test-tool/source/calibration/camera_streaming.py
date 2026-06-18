import threading
import socket
import struct
import sys
import os

# Add path for protobuf
pb2_path = os.path.join(os.path.dirname(__file__), '..', '..', 'neo-calibration-server-api', 'source', 'python')
sys.path.insert(0, pb2_path)

import calibration_server_api_pb2
from source.common_utilities.log_config import logger


class CameraStreamManager:
    def __init__(self):
        self.socket = None
        self.streaming = False
        self.stream_thread = None

    def connect(self, host="10.10.10.1", port=50051):
        """Connect to calibration server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            logger.info(f"Connected to calibration server at {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to calibration server: {e}")
            return False

    def disconnect(self):
        """Disconnect from calibration server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            logger.info("Disconnected from calibration server")

    def send_message(self, message):
        """Send protobuf message to server"""
        try:
            serialized = message.SerializeToString()
            length = struct.pack('>I', len(serialized))
            self.socket.sendall(length + serialized)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    def receive_message(self):
        """Receive protobuf message from server"""
        try:
            length_data = self.socket.recv(4)
            if not length_data:
                return None
            length = struct.unpack('>I', length_data)[0]
            
            data = b''
            while len(data) < length:
                chunk = self.socket.recv(length - len(data))
                if not chunk:
                    return None
                data += chunk
            
            message = calibration_server_api_pb2.FromServer()
            message.ParseFromString(data)
            return message
        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
            return None

    def start_streaming(self, output_callback=None):
        """Start streaming frames from server"""
        try:
            if not self.socket:
                raise Exception("Not connected to calibration server")
            
            request = calibration_server_api_pb2.ToServer()
            request.start_video_stream.CopyFrom(calibration_server_api_pb2.StartVideoStream())
            self.send_message(request)
            
            self.streaming = True
            logger.info("Stream started")
            
            self.stream_thread = threading.Thread(
                target=self._receive_stream_frames,
                args=(output_callback,),
                daemon=True
            )
            self.stream_thread.start()
            
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            raise

    def stop_streaming(self):
        """Stop streaming frames from server"""
        try:
            self.streaming = False
            
            if self.socket:
                request = calibration_server_api_pb2.ToServer()
                request.stop_video_stream.CopyFrom(calibration_server_api_pb2.StopVideoStream())
                self.send_message(request)
            
            logger.info("Stream stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop streaming: {e}")
            raise

    def _receive_stream_frames(self, output_callback=None):
        """Receive stream frames (runs in background thread)"""
        frame_count = 0
        try:
            while self.streaming:
                message = self.receive_message()
                if not message:
                    break
                
                if message.HasField('stream_frame'):
                    frame_count += 1
                    frame_data = message.stream_frame.frame
                    
                    result = {
                        'frame_number': frame_count,
                        'left': {
                            'image': frame_data.left.image,
                            'source': frame_data.left.source,
                            'width': frame_data.left.width,
                            'height': frame_data.left.height,
                            'timestamp_ms': frame_data.left.timestamp_ms,
                            'format': frame_data.left.format,
                        },
                        'right': {
                            'image': frame_data.right.image,
                            'source': frame_data.right.source,
                            'width': frame_data.right.width,
                            'height': frame_data.right.height,
                            'timestamp_ms': frame_data.right.timestamp_ms,
                            'format': frame_data.right.format,
                        },
                        'is_final': message.stream_frame.is_final,
                    }
                    
                    if output_callback:
                        output_callback(result)
                    
                    logger.debug(f"Frame {frame_count} received")
                    
        except Exception as e:
            if self.streaming:
                logger.error(f"Error receiving stream frames: {e}")
        finally:
            self.streaming = False


# Global instance
_stream_manager = None

def get_stream_manager():
    """Get or create the global stream manager"""
    global _stream_manager
    if _stream_manager is None:
        _stream_manager = CameraStreamManager()
    return _stream_manager


def start_camera_stream(output_callback=None):
    """Start streaming camera frames"""
    manager = get_stream_manager()
    
    try:
        if not manager.socket:
            if not manager.connect():
                return "Failed to connect to calibration server"
        
        manager.start_streaming(output_callback)
        return "Stream started successfully"
        
    except Exception as e:
        logger.exception("Failed to start camera stream")
        return str(e)


def stop_camera_stream():
    """Stop streaming camera frames"""
    manager = get_stream_manager()
    
    try:
        manager.stop_streaming()
        manager.disconnect()
        return "Stream stopped successfully"
        
    except Exception as e:
        logger.exception("Failed to stop camera stream")
        return str(e)


def disconnect_camera():
    """Disconnect from calibration server"""
    manager = get_stream_manager()
    manager.disconnect()
