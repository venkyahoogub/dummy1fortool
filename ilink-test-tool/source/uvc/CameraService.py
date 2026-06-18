import asyncio
import socket
import struct
import cv2
import numpy as np
from common_utilities import constants
from common_utilities.log_config import logger


class CameraService:
    """
    CameraService: receives frames from a TCP UVC server.
    This implementation uses a persistent buffer and processes frames from that buffer,
    instead of assuming each recv will align to a header or frame boundary.
    """
    def __init__(self, server_ip, server_port, camera_command_left, frame_callback=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.camera_command_left = camera_command_left
        self.sock = None
        self.running = False
        self.buffer = b''  # persistent read buffer
        self.frame_callback = frame_callback
        # Maximum buffer we allow before truncating to avoid unbounded growth
        self.max_buffer_size = constants.MAX_BUFFER_SIZE  # 20 MB is the max allowed (similar to CPP streamservice)

    async def connect(self, camera_side=constants.CAMERA_STRING_LEFT):
        """
        Connect to the UVC server and select the camera. 
        Note: Selection is still dependent on having the nc port open.
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setblocking(False)
            await asyncio.get_event_loop().sock_connect(self.sock, (self.server_ip, self.server_port))
            logger.info(f"Connected to UVC server at {self.server_ip}:{self.server_port}")

            camera_command = self.camera_command_left if camera_side == constants.CAMERA_STRING_LEFT else constants.CAMERA_COMMAND_RIGHT
            if camera_command:
                logger.info(f"Sending camera command: {camera_command!r}")
                await asyncio.get_event_loop().sock_sendall(self.sock, camera_command)

            logger.info(f"Sending grab command: {constants.CAMERA_COMMAND_GRAB!r}")
            await asyncio.get_event_loop().sock_sendall(self.sock, constants.CAMERA_COMMAND_GRAB)
            self.running = True
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.running = False
            raise

    async def disconnect(self):
        """
        Disconnect the socket and clean up resources.
        """
        self.running = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except Exception as e:
                logger.warning(f"Socket shutdown failed: {e}")
            try:
                self.sock.close()
            except Exception as e:
                logger.warning(f"Socket close failed: {e}")
            logger.info("Disconnected from UVC server.")
        try:
            cv2.destroyAllWindows()
        except Exception as e:
            logger.warning(f"cv2.destroyAllWindows() failed: {e}")

    def parse_header(self, header_bytes):
        """
        Extract image size from the 48-byte header. 
        Similar to the cpp code's stream service
        """
        try:
            # Used struct.unpack to convert binary to python native types. 
            # Little endian unsigned int (4 Bytes) * 12 = 48 Bytes
            fields = struct.unpack('<' + 'I' * 12, header_bytes) 
        except struct.error:
            logger.warning("Header unpack failed due to unexpected size.")
            return {"imageSize": 0}
        # Find a plausible image size field (tunable thresholds)
        # Rough esitmate of minimum to maximum size of image.
        possible_sizes = [x for x in fields if 10_000 < x < 10_000_000]
        if not possible_sizes:
            logger.warning("No valid image size found in header fields.")
            return {"imageSize": 0}
        return {"imageSize": possible_sizes[0]}

    async def receive_live(self):
        """
        Buffered reader: read chunks from the socket, append to buffer,
        locate FRAME_HEADER_MARKER, parse header when available, wait for full image payload,
        then decode and deliver frame via frame_callback or fallback cv2.imshow.
        """
        loop = asyncio.get_event_loop()
        recv_chunk_size = constants.RECIEVED_CHUNK_SIZE  # 64KB reads

        while self.running:
            try:
                # Read available data (await socket recv)
                try:
                    data = await loop.sock_recv(self.sock, recv_chunk_size)
                except (ConnectionResetError, BrokenPipeError):
                    logger.error("Socket closed by peer.")
                    break
                except Exception as e:
                    logger.error(f"Socket recv error: {e}")
                    break

                if not data:
                    logger.warning("No data received (connection closed).")
                    break

                # Append new data to persistent buffer
                self.buffer += data

                # If the buffer gets very large, trim older bytes to avoid memory blow-up.
                if len(self.buffer) > self.max_buffer_size:
                    logger.warning("Buffer exceeded max size; truncating to most recent bytes.")
                    # Keep tail that could contain partial header
                    self.buffer = self.buffer[-(constants.UVC_VIDEO_HEADER_SIZE * 4):]

                # Try to find the FRAME_HEADER_MARKER header start in the buffer
                while True:
                    marker_idx = self.buffer.find(constants.FRAME_HEADER_MARKER)
                    if marker_idx == -1:
                        # No marker yet; wait for more data
                        break

                    # If marker not at start, discard bytes before marker
                    if marker_idx > 0:
                        # Quietly drop leading junk bytes
                        self.buffer = self.buffer[marker_idx:]

                    # Ensure we have the full header
                    if len(self.buffer) < constants.UVC_VIDEO_HEADER_SIZE:
                        # Wait for more bytes to complete header
                        break

                    # Now parse header from buffer start
                    header_bytes = self.buffer[:constants.UVC_VIDEO_HEADER_SIZE]
                    header = self.parse_header(header_bytes)
                    image_size = header.get("imageSize", 0)

                    if image_size <= 0:
                        # Bad header or parsing issue: drop the FRAME_HEADER_MARKER header (advance by 1 byte)
                        logger.warning("Invalid image size parsed from header; skipping one byte and retrying.")
                        self.buffer = self.buffer[1:]
                        continue

                    total_frame_len = constants.UVC_VIDEO_HEADER_SIZE + image_size
                    # Wait until full image payload is available in buffer
                    if len(self.buffer) < total_frame_len:
                        # Not enough bytes yet to extract the full image
                        break

                    # Extract image payload
                    image_data = self.buffer[constants.UVC_VIDEO_HEADER_SIZE:total_frame_len]
                    # Remove processed bytes from buffer
                    self.buffer = self.buffer[total_frame_len:]

                    try:
                        nparr = np.frombuffer(image_data, np.uint8)
                        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        if img is None:
                            logger.warning("cv2.imdecode returned None for a frame.")
                            # Continue to next frame if present without raising
                            continue
                        try:
                            img = cv2.resize(img, (500, 500))
                        except Exception as e:
                            logger.error(f"Image resizing failed with ERROR: {e}")

                        # Deliver frame to callback or fallback to cv2.imshow
                        if self.frame_callback:
                            try:
                                self.frame_callback(img)
                            except Exception as cb_e:
                                logger.error(f"Frame callback error: {cb_e}")
                        else:
                            cv2.imshow("Live UVC Stream", img)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                logger.info("User requested quit via OpenCV window.")
                                self.running = False
                                break
                    except Exception as e:
                        logger.error(f"Error decoding or handling frame: {e}")
                        # continue processing buffer for next frames
            except Exception as outer_e:
                logger.error(f"Unexpected error in receive_live loop: {outer_e}")
                break

        logger.info("Exiting receive loop, performing disconnect.")
        await self.disconnect()

    def run_blocking(self, camera_side=constants.CAMERA_STRING_LEFT):
        import asyncio
        asyncio.run(self.run(camera_side))

    async def run(self, camera_side=constants.CAMERA_STRING_LEFT):
        """Run the camera service, connecting then processing frames."""
        try:
            await self.connect(camera_side)
            await self.receive_live()
        except Exception as e:
            logger.error(f"Error running camera service: {e}")
        finally:
            await self.disconnect()