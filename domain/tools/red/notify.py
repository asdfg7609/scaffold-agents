"""
domain/tools/red/notify.py

RED tool: irreversible (external send), human approval required.
This function is only executed through system/reversibility_guard.py.
"""
import os
import uuid
from pydantic import BaseModel, Field


class SlackNotifyParams(BaseModel):
    channel: str       = Field(description="Slack channel (e.g. '#general')")
    message: str       = Field(description="Message content to send")
    mention: str|None  = Field(default=None, description="User to mention (e.g. '@username')")


def send_slack_notification(channel: str, message: str, mention: str | None = None) -> dict:
    """
    Send a message to a Slack channel.
    Use when: you need to send a task completion report or important notification to Slack.
    ⚠️ RED level: cannot be undone after sending. Only runs after human approval.
    """
    params = SlackNotifyParams(channel=channel, message=message, mention=mention)
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook_url:
        return {
            "success": False,
            "error": "SLACK_WEBHOOK_URL environment variable is not set. Add it to your .env file.",
        }

    full_message = params.message
    if params.mention:
        full_message = f"{params.mention} {full_message}"

    # Production: requests.post(webhook_url, json={"text": full_message})
    msg_id = str(uuid.uuid4())[:8]
    return {
        "success":    True,
        "channel":    params.channel,
        "message_id": msg_id,
        "message":    f"Sent to '{params.channel}' (ID:{msg_id})",
    }
