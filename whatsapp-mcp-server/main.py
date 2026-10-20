import functools
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from whatsapp import (
    ensure_bridge,
    search_contacts as whatsapp_search_contacts,
    list_messages as whatsapp_list_messages,
    list_chats as whatsapp_list_chats,
    get_chat as whatsapp_get_chat,
    get_direct_chat_by_contact as whatsapp_get_direct_chat_by_contact,
    get_contact_chats as whatsapp_get_contact_chats,
    get_last_interaction as whatsapp_get_last_interaction,
    get_message_context as whatsapp_get_message_context,
    send_message as whatsapp_send_message,
    send_file as whatsapp_send_file,
    send_audio_message as whatsapp_audio_voice_message,
    download_media as whatsapp_download_media,
    react_to_message as whatsapp_react_to_message,
    mark_as_read as whatsapp_mark_as_read,
    edit_message as whatsapp_edit_message,
    delete_message as whatsapp_delete_message,
    create_group as whatsapp_create_group,
    leave_group as whatsapp_leave_group,
    update_group_participants as whatsapp_update_group_participants,
)

# Initialize FastMCP server
mcp = FastMCP("whatsapp")


def tool(fn):
    """Register fn as an MCP tool that starts the bridge first if it isn't running."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        ensure_bridge()
        return fn(*args, **kwargs)
    return mcp.tool()(wrapper)


@tool
def search_contacts(query: str) -> List[Dict[str, Any]]:
    """Search WhatsApp contacts by name or phone number.
    
    Args:
        query: Search term to match against contact names or phone numbers
    """
    contacts = whatsapp_search_contacts(query)
    return contacts

@tool
def list_messages(
    after: Optional[str] = None,
    before: Optional[str] = None,
    sender_phone_number: Optional[str] = None,
    chat_jid: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_context: bool = True,
    context_before: int = 1,
    context_after: int = 1
) -> List[Dict[str, Any]]:
    """Get WhatsApp messages matching specified criteria with optional context.
    
    Args:
        after: Optional ISO-8601 formatted string to only return messages after this date
        before: Optional ISO-8601 formatted string to only return messages before this date
        sender_phone_number: Optional phone number to filter messages by sender
        chat_jid: Optional chat JID to filter messages by chat
        query: Optional search term to filter messages by content
        limit: Maximum number of messages to return (default 20)
        page: Page number for pagination (default 0)
        include_context: Whether to include messages before and after matches (default True)
        context_before: Number of messages to include before each match (default 1)
        context_after: Number of messages to include after each match (default 1)
    """
    messages = whatsapp_list_messages(
        after=after,
        before=before,
        sender_phone_number=sender_phone_number,
        chat_jid=chat_jid,
        query=query,
        limit=limit,
        page=page,
        include_context=include_context,
        context_before=context_before,
        context_after=context_after
    )
    return messages

@tool
def list_chats(
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_last_message: bool = True,
    sort_by: str = "last_active"
) -> List[Dict[str, Any]]:
    """Get WhatsApp chats matching specified criteria.
    
    Args:
        query: Optional search term to filter chats by name or JID
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
        include_last_message: Whether to include the last message in each chat (default True)
        sort_by: Field to sort results by, either "last_active" or "name" (default "last_active")
    """
    chats = whatsapp_list_chats(
        query=query,
        limit=limit,
        page=page,
        include_last_message=include_last_message,
        sort_by=sort_by
    )
    return chats

@tool
def get_chat(chat_jid: str, include_last_message: bool = True) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by JID.
    
    Args:
        chat_jid: The JID of the chat to retrieve
        include_last_message: Whether to include the last message (default True)
    """
    chat = whatsapp_get_chat(chat_jid, include_last_message)
    return chat

@tool
def get_direct_chat_by_contact(sender_phone_number: str) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by sender phone number.
    
    Args:
        sender_phone_number: The phone number to search for
    """
    chat = whatsapp_get_direct_chat_by_contact(sender_phone_number)
    return chat

@tool
def get_contact_chats(jid: str, limit: int = 20, page: int = 0) -> List[Dict[str, Any]]:
    """Get all WhatsApp chats involving the contact.
    
    Args:
        jid: The contact's JID to search for
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
    """
    chats = whatsapp_get_contact_chats(jid, limit, page)
    return chats

@tool
def get_last_interaction(jid: str) -> str:
    """Get most recent WhatsApp message involving the contact.
    
    Args:
        jid: The JID of the contact to search for
    """
    message = whatsapp_get_last_interaction(jid)
    return message

@tool
def get_message_context(
    message_id: str,
    before: int = 5,
    after: int = 5
) -> Dict[str, Any]:
    """Get context around a specific WhatsApp message.
    
    Args:
        message_id: The ID of the message to get context for
        before: Number of messages to include before the target message (default 5)
        after: Number of messages to include after the target message (default 5)
    """
    context = whatsapp_get_message_context(message_id, before, after)
    return context

@tool
def send_message(
    recipient: str,
    message: str,
    quoted_message_id: str = ""
) -> Dict[str, Any]:
    """Send a WhatsApp message to a person or group. For group chats use the JID.

    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        message: The message text to send
        quoted_message_id: Optional ID of a message to reply to / quote. Leave empty for a normal message.

    Returns:
        A dictionary containing success status and a status message
    """
    # Validate input
    if not recipient:
        return {
            "success": False,
            "message": "Recipient must be provided"
        }

    # Call the whatsapp_send_message function with the unified recipient parameter
    success, status_message = whatsapp_send_message(recipient, message, quoted_message_id)
    return {
        "success": success,
        "message": status_message
    }

@tool
def send_file(recipient: str, media_path: str, caption: str = "") -> Dict[str, Any]:
    """Send a file such as a picture, raw audio, video or document via WhatsApp to the specified recipient. For group messages use the JID.

    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        media_path: The absolute path to the media file to send (image, video, document)
        caption: Optional text caption to send together with the file (shown under images/videos/documents)

    Returns:
        A dictionary containing success status and a status message
    """

    # Call the whatsapp_send_file function
    success, status_message = whatsapp_send_file(recipient, media_path, caption)
    return {
        "success": success,
        "message": status_message
    }

@tool
def send_audio_message(recipient: str, media_path: str) -> Dict[str, Any]:
    """Send any audio file as a WhatsApp audio message to the specified recipient. For group messages use the JID. If it errors due to ffmpeg not being installed, use send_file instead.
    
    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        media_path: The absolute path to the audio file to send (will be converted to Opus .ogg if it's not a .ogg file)
    
    Returns:
        A dictionary containing success status and a status message
    """
    success, status_message = whatsapp_audio_voice_message(recipient, media_path)
    return {
        "success": success,
        "message": status_message
    }

@tool
def download_media(message_id: str, chat_jid: str) -> Dict[str, Any]:
    """Download media from a WhatsApp message and get the local file path.
    
    Args:
        message_id: The ID of the message containing the media
        chat_jid: The JID of the chat containing the message
    
    Returns:
        A dictionary containing success status, a status message, and the file path if successful
    """
    file_path = whatsapp_download_media(message_id, chat_jid)
    
    if file_path:
        return {
            "success": True,
            "message": "Media downloaded successfully",
            "file_path": file_path
        }
    else:
        return {
            "success": False,
            "message": "Failed to download media"
        }

@tool
def react_to_message(chat_jid: str, message_id: str, emoji: str) -> Dict[str, Any]:
    """React to a WhatsApp message with an emoji. Pass an empty emoji to remove your reaction.

    Args:
        chat_jid: The JID of the chat containing the message
        message_id: The ID of the message to react to
        emoji: The emoji to react with (e.g. "👍"), or "" to remove a previous reaction
    """
    success, status_message = whatsapp_react_to_message(chat_jid, message_id, emoji)
    return {"success": success, "message": status_message}

@tool
def mark_as_read(chat_jid: str, message_ids: List[str]) -> Dict[str, Any]:
    """Mark one or more WhatsApp messages as read (sends read receipts).

    Args:
        chat_jid: The JID of the chat containing the messages
        message_ids: A list of message IDs to mark as read
    """
    success, status_message = whatsapp_mark_as_read(chat_jid, message_ids)
    return {"success": success, "message": status_message}

@tool
def edit_message(chat_jid: str, message_id: str, new_text: str) -> Dict[str, Any]:
    """Edit a text message you previously sent. WhatsApp only allows editing within ~15 minutes of sending.

    Args:
        chat_jid: The JID of the chat containing the message
        message_id: The ID of your message to edit
        new_text: The new text content
    """
    success, status_message = whatsapp_edit_message(chat_jid, message_id, new_text)
    return {"success": success, "message": status_message}

@tool
def delete_message(chat_jid: str, message_id: str) -> Dict[str, Any]:
    """Delete (revoke) a message for everyone. Works on your own messages, or others' messages if you are a group admin.

    Args:
        chat_jid: The JID of the chat containing the message
        message_id: The ID of the message to delete
    """
    success, status_message = whatsapp_delete_message(chat_jid, message_id)
    return {"success": success, "message": status_message}

@tool
def create_group(name: str, participants: List[str]) -> Dict[str, Any]:
    """Create a new WhatsApp group.

    Args:
        name: The group name (max 25 characters)
        participants: List of phone numbers (country code, no +) or JIDs to add. You are added automatically.
    """
    success, status_message = whatsapp_create_group(name, participants)
    return {"success": success, "message": status_message}

@tool
def leave_group(group_jid: str) -> Dict[str, Any]:
    """Leave a WhatsApp group.

    Args:
        group_jid: The JID of the group to leave (e.g. "123456789@g.us")
    """
    success, status_message = whatsapp_leave_group(group_jid)
    return {"success": success, "message": status_message}

@tool
def update_group_participants(group_jid: str, action: str, participants: List[str]) -> Dict[str, Any]:
    """Add, remove, promote or demote participants in a WhatsApp group (requires admin rights).

    Args:
        group_jid: The JID of the group (e.g. "123456789@g.us")
        action: One of "add", "remove", "promote", "demote"
        participants: List of phone numbers (country code, no +) or JIDs to act on
    """
    success, status_message = whatsapp_update_group_participants(group_jid, action, participants)
    return {"success": success, "message": status_message}

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')