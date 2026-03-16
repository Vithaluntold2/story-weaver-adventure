import streamlit as st
from openai import AzureOpenAI
import json
import re
import io
from datetime import datetime
from fpdf import FPDF

# inline lucide SVGs (no pip package for streamlit)

LUCIDE_ICONS = {
    "book-open": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
    "castle": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 20v-9H2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2Z"/><path d="M18 11V4H6v7"/><path d="M15 22v-4a3 3 0 0 0-3-3a3 3 0 0 0-3 3v4"/><path d="M22 11V9"/><path d="M2 11V9"/><path d="M6 4V2"/><path d="M18 4V2"/><path d="M10 4V2"/><path d="M14 4V2"/></svg>',
    "rocket": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg>',
    "search": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    "sword": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="14.5 17.5 3 6 3 3 6 3 17.5 14.5"/><line x1="13" x2="19" y1="19" y2="13"/><line x1="16" x2="20" y1="16" y2="20"/><line x1="19" x2="21" y1="21" y2="19"/></svg>',
    "ghost": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 10h.01"/><path d="M15 10h.01"/><path d="M12 2a8 8 0 0 0-8 8v12l3-3 2.5 2.5L12 19l2.5 2.5L17 19l3 3V10a8 8 0 0 0-8-8z"/></svg>',
    "heart": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>',
    "zap": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/></svg>',
    "rainbow": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 17a10 10 0 0 0-20 0"/><path d="M6 17a6 6 0 0 1 12 0"/><path d="M10 17a2 2 0 0 1 4 0"/></svg>',
    "moon": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>',
    "cloud-fog": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M16 17H7"/><path d="M17 21H9"/></svg>',
    "sparkles": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/></svg>',
    "flame": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>',
    "user": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "users": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "pen-line": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.376 3.622a1 1 0 0 1 3.002 3.002L7.368 18.635a2 2 0 0 1-.855.506l-2.872.838a.5.5 0 0 1-.62-.62l.838-2.872a2 2 0 0 1 .506-.854z"/></svg>',
    "map-pin": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    "palette": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/></svg>',
    "check-circle": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>',
    "copy": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>',
    "rotate-ccw": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>',
    "flag": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" x2="4" y1="22" y2="15"/></svg>',
    "play": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="6 3 20 12 6 21 6 3"/></svg>',
    "theater": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 10s3-3 3-8"/><path d="M22 10s-3-3-3-8"/><path d="M10 2c0 4.4-3.6 8-8 8"/><path d="M14 2c0 4.4 3.6 8 8 8"/><path d="M2 10s2 2 2 5"/><path d="M22 10s-2 2-2 5"/><path d="M8 15h8"/><path d="M2 22v-1a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v1"/><path d="M14 22v-1a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v1"/></svg>',
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/></svg>',
    "user-round": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/></svg>',
    "skull": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="12" r="1"/><circle cx="15" cy="12" r="1"/><path d="M8 20v2h8v-2"/><path d="m12.5 17-.5-1-.5 1h1z"/><path d="M16 20a2 2 0 0 0 1.56-3.25 8 8 0 1 0-11.12 0A2 2 0 0 0 8 20"/></svg>',
    "eye": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg>',
    "arrow-right": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>',
    "chevron-right": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>',
    "plus": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>',
    "x": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>',
    "send": '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"/><path d="m21.854 2.147-10.94 10.939"/></svg>',
}


def lucide(name, size=18, color="currentColor"):
    svg = LUCIDE_ICONS.get(name, "")
    return svg.replace("{size}", str(size)).replace("{color}", color)


def icon_html(name, size=18, color="#d4a337"):
    return f'<span style="display:inline-flex;vertical-align:middle;margin-right:6px">{lucide(name, size, color)}</span>'


# themes, tones, character roles

THEMES = [
    {"id": "fantasy", "name": "Fantasy",         "icon": "castle",  "desc": "Magic, mythical creatures, and epic quests",
     "subs": ["High Fantasy", "Dark Fantasy", "Fairy Tale", "Mythological"]},
    {"id": "scifi",   "name": "Science Fiction",  "icon": "rocket",  "desc": "Space exploration, future tech, and alien worlds",
     "subs": ["Space Opera", "Cyberpunk", "Post-Apocalyptic", "Time Travel"]},
    {"id": "mystery", "name": "Mystery",          "icon": "search",  "desc": "Puzzles, clues, and thrilling investigations",
     "subs": ["Detective Noir", "Cozy Mystery", "Psychological Thriller", "Heist"]},
    {"id": "adventure", "name": "Adventure",      "icon": "sword",   "desc": "Daring exploits, treasure hunts, and survival",
     "subs": ["Exploration", "Treasure Hunt", "Survival", "Swashbuckling"]},
    {"id": "horror",  "name": "Horror",           "icon": "ghost",   "desc": "Spine-chilling tales and supernatural encounters",
     "subs": ["Gothic", "Cosmic Horror", "Haunted", "Survival Horror"]},
    {"id": "romance", "name": "Romance",          "icon": "heart",   "desc": "Love, relationships, and emotional journeys",
     "subs": ["Historical Romance", "Contemporary", "Fantasy Romance", "Star-Crossed"]},
]

TONES = [
    {"id": "epic",          "name": "Epic & Grand",             "icon": "zap"},
    {"id": "lighthearted",  "name": "Lighthearted & Fun",       "icon": "rainbow"},
    {"id": "dark",          "name": "Dark & Gritty",            "icon": "moon"},
    {"id": "mysterious",    "name": "Mysterious & Suspenseful", "icon": "cloud-fog"},
    {"id": "whimsical",     "name": "Whimsical & Playful",      "icon": "sparkles"},
    {"id": "dramatic",      "name": "Dramatic & Intense",       "icon": "flame"},
]

CHARACTER_ROLES = [
    "Hero / Protagonist",
    "Mentor / Guide",
    "Sidekick / Companion",
    "Villain / Antagonist",
    "Mysterious Stranger",
    "Love Interest",
]

# azure openai setup

AZURE_ENDPOINT = st.secrets.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_KEY = st.secrets.get("AZURE_OPENAI_API_KEY", "")
AZURE_VERSION = st.secrets.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
AZURE_DEPLOYMENT = st.secrets.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5.2-chat")


def get_client():
    return AzureOpenAI(
        api_key=AZURE_KEY,
        azure_endpoint=AZURE_ENDPOINT,
        api_version=AZURE_VERSION,
    )


def build_system_prompt(config):
    chars = "\n".join(
        f"- {c['name']} ({c['role']}): {c['personality']}. Background: {c['background']}"
        for c in config["characters"]
    )
    return f"""You are a masterful interactive storyteller creating a {config['tone']} {config['theme']} ({config['subgenre']}) story set in {config['setting']}.

CHARACTERS:
{chars}

STORYTELLING RULES:
1. Write vivid, immersive narrative prose (2-3 paragraphs per response).
2. Use rich sensory details and dialogue in quotation marks.
3. Always end your response with exactly 3 distinct choices for the reader.
4. Format choices as a JSON array at the very end, on its own line, like:
   CHOICES: [{{"id":"a","text":"Choice description"}},{{"id":"b","text":"Choice description"}},{{"id":"c","text":"Choice description"}}]
5. Each choice should lead to meaningfully different story paths.
6. Maintain story continuity and remember all previous events.
7. Build tension and character development throughout the narrative.
8. When the story has reached a natural climax (after ~10+ exchanges), you may offer a "Conclude the story" choice.
9. If the user selects a conclusion choice, write a satisfying ending (3-4 paragraphs) and append: STORY_COMPLETE
10. Keep the tone consistently {config['tone']} throughout.
11. Never break character or reference that you are an AI."""


def parse_response(text):
    is_complete = "STORY_COMPLETE" in text
    narrative = text.replace("STORY_COMPLETE", "").strip()
    choices = []

    match = re.search(r"CHOICES:\s*(\[[\s\S]*?\])", narrative)
    if match:
        try:
            choices = json.loads(match.group(1))
            narrative = narrative[:match.start()].strip()
        except json.JSONDecodeError:
            # fallback choices if the model messes up the JSON
            choices = [
                {"id": "a", "text": "Continue exploring"},
                {"id": "b", "text": "Take a different approach"},
                {"id": "c", "text": "Investigate further"},
            ]
    return narrative, choices, is_complete


def call_azure(config, history, user_input=None, action="start"):
    client = get_client()
    messages = [{"role": "system", "content": build_system_prompt(config)}]

    if action == "start":
        messages.append({
            "role": "user",
            "content": f"Begin the {config['theme']} story! Set the scene in {config['setting']} and introduce the main character(s). Create an engaging opening that immediately draws the reader in. Remember to end with exactly 3 choices.",
        })
    else:
        for seg in history:
            messages.append({"role": "assistant" if seg["narrator"] == "ai" else "user", "content": seg["text"]})
        if user_input:
            messages.append({
                "role": "user",
                "content": f'The reader chose: "{user_input}". Continue the story based on this decision. Write the next part of the narrative and provide 3 new choices.',
            })

    resp = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=messages,
        max_completion_tokens=1000,
    )
    return parse_response(resp.choices[0].message.content or "")


def init_state():
    defaults = {
        "phase": "welcome",      # welcome | setup | playing | complete
        "setup_step": 0,         # 0-5
        "theme_id": "",
        "subgenre": "",
        "setting": "",
        "tone_id": "",
        "characters": [{"name": "", "personality": "", "background": "", "role": CHARACTER_ROLES[0]}],
        "config": None,
        "segments": [],
        "turn_count": 0,
        "is_complete": False,
        "error": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


CUSTOM_CSS = """
<style>
    /* Compact layout */
    .block-container { max-width: 780px; padding-top: 1.5rem; padding-bottom: 1rem; }

    /* Card component */
    .sw-card {
        background: rgba(19, 19, 32, 0.7);
        border: 1px solid rgba(212, 163, 55, 0.15);
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 8px;
        transition: border-color 0.2s;
    }
    .sw-card:hover { border-color: rgba(212, 163, 55, 0.4); }
    .sw-card-selected {
        border-color: #d4a337 !important;
        background: rgba(212, 163, 55, 0.08) !important;
        box-shadow: 0 0 12px rgba(212, 163, 55, 0.12);
    }

    /* Narrative text */
    .narrative-block {
        font-family: 'Georgia', serif;
        font-size: 15px;
        line-height: 1.75;
        color: #d8d8e4;
        padding: 16px 20px;
        background: rgba(19, 19, 32, 0.5);
        border-left: 3px solid #d4a337;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
    }

    /* User choice bubble */
    .user-choice-bubble {
        background: rgba(212, 163, 55, 0.12);
        border: 1px solid rgba(212, 163, 55, 0.25);
        border-radius: 12px 12px 4px 12px;
        padding: 10px 16px;
        margin: 8px 0 12px auto;
        max-width: 70%;
        text-align: right;
        color: #e8d89c;
        font-size: 14px;
        font-style: italic;
    }

    /* Choice buttons */
    .choice-btn {
        display: block;
        width: 100%;
        text-align: left;
        padding: 12px 16px;
        margin-bottom: 6px;
        background: rgba(19, 19, 32, 0.6);
        border: 1px solid rgba(100, 100, 120, 0.3);
        border-radius: 8px;
        color: #d0d0dc;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .choice-btn:hover {
        border-color: rgba(212, 163, 55, 0.5);
        background: rgba(212, 163, 55, 0.06);
    }
    .choice-label { color: #d4a337; font-weight: 700; margin-right: 8px; }

    /* Header bar */
    .sw-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0 12px;
        border-bottom: 1px solid rgba(100, 100, 120, 0.15);
        margin-bottom: 16px;
    }
    .sw-header-title { font-size: 14px; font-weight: 700; color: #d4a337; }
    .sw-header-sub { font-size: 11px; color: #888; }

    /* Progress bar */
    .sw-progress-bar {
        height: 3px;
        background: rgba(100, 100, 120, 0.2);
        border-radius: 2px;
        margin: 8px 0 18px;
        overflow: hidden;
    }
    .sw-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #b8862e, #d4a337);
        border-radius: 2px;
        transition: width 0.4s ease;
    }

    /* Welcome hero */
    .welcome-hero {
        text-align: center;
        padding: 60px 20px 40px;
    }
    .welcome-hero h1 {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #d4a337, #f0d78c, #d4a337);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .welcome-hero .tagline {
        font-size: 17px;
        color: #999;
        margin-bottom: 8px;
    }
    .welcome-hero .subtitle {
        font-size: 13px;
        color: #666;
        max-width: 480px;
        margin: 0 auto 32px;
    }
    .feature-row {
        display: flex;
        justify-content: center;
        gap: 28px;
        margin-top: 24px;
    }
    .feature-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        color: #666;
    }

    /* Section title */
    .section-title {
        font-size: 22px;
        font-weight: 700;
        color: #e8d89c;
        margin-bottom: 4px;
    }
    .section-desc {
        font-size: 13px;
        color: #888;
        margin-bottom: 16px;
    }

    /* Typing indicator */
    .typing-dots {
        display: inline-flex;
        gap: 4px;
        align-items: center;
        padding: 12px 16px;
    }
    .typing-dots span {
        width: 6px; height: 6px;
        background: #d4a337;
        border-radius: 50%;
        animation: dotBounce 1.2s ease-in-out infinite;
    }
    .typing-dots span:nth-child(2) { animation-delay: 0.15s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.3s; }
    @keyframes dotBounce {
        0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
        40% { transform: translateY(-6px); opacity: 1; }
    }

    /* End banner */
    .end-banner {
        text-align: center;
        padding: 30px 20px;
        border-top: 1px solid rgba(212, 163, 55, 0.2);
        margin-top: 16px;
    }
    .end-banner h2 {
        font-size: 24px;
        color: #e8d89c;
        margin-bottom: 6px;
    }

    /* Streamlit button overrides for golden */
    div.stButton > button[kind="primary"] {
        background-color: #d4a337;
        color: #0a0a0f;
        font-weight: 700;
        border: none;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #e0b54e;
    }

    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
</style>
"""

def render_welcome():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="welcome-hero">
        <div style="margin-bottom:16px">{lucide("book-open", 56, "#d4a337")}</div>
        <h1>Story Weaver</h1>
        <div class="tagline">Interactive AI Storytelling Adventure</div>
        <div class="subtitle">Craft unique narratives with AI as your co-author. Choose your genre, create characters, and shape the story with every decision.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if st.button("Begin Your Adventure  →", key="start_btn", type="primary", use_container_width=True):
            st.session_state.phase = "setup"
            st.rerun()

    st.markdown(f"""
    <div class="feature-row">
        <div class="feature-item">{icon_html("theater", 14, "#777")} Choose Your Genre</div>
        <div class="feature-item">{icon_html("user", 14, "#777")} Create Characters</div>
        <div class="feature-item">{icon_html("pen-line", 14, "#777")} Shape the Story</div>
    </div>
    """, unsafe_allow_html=True)


def render_setup():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    step = st.session_state.setup_step
    total = 6
    pct = int(((step + 1) / total) * 100)

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;font-size:11px;color:#666;margin-top:4px">
        <span>Step {step + 1} of {total}</span><span>{pct}%</span>
    </div>
    <div class="sw-progress-bar"><div class="sw-progress-fill" style="width:{pct}%"></div></div>
    """, unsafe_allow_html=True)

    # Step 0: Theme
    if step == 0:
        st.markdown(f'<div class="section-title">{icon_html("castle", 20)} Choose Your Genre</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">What kind of story would you like to tell?</div>', unsafe_allow_html=True)

        cols = st.columns(3)
        for i, t in enumerate(THEMES):
            with cols[i % 3]:
                selected = st.session_state.theme_id == t["id"]
                cls = "sw-card sw-card-selected" if selected else "sw-card"
                st.markdown(f"""<div class="{cls}">
                    <div style="margin-bottom:4px">{lucide(t['icon'], 22, '#d4a337' if selected else '#888')}</div>
                    <div style="font-weight:600;font-size:14px;color:{'#e8d89c' if selected else '#ccc'}">{t['name']}</div>
                    <div style="font-size:11px;color:#777;margin-top:2px">{t['desc']}</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"Select {t['name']}", key=f"theme_{t['id']}", use_container_width=True):
                    st.session_state.theme_id = t["id"]
                    st.session_state.subgenre = ""
                    st.rerun()

    # Step 1: Subgenre
    elif step == 1:
        theme = next((t for t in THEMES if t["id"] == st.session_state.theme_id), None)
        if not theme:
            st.session_state.setup_step = 0
            st.rerun()
            return
        st.markdown(f'<div class="section-title">{icon_html(theme["icon"], 20)} Refine Your {theme["name"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Pick a subgenre to shape the story\'s style</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, sub in enumerate(theme["subs"]):
            with cols[i % 2]:
                selected = st.session_state.subgenre == sub
                cls = "sw-card sw-card-selected" if selected else "sw-card"
                st.markdown(f'<div class="{cls}" style="text-align:center"><span style="font-weight:600;font-size:14px">{sub}</span></div>', unsafe_allow_html=True)
                if st.button(f"Pick {sub}", key=f"sub_{sub}", use_container_width=True):
                    st.session_state.subgenre = sub
                    st.rerun()

    # Step 2: Setting
    elif step == 2:
        st.markdown(f'<div class="section-title">{icon_html("map-pin", 20)} Describe the Setting</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Where does your story take place? Be as creative as you want!</div>', unsafe_allow_html=True)
        setting = st.text_area(
            "Setting",
            value=st.session_state.setting,
            placeholder='e.g., "A forgotten kingdom floating above the clouds, where ancient libraries hold the secrets of lost civilizations..."',
            height=120,
            label_visibility="collapsed",
        )
        st.session_state.setting = setting

    # Step 3: Tone
    elif step == 3:
        st.markdown(f'<div class="section-title">{icon_html("palette", 20)} Set the Tone</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">How should the story feel?</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, tone in enumerate(TONES):
            with cols[i % 3]:
                selected = st.session_state.tone_id == tone["id"]
                cls = "sw-card sw-card-selected" if selected else "sw-card"
                st.markdown(f"""<div class="{cls}" style="text-align:center">
                    <div style="margin-bottom:4px">{lucide(tone['icon'], 20, '#d4a337' if selected else '#888')}</div>
                    <div style="font-weight:600;font-size:13px">{tone['name']}</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"Pick {tone['name']}", key=f"tone_{tone['id']}", use_container_width=True):
                    st.session_state.tone_id = tone["id"]
                    st.rerun()

    # Step 4: Characters
    elif step == 4:
        st.markdown(f'<div class="section-title">{icon_html("users", 20)} Create Your Characters</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Introduce the people who will bring your story to life</div>', unsafe_allow_html=True)

        chars = st.session_state.characters
        for idx, char in enumerate(chars):
            with st.container():
                st.markdown(f"**Character {idx + 1}**")
                c1, c2 = st.columns(2)
                with c1:
                    chars[idx]["name"] = st.text_input("Name", value=char["name"], key=f"cname_{idx}", placeholder="Character name")
                with c2:
                    chars[idx]["role"] = st.selectbox("Role", CHARACTER_ROLES, index=CHARACTER_ROLES.index(char["role"]) if char["role"] in CHARACTER_ROLES else 0, key=f"crole_{idx}")
                chars[idx]["personality"] = st.text_input("Personality", value=char["personality"], key=f"cpers_{idx}", placeholder="e.g., brave, cunning, compassionate")
                chars[idx]["background"] = st.text_input("Background", value=char["background"], key=f"cbg_{idx}", placeholder="e.g., an exiled prince seeking redemption")

                if len(chars) > 1:
                    if st.button(f"Remove", key=f"cremove_{idx}"):
                        chars.pop(idx)
                        st.rerun()
                st.divider()

        if len(chars) < 4:
            if st.button("+ Add Another Character", key="add_char"):
                chars.append({"name": "", "personality": "", "background": "", "role": CHARACTER_ROLES[1]})
                st.rerun()
        st.session_state.characters = chars

    # Step 5: Review
    elif step == 5:
        theme = next((t for t in THEMES if t["id"] == st.session_state.theme_id), None)
        tone = next((t for t in TONES if t["id"] == st.session_state.tone_id), None)
        st.markdown(f'<div class="section-title">{icon_html("check-circle", 20)} Your Story Awaits</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Review your story setup before embarking on your adventure</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sw-card" style="padding:18px 20px">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
                {lucide(theme['icon'] if theme else 'book-open', 22, '#d4a337')}
                <div>
                    <div style="font-size:10px;text-transform:uppercase;color:#d4a337;letter-spacing:1px">Genre</div>
                    <div style="font-weight:600">{theme['name'] if theme else '—'} — {st.session_state.subgenre}</div>
                </div>
            </div>
            <hr style="border-color:rgba(100,100,120,0.15);margin:8px 0">
            <div style="margin-bottom:8px">
                <div style="font-size:10px;text-transform:uppercase;color:#d4a337;letter-spacing:1px">Setting</div>
                <div style="color:#bbb;font-size:14px;margin-top:2px">{st.session_state.setting}</div>
            </div>
            <hr style="border-color:rgba(100,100,120,0.15);margin:8px 0">
            <div style="margin-bottom:8px">
                <div style="font-size:10px;text-transform:uppercase;color:#d4a337;letter-spacing:1px">Tone</div>
                <div style="display:flex;align-items:center;gap:4px;margin-top:2px">{lucide(tone['icon'] if tone else 'zap', 14, '#d4a337')} {tone['name'] if tone else '—'}</div>
            </div>
            <hr style="border-color:rgba(100,100,120,0.15);margin:8px 0">
            <div>
                <div style="font-size:10px;text-transform:uppercase;color:#d4a337;letter-spacing:1px">Characters</div>
                {"".join(f'<div style="display:flex;align-items:flex-start;gap:6px;margin-top:6px">{icon_html("user-round", 14, "#d4a337")}<div><span style="font-weight:600">{c["name"]}</span> <span style="color:#888">({c["role"]})</span><div style="font-size:12px;color:#999">{c["personality"]}{" — " + c["background"] if c["background"] else ""}</div></div></div>' for c in st.session_state.characters if c["name"].strip())}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Navigation
    st.markdown("")
    nav1, nav2 = st.columns([1, 1])
    with nav1:
        label = "← Back"
        if st.button(label, key="back_btn"):
            if step == 0:
                st.session_state.phase = "welcome"
            else:
                st.session_state.setup_step = step - 1
            st.rerun()
    with nav2:
        can_next = False
        if step == 0:
            can_next = st.session_state.theme_id != ""
        elif step == 1:
            can_next = st.session_state.subgenre != ""
        elif step == 2:
            can_next = st.session_state.setting.strip() != ""
        elif step == 3:
            can_next = st.session_state.tone_id != ""
        elif step == 4:
            can_next = any(c["name"].strip() and c["personality"].strip() for c in st.session_state.characters)
        elif step == 5:
            can_next = True

        if step < 5:
            if st.button("Next →", key="next_btn", type="primary", disabled=not can_next, use_container_width=True):
                st.session_state.setup_step = step + 1
                st.rerun()
        else:
            if st.button("🚀 Start the Adventure", key="launch_btn", type="primary", use_container_width=True):
                launch_story()
                st.rerun()


def launch_story():
    theme = next((t for t in THEMES if t["id"] == st.session_state.theme_id), THEMES[0])
    tone = next((t for t in TONES if t["id"] == st.session_state.tone_id), TONES[0])
    config = {
        "theme": theme["name"],
        "subgenre": st.session_state.subgenre,
        "setting": st.session_state.setting,
        "tone": tone["name"],
        "characters": [c for c in st.session_state.characters if c["name"].strip()],
    }
    st.session_state.config = config
    st.session_state.phase = "playing"
    st.session_state.turn_count = 0
    st.session_state.segments = []
    st.session_state.is_complete = False

    with st.spinner("The story begins..."):
        narrative, choices, is_complete = call_azure(config, [], action="start")
    st.session_state.segments.append({"narrator": "ai", "text": narrative, "choices": choices, "ts": datetime.now().isoformat()})
    st.session_state.turn_count = 1
    st.session_state.is_complete = is_complete


def render_playing():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    config = st.session_state.config

    # Header
    st.markdown(f"""
    <div class="sw-header">
        <div>
            <div class="sw-header-title">{icon_html("book-open", 14)} Story Weaver</div>
            <div class="sw-header-sub">{config['theme']} — {config['subgenre']}  ·  Chapter {st.session_state.turn_count}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action bar
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        if st.button("📋 Copy Story", key="copy_btn"):
            st.session_state["_export_text"] = export_story_text()
            st.toast("Story copied — paste it anywhere!", icon="✅")
    with col_b:
        pdf_data = export_story_pdf()
        st.download_button("💾 Download PDF", data=pdf_data, file_name=f"{config['theme']}-adventure.pdf", mime="application/pdf", use_container_width=True)
    with col_c:
        if st.button("🔄 New Story", key="reset_btn"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    st.divider()

    # Render segments
    for seg in st.session_state.segments:
        if seg["narrator"] == "ai":
            st.markdown(f'<div class="narrative-block">{seg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="user-choice-bubble">✦ {seg["text"]}</div>', unsafe_allow_html=True)

    # Ending
    if st.session_state.is_complete:
        st.markdown(f"""
        <div class="end-banner">
            {lucide("flag", 36, "#d4a337")}
            <h2>The End</h2>
            <p style="color:#888;font-size:13px">Your adventure has reached its conclusion. What a journey!</p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            end_pdf = export_story_pdf()
            st.download_button("💾 Download PDF", data=end_pdf, file_name=f"{config['theme']}-adventure.pdf", mime="application/pdf", key="end_dl", use_container_width=True)
        with c3:
            if st.button("🔄 New Adventure", key="end_reset", use_container_width=True):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()
        return

    # Choices
    latest_ai = None
    for s in reversed(st.session_state.segments):
        if s["narrator"] == "ai":
            latest_ai = s
            break

    if latest_ai and latest_ai.get("choices"):
        st.markdown(f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:1.5px;color:#666;margin:12px 0 8px">{icon_html("chevron-right", 12, "#666")} What do you do?</div>', unsafe_allow_html=True)
        for ch in latest_ai["choices"]:
            if st.button(f"**{ch['id'].upper()}.** {ch['text']}", key=f"choice_{ch['id']}_{st.session_state.turn_count}", use_container_width=True):
                make_choice(ch["text"])
                st.rerun()

        # Custom input
        with st.expander("✏️ Or write your own action...", expanded=False):
            custom = st.text_input("Your action", key="custom_input", placeholder="Describe your own action...", label_visibility="collapsed")
            if st.button("Go →", key="custom_go", type="primary"):
                if custom and custom.strip():
                    make_choice(custom.strip())
                    st.rerun()


def make_choice(text: str):
    config = st.session_state.config
    st.session_state.segments.append({"narrator": "user", "text": text, "choices": None, "ts": datetime.now().isoformat()})

    with st.spinner("The story continues..."):
        narrative, choices, is_complete = call_azure(config, st.session_state.segments, user_input=text, action="continue")

    st.session_state.segments.append({"narrator": "ai", "text": narrative, "choices": choices, "ts": datetime.now().isoformat()})
    st.session_state.turn_count += 1
    st.session_state.is_complete = is_complete


def export_story_text():
    config = st.session_state.config
    if not config:
        return ""
    lines = [
        f"{config['theme']} Story — {config['subgenre']}",
        f"Setting: {config['setting']}",
        f"Tone: {config['tone']}\n",
        "Characters:",
    ]
    for c in config["characters"]:
        lines.append(f"  - {c['name']} ({c['role']}): {c['personality']}")
    lines.append("\n" + "—" * 40 + "\n")
    for seg in st.session_state.segments:
        if seg["narrator"] == "ai":
            lines.append(f"{seg['text']}\n")
        else:
            lines.append(f"  ▸ Your choice: {seg['text']}\n")
    return "\n".join(lines)


def export_story_pdf():
    config = st.session_state.config
    if not config:
        return b""

    def sanitize(text):
        # fpdf2 core fonts only handle latin-1, so swap out fancy unicode chars
        replacements = {
            "\u2014": "--", "\u2013": "-", "\u2018": "'", "\u2019": "'",
            "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u2022": "*",
            "\u25b8": ">", "\u2192": "->", "\u2190": "<-", "\u2605": "*",
            "\u266a": "~", "\u2248": "~", "\u00a0": " ",
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text.encode("latin-1", errors="replace").decode("latin-1")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 14, sanitize(f"{config['theme']} Story"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "I", 13)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, sanitize(config["subgenre"]), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)

    # Meta
    pdf.set_draw_color(200, 200, 200)
    pdf.line(20, pdf.get_y(), pdf.w - 20, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, sanitize(f"Setting: {config['setting']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, sanitize(f"Tone: {config['tone']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Characters
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, "Characters", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    for c in config["characters"]:
        pdf.cell(0, 6, sanitize(f"  {c['name']} ({c['role']}): {c['personality']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.line(20, pdf.get_y(), pdf.w - 20, pdf.get_y())
    pdf.ln(6)

    # Story segments
    for seg in st.session_state.segments:
        if seg["narrator"] == "ai":
            pdf.set_font("Times", "", 11)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 6, sanitize(seg["text"]))
            pdf.ln(4)
        else:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(140, 110, 30)
            pdf.multi_cell(0, 6, sanitize(f"Your choice: {seg['text']}"))
            pdf.ln(3)

    # Footer
    pdf.ln(6)
    pdf.line(20, pdf.get_y(), pdf.w - 20, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(0, 6, "Generated by Story Weaver -- Interactive AI Storytelling Adventure", new_x="LMARGIN", new_y="NEXT", align="C")

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def main():
    st.set_page_config(
        page_title="Story Weaver — Interactive AI Storytelling",
        page_icon="📖",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    init_state()

    if not AZURE_KEY or not AZURE_ENDPOINT:
        st.error("Azure OpenAI credentials not configured. Add AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT to `.streamlit/secrets.toml`.")
        st.stop()

    phase = st.session_state.phase
    if phase == "welcome":
        render_welcome()
    elif phase == "setup":
        render_setup()
    elif phase == "playing":
        render_playing()


if __name__ == "__main__":
    main()
