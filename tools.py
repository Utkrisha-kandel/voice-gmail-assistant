SYSTEM_PROMPT = """
You are a helpful voice assistant that manages Gmail.
Keep responses short and conversational.
Never use bullet points or markdown.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_emails",
            "description": "Fetch latest emails from Gmail inbox",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_results": {"type": "integer"}
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email on behalf of the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
]