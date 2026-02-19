"""
Zia AI — Action Registry
Central registry of all supported action schemas.
"""

from app.schemas.action import ActionSchema, RiskLevel

ACTION_REGISTRY: dict[str, ActionSchema] = {
    # ── Gmail ──
    "gmail.send_email": ActionSchema(
        action_type="gmail.send_email",
        display_name="Send Email",
        description="Send an email via Gmail API",
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        required_params=["recipient", "subject", "body"],
        executor="gmail",
        max_daily_executions=50,
    ),
    "gmail.read_inbox": ActionSchema(
        action_type="gmail.read_inbox",
        display_name="Read Inbox",
        description="Read recent emails from Gmail inbox",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        required_params=[],
        optional_params=["limit", "query"],
        executor="gmail",
    ),

    # ── Twilio Voice ──
    "twilio.make_call": ActionSchema(
        action_type="twilio.make_call",
        display_name="Make Phone Call",
        description="Make a voice call via Twilio",
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        required_params=["recipient"],
        optional_params=["message"],
        executor="twilio_voice",
        cooldown_seconds=30,
        max_daily_executions=20,
    ),

    # ── Twilio WhatsApp ──
    "twilio.send_whatsapp": ActionSchema(
        action_type="twilio.send_whatsapp",
        display_name="Send WhatsApp Message",
        description="Send a WhatsApp message via Twilio",
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        required_params=["recipient", "content"],
        executor="twilio_whatsapp",
    ),

    # ── Filesystem ──
    "filesystem.read_file": ActionSchema(
        action_type="filesystem.read_file",
        display_name="Read File",
        description="Read contents of a local file",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        required_params=["path"],
        executor="filesystem",
    ),
    "filesystem.search": ActionSchema(
        action_type="filesystem.search",
        display_name="Search Files",
        description="Search for files by name or content",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        required_params=["query"],
        optional_params=["directory", "extension"],
        executor="filesystem",
    ),
    "filesystem.open_file": ActionSchema(
        action_type="filesystem.open_file",
        display_name="Open File",
        description="Open a file or folder with default application",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        required_params=["path"],
        executor="filesystem",
    ),

    # ── Browser ──
    "browser.open_url": ActionSchema(
        action_type="browser.open_url",
        display_name="Open URL",
        description="Open a URL in the browser",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        required_params=["url"],
        executor="browser",
    ),
    "browser.youtube_play": ActionSchema(
        action_type="browser.youtube_play",
        display_name="Play YouTube",
        description="Search and play a YouTube video",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        required_params=["query"],
        executor="browser",
    ),

    # ── System ──
    "system.run_command": ActionSchema(
        action_type="system.run_command",
        display_name="Run System Command",
        description="Run a non-privileged system command",
        risk_level=RiskLevel.CRITICAL,
        requires_confirmation=True,
        required_params=["command"],
        executor="system",
        max_daily_executions=100,
        allowed_roles=["admin"],
    ),

    # ── Macros ──
    "macro.work_mode": ActionSchema(
        action_type="macro.work_mode",
        display_name="Work Mode",
        description="Activate work routine: open workspace, play music, send notification",
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        required_params=[],
        executor="macros",
    ),
}


def get_action_schema(action_type: str) -> ActionSchema | None:
    """Look up an action schema by type string."""
    return ACTION_REGISTRY.get(action_type)


def list_action_schemas() -> list[ActionSchema]:
    """Return all registered action schemas."""
    return list(ACTION_REGISTRY.values())
