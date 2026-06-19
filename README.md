# WhatsApp MCP Server (Plus)

A Model Context Protocol (MCP) server for WhatsApp, with extra **agent-oriented** features.

With this you can search and read your personal WhatsApp messages (including images, videos, documents, and audio), search your contacts, and send messages to individuals or groups. You can also send media, **react, reply, edit, delete, mark as read, and manage groups** — all driven by an AI agent through MCP tools that you control.

It connects to your **personal WhatsApp account** directly via the WhatsApp web multidevice API (using the [whatsmeow](https://github.com/tulir/whatsmeow) library). All messages are stored locally in a SQLite database and only sent to an LLM when the agent accesses them through tools.

> ### Attribution
> This project is a fork of **[lharries/whatsapp-mcp](https://github.com/lharries/whatsapp-mcp)** by Luke Harries, licensed under MIT. It keeps the original architecture and adds the agent features listed below. See [`LICENSE`](./LICENSE).

> *Caution:* as with many MCP servers, the WhatsApp MCP is subject to [the lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/). Prompt injection could lead to private data exfiltration. Only connect it to agents and content you trust.

---

## ✨ What's new in this fork

| Feature | Tool / param | Notes |
|---|---|---|
| **Document MIME types** | `send_file` | PDF/DOCX/XLSX/PPTX/TXT/CSV/ZIP etc. send with the correct MIME + filename (no more "Untitled" / unrecognized file) |
| **Persist outgoing messages** | automatic | Messages the agent sends are written to the local DB, so `list_messages` shows the agent's own sends |
| **Caption on files** | `send_file(caption=...)` | Send a file and a text caption in one message |
| **Reply / quote** | `send_message(quoted_message_id=...)` | Thread-aware replies that quote an earlier message |
| **Reactions** | `react_to_message` | React with an emoji (empty string removes the reaction) |
| **Mark as read** | `mark_as_read` | Send read receipts for one or more messages |
| **Edit** | `edit_message` | Edit a message you sent (within WhatsApp's edit window) |
| **Delete / revoke** | `delete_message` | Delete a message for everyone |
| **Group management** | `create_group`, `leave_group`, `update_group_participants` | Create/leave groups; add/remove/promote/demote members |

These features are built into the Go bridge and exposed as MCP tools, so they work with **any MCP client** (see below), not just Claude Code.

---

## Compatible clients

This is a standard **stdio MCP server**, so it works with any MCP-compatible client. The launch command is always the same:

```
uv --directory {{PATH_TO_REPO}}/whatsapp-mcp-server run main.py
```

Where `{{PATH_TO_REPO}}` is the absolute path to your clone, and `uv` is the [uv](https://docs.astral.sh/uv/) launcher (run `which uv` for its full path if your client needs it).

The universal config object (used by most clients) is:

```json
{
  "mcpServers": {
    "whatsapp": {
      "command": "uv",
      "args": ["--directory", "{{PATH_TO_REPO}}/whatsapp-mcp-server", "run", "main.py"]
    }
  }
}
```

### Claude Code (CLI)

One command — no manual JSON editing:

```bash
claude mcp add whatsapp -- uv --directory {{PATH_TO_REPO}}/whatsapp-mcp-server run main.py
```

Then run `/mcp` inside Claude Code to confirm the `whatsapp` server is connected. Use `claude mcp list` to verify, or add `-s user` to make it available across all your projects.

### Claude Desktop

Save the universal config as `claude_desktop_config.json`:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Restart Claude Desktop; WhatsApp appears as an integration.

### Cursor

Save the universal config as `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per-project), then restart Cursor.

### Windsurf

Add the universal config to `~/.codeium/windsurf/mcp_config.json` (or via Settings → Cascade → MCP Servers → "Add Server"), then refresh.

### Cline / Roo Code (VS Code)

Open the Cline MCP settings (MCP Servers icon → Configure / Edit `cline_mcp_settings.json`) and add the same `mcpServers` entry.

### VS Code (GitHub Copilot agent mode)

Create `.vscode/mcp.json` in your workspace — note VS Code uses the `servers` key:

```json
{
  "servers": {
    "whatsapp": {
      "command": "uv",
      "args": ["--directory", "{{PATH_TO_REPO}}/whatsapp-mcp-server", "run", "main.py"]
    }
  }
}
```

### Zed

In `settings.json`, add under `context_servers`:

```json
{
  "context_servers": {
    "whatsapp": {
      "command": { "path": "uv", "args": ["--directory", "{{PATH_TO_REPO}}/whatsapp-mcp-server", "run", "main.py"] },
      "settings": {}
    }
  }
}
```

### Goose

```bash
goose session --with-extension "uv --directory {{PATH_TO_REPO}}/whatsapp-mcp-server run main.py"
```

Or add a **Command-line (stdio) extension** in the Goose UI with the command above.

### Continue

In `~/.continue/config.yaml`:

```yaml
mcpServers:
  - name: whatsapp
    command: uv
    args: ["--directory", "{{PATH_TO_REPO}}/whatsapp-mcp-server", "run", "main.py"]
```

> Any other MCP client works too — point it at the universal launch command above.

---

## Installation

### Prerequisites

- Go
- Python 3.6+
- An MCP client (Claude Code, Claude Desktop, Cursor, Windsurf, Cline, Zed, Goose, Continue, …)
- UV (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- FFmpeg (_optional_) — only needed to send audio files as playable WhatsApp voice messages (`.ogg` Opus). Without it, you can still send raw audio via `send_file`.

### Steps

1. **Clone this repository**

   ```bash
   git clone https://github.com/bayujo/whatsapp-mcp-plus.git
   cd whatsapp-mcp-plus
   ```

2. **Run the WhatsApp bridge**

   ```bash
   cd whatsapp-bridge
   go run main.go
   ```

   The first time, scan the QR code with your WhatsApp mobile app (Settings → Linked Devices). After ~20 days you may need to re-authenticate.

   Keep this process running — it maintains the WhatsApp connection and the local message store.

3. **Connect your MCP client** using the relevant section under [Compatible clients](#compatible-clients) above.

4. **Restart your client** and confirm the `whatsapp` server is connected.

### Windows Compatibility

`go-sqlite3` requires **CGO enabled** and a C compiler. CGO is disabled by default on Windows.

1. **Install a C compiler** — [MSYS2](https://www.msys2.org/) is recommended; add the `ucrt64\bin` folder to your `PATH` ([guide](https://code.visualstudio.com/docs/cpp/config-mingw)).
2. **Enable CGO and run:**

   ```bash
   cd whatsapp-bridge
   go env -w CGO_ENABLED=1
   go run main.go
   ```

Without this you'll hit: `Binary was compiled with 'CGO_ENABLED=0', go-sqlite3 requires cgo to work.`

## Architecture Overview

Two components:

1. **Go WhatsApp Bridge** (`whatsapp-bridge/`): connects to WhatsApp's web API, handles QR authentication, stores message history in SQLite, and exposes a small REST API consumed by the MCP server.
2. **Python MCP Server** (`whatsapp-mcp-server/`): implements the Model Context Protocol, providing standardized tools for an agent to interact with WhatsApp.

### Data Storage

- Message history is stored in SQLite under `whatsapp-bridge/store/`.
- Tables for chats and messages; indexed for efficient search.
- Messages the agent **sends** are now persisted too, so they appear in history.

## Usage

### MCP Tools

**Reading & search**
- **search_contacts** — search contacts by name or phone number
- **list_messages** — retrieve messages with filters and context
- **list_chats** — list chats with metadata
- **get_chat** — info about a specific chat
- **get_direct_chat_by_contact** — find a direct chat with a contact
- **get_contact_chats** — list all chats involving a contact
- **get_last_interaction** — most recent message with a contact
- **get_message_context** — context around a specific message

**Sending & media**
- **send_message** — send a message; optional `quoted_message_id` to reply/quote
- **send_file** — send an image/video/document/raw audio; optional `caption`
- **send_audio_message** — send an audio file as a playable voice message (`.ogg` Opus, or FFmpeg installed)
- **download_media** — download media from a message and get the local file path

**Agent actions (new)**
- **react_to_message** — react with an emoji (empty removes it)
- **mark_as_read** — send read receipts
- **edit_message** — edit a message you sent
- **delete_message** — delete (revoke) a message for everyone
- **create_group** — create a group
- **leave_group** — leave a group
- **update_group_participants** — add / remove / promote / demote members

### Media Handling

- **Sending**: use `send_file` for images, videos, and documents (correct MIME + filename), and `send_audio_message` for voice notes. With FFmpeg, non-Opus audio is auto-converted.
- **Downloading**: only media metadata is stored by default. Use `download_media` with the `message_id` and `chat_jid` to fetch the file and get its local path.

## Troubleshooting

- If `uv` isn't found, add it to your `PATH` or use its full path (`which uv`) in your client config.
- Make sure **both** the Go bridge and the MCP server are running.

### Authentication Issues
- **QR not displaying**: restart the bridge; ensure your terminal can render QR codes.
- **Already logged in**: the bridge reconnects automatically without a QR.
- **Device limit reached**: remove a device in WhatsApp (Settings → Linked Devices).
- **No messages loading**: history can take several minutes after first auth.
- **Out of sync**: delete `whatsapp-bridge/store/messages.db` and `whatsapp-bridge/store/whatsapp.db`, then restart to re-authenticate.

For client-specific MCP troubleshooting, see the [MCP documentation](https://modelcontextprotocol.io/).

## License

MIT — see [`LICENSE`](./LICENSE). Original work © Luke Harries; fork additions © Johar Bayu.
