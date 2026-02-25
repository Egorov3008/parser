import asyncio
import json
import logging
import websockets
import hmac
import hashlib
import secrets

logger = logging.getLogger("parser.gateway")


class GatewayClient:
    """WebSocket client for communicating with OpenClaw Gateway."""

    def __init__(self, gateway_url: str, token: str):
        self.gateway_url = gateway_url
        self.token = token
        self.websocket = None
        self.request_id = 0

    async def connect(self) -> None:
        """Connect to OpenClaw Gateway with handshake."""
        logger.info(f"Connecting to OpenClaw Gateway at {self.gateway_url}")
        self.websocket = await websockets.connect(self.gateway_url)

        # Perform handshake with nonce-signature
        nonce = secrets.token_hex(16)
        signature = hmac.new(
            self.token.encode(),
            nonce.encode(),
            hashlib.sha256,
        ).hexdigest()

        connect_frame = {
            "type": "connect",
            "nonce": nonce,
            "signature": signature,
        }

        logger.debug(f"Sending connect frame: {connect_frame}")
        await self.websocket.send(json.dumps(connect_frame))

        # Wait for connection acknowledgement
        response = await self.websocket.recv()
        response_data = json.loads(response)
        logger.debug(f"Received response: {response_data}")

        if response_data.get("type") == "connected":
            logger.info("Successfully connected to OpenClaw Gateway")
        else:
            logger.error(f"Unexpected response during handshake: {response_data}")
            raise RuntimeError("Failed to handshake with OpenClaw Gateway")

    async def send_event(self, method: str, params: dict | None = None) -> int:
        """Send an event to OpenClaw Gateway."""
        if self.websocket is None:
            logger.warning("WebSocket not connected, skipping send_event")
            return -1

        self.request_id += 1
        frame = {
            "type": "req",
            "id": self.request_id,
            "method": method,
            "params": params if params is not None else {},
        }

        try:
            logger.debug(f"Sending req frame: {frame}")
            await self.websocket.send(json.dumps(frame))
            return self.request_id
        except Exception as e:
            logger.error(f"Failed to send event: {e}")
            return -1

    async def send_raw(self, frame: dict) -> bool:
        """Send a raw frame directly to the gateway."""
        if self.websocket is None:
            logger.warning("WebSocket not connected, skipping send_raw")
            return False

        try:
            logger.debug(f"Sending raw frame: {frame}")
            await self.websocket.send(json.dumps(frame))
            return True
        except Exception as e:
            logger.error(f"Failed to send raw frame: {e}")
            return False

    async def listen(self, callback) -> None:
        """Listen for incoming frames from OpenClaw Gateway."""
        if self.websocket is None:
            logger.warning("WebSocket not connected, cannot listen")
            return

        try:
            async for message in self.websocket:
                try:
                    frame = json.loads(message)
                    logger.debug(f"Received frame: {frame}")
                    await callback(frame)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse frame: {e}")
        except asyncio.CancelledError:
            logger.info("Listen loop cancelled")
        except Exception as e:
            logger.error(f"Error in listen loop: {e}")

    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            logger.info("WebSocket connection closed")
