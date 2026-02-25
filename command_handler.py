import logging

logger = logging.getLogger("parser.command")


async def handle_gateway_command(frame: dict, registry, gateway=None, app=None) -> dict:
    """
    Handle incoming commands from OpenClaw Gateway.

    Supported methods:
    - channel.add: Add a channel to monitor
    - channel.remove: Remove a channel from monitoring
    - bot.enable: Enable the bot globally
    - bot.disable: Disable the bot globally
    """
    frame_id = frame.get("id")
    method = frame.get("method")
    params = frame.get("params", {})

    logger.info(f"Received command: method={method}, params={params}")

    response = None

    try:
        if method == "channel.add":
            username = params.get("username")
            if not username:
                response = {
                    "type": "res",
                    "id": frame_id,
                    "ok": False,
                    "error": "Missing 'username' parameter",
                }
            else:
                success = registry.add(username)
                response = {
                    "type": "res",
                    "id": frame_id,
                    "ok": success,
                    "payload": {"username": username, "added": success},
                }

        elif method == "channel.remove":
            username = params.get("username")
            if not username:
                response = {
                    "type": "res",
                    "id": frame_id,
                    "ok": False,
                    "error": "Missing 'username' parameter",
                }
            else:
                success = registry.remove(username)
                response = {
                    "type": "res",
                    "id": frame_id,
                    "ok": success,
                    "payload": {"username": username, "removed": success},
                }

        elif method == "bot.enable":
            success = registry.enable()
            response = {
                "type": "res",
                "id": frame_id,
                "ok": success,
                "payload": {"enabled": True},
            }

        elif method == "bot.disable":
            success = registry.disable()
            response = {
                "type": "res",
                "id": frame_id,
                "ok": success,
                "payload": {"enabled": False},
            }

        else:
            response = {
                "type": "res",
                "id": frame_id,
                "ok": False,
                "error": f"Unknown method: {method}",
            }

    except Exception as e:
        logger.error(f"Error handling command {method}: {e}")
        response = {
            "type": "res",
            "id": frame_id,
            "ok": False,
            "error": str(e),
        }

    # Send response back through gateway if available
    if gateway and response:
        await gateway.send_raw(response)

    return response
