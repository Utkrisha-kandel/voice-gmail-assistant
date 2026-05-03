import json
import os
from groq import Groq
from tools import SYSTEM_PROMPT, TOOLS
from gmail import read_emails, send_email_fn

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
conversation_history = []

def execute_tool(tool_name, tool_args, token_data):
    if tool_name == "read_emails":
        emails = read_emails(token_data, max_results=tool_args.get("max_results", 5))
        if not emails:
            return "No emails found."
        return "".join(
            f"Email {i}:\nFrom: {e['from']}\nSubject: {e['subject']}\nDate: {e['date']}\nBody: {e['body'][:300]}\n\n"
            for i, e in enumerate(emails, 1)
        )
    elif tool_name == "send_email":
        status = send_email_fn(token_data, **tool_args)
        return f"Email sent to {tool_args['to']}." if status == "sent" else f"Failed: {status}"
    return "Unknown tool."

def chat(user_message: str, token_data: dict) -> str:
    conversation_history.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *conversation_history],
        tools=TOOLS, tool_choice="auto", max_tokens=500, temperature=0.7,
    )
    message = response.choices[0].message
    if message.tool_calls:
        conversation_history.append({
            "role": "assistant", "content": message.content or "",
            "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in message.tool_calls]
        })
        for tc in message.tool_calls:
            result = execute_tool(tc.function.name, json.loads(tc.function.arguments), token_data)
            conversation_history.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        reply = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *conversation_history],
            max_tokens=300, temperature=0.7,
        ).choices[0].message.content.strip()
    else:
        reply = message.content.strip()
    conversation_history.append({"role": "assistant", "content": reply})
    return reply