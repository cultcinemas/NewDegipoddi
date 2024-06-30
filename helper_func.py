import asyncio
import base64
import re
from pyrogram import Client, enums
from pyrogram.errors import FloodWait
from config import FORCE_SUB_CHANNEL

async def is_notsubscribed(client: Client, user_id: int):
    """
    Check if the user is subscribed to the required channels.
    Returns a list of channel IDs where the user is not subscribed.
    """
    not_subscribed_channels = []
    for _id in FORCE_SUB_CHANNEL:
        try:
            user = await client.get_chat_member(_id, user_id)
        except Exception:
            not_subscribed_channels.append(_id)
        else:
            if user.status == enums.ChatMemberStatus.BANNED:
                not_subscribed_channels.append(_id)
    return not_subscribed_channels

async def encode(string: str) -> str:
    """
    Encode a string to base64.
    """
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii").strip("=")
    return base64_string

async def decode(base64_string: str) -> str:
    """
    Decode a base64 string.
    """
    base64_string = base64_string.strip("=")  # Handle padding
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    string = string_bytes.decode("ascii")
    return string

async def auto_delete_message(messages):
    """
    Delete a list of messages after 600 seconds.
    """
    await asyncio.sleep(600)
    await asyncio.gather(*[msg.delete() for msg in messages if msg])

async def get_messages(client: Client, message_ids: list) -> list:
    """
    Retrieve messages by their IDs from the specified chat.
    """
    messages = []
    total_messages = 0
    while total_messages < len(message_ids):
        temp_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temp_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temp_ids
            )
        except Exception:
            continue
        total_messages += len(temp_ids)
        messages.extend(msgs)
    return messages

async def get_message_id(client: Client, message) -> int:
    """
    Extract the message ID from a forwarded message or link.
    """
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern, message.text)
        if matches:
            channel_id = matches.group(1)
            msg_id = int(matches.group(2))
            if channel_id.isdigit():
                if f"-100{channel_id}" == str(client.db_channel.id):
                    return msg_id
            elif channel_id == client.db_channel.username:
                return msg_id
    return 0

def get_readable_time(seconds: int) -> str:
    """
    Convert seconds to a human-readable time format.
    """
    time_units = [
        (60 * 60 * 24, "days"),
        (60 * 60, "h"),
        (60, "m"),
        (1, "s")
    ]
    readable_time = []
    for unit, suffix in time_units:
        value, seconds = divmod(seconds, unit)
        if value:
            readable_time.append(f"{value}{suffix}")
    return ":".join(readable_time) if readable_time else "0s"
