# Story Weaver

An interactive storytelling app where you co-author narratives with AI. Pick a genre, create characters, set the tone, and make choices that shape the plot as you go.

Built as a course-end project for the AI Literacy program.

## How it works

1. Choose a genre (fantasy, sci-fi, mystery, etc.) and subgenre
2. Describe your story's setting
3. Pick a narrative tone
4. Create up to 4 characters with names, roles, and personalities
5. The AI generates story segments and you pick from 3 choices (or write your own) each turn
6. Export the finished story as a PDF

## Tech stack

- **Frontend (web):** Next.js 16, TypeScript, Tailwind CSS
- **Frontend (standalone):** Streamlit (Python)
- **AI:** Azure OpenAI (gpt-5.2-chat)
- **PDF export:** jsPDF (web) / fpdf2 (Streamlit)

## Running locally

### Next.js version

```bash
npm install
npm run dev
```

Needs a `.env.local` with your Azure OpenAI creds:

```
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.2-chat
```

### Streamlit version

```bash
pip install -r requirements.txt
streamlit run app.py
```

Put your creds in `.streamlit/secrets.toml` (same keys as above).

## Project structure

```
app.py                  # Streamlit app (standalone version)
src/
  app/
    page.tsx            # main page
    api/story/route.ts  # AI story generation endpoint
    components/         # WelcomeScreen, StorySetup, StoryPlayer
    hooks/useStory.ts   # story state management
    types.ts            # shared types and constants
```
