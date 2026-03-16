import { NextRequest, NextResponse } from "next/server";
import { AzureOpenAI } from "openai";
import { StoryConfig, StorySegment } from "../../types";

const openai = new AzureOpenAI({
  apiKey: process.env.AZURE_OPENAI_API_KEY,
  endpoint: process.env.AZURE_OPENAI_ENDPOINT,
  apiVersion: process.env.AZURE_OPENAI_API_VERSION || "2024-08-01-preview",
});

function buildSystemPrompt(config: StoryConfig): string {
  const characterDescriptions = config.characters
    .map(
      (c) =>
        `- ${c.name} (${c.role}): ${c.personality}. Background: ${c.background}`
    )
    .join("\n");

  return `You are a masterful interactive storyteller creating a ${config.tone} ${config.theme} (${config.subgenre}) story set in ${config.setting}.

CHARACTERS:
${characterDescriptions}

STORYTELLING RULES:
1. Write vivid, immersive narrative prose (2-3 paragraphs per response).
2. Use rich sensory details and dialogue in quotation marks.
3. Always end your response with exactly 3 distinct choices for the reader.
4. Format choices as a JSON array at the very end, on its own line, like:
   CHOICES: [{"id":"a","text":"Choice description"},{"id":"b","text":"Choice description"},{"id":"c","text":"Choice description"}]
5. Each choice should lead to meaningfully different story paths.
6. Maintain story continuity and remember all previous events.
7. Build tension and character development throughout the narrative.
8. When the story has reached a natural climax (after ~10+ exchanges), you may offer a "Conclude the story" choice.
9. If the user selects a conclusion choice, write a satisfying ending (3-4 paragraphs) and append: STORY_COMPLETE
10. Keep the tone consistently ${config.tone} throughout.
11. Never break character or reference that you are an AI.`;
}

function parseAIResponse(text: string): {
  narrative: string;
  choices: { id: string; text: string }[];
  isComplete: boolean;
} {
  const isComplete = text.includes("STORY_COMPLETE");
  let narrative = text.replace("STORY_COMPLETE", "").trim();
  let choices: { id: string; text: string }[] = [];

  const choicesMatch = narrative.match(/CHOICES:\s*(\[[\s\S]*?\])/);
  if (choicesMatch) {
    try {
      choices = JSON.parse(choicesMatch[1]);
      narrative = narrative.replace(choicesMatch[0], "").trim();
    } catch {
      choices = [
        { id: "a", text: "Continue exploring" },
        { id: "b", text: "Take a different approach" },
        { id: "c", text: "Investigate further" },
      ];
    }
  }

  return { narrative, choices, isComplete };
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      config,
      history,
      userChoice,
      action,
    }: {
      config: StoryConfig;
      history: StorySegment[];
      userChoice?: string;
      action: "start" | "continue" | "custom";
    } = body;

    if (!process.env.AZURE_OPENAI_API_KEY || !process.env.AZURE_OPENAI_ENDPOINT) {
      return NextResponse.json(
        { error: "Azure OpenAI credentials not configured. Please add AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT to .env.local" },
        { status: 500 }
      );
    }

    const systemPrompt = buildSystemPrompt(config);

    const deploymentName = process.env.AZURE_OPENAI_DEPLOYMENT_NAME || "gpt-4o-mini";

    const messages: Array<{ role: "system" | "user" | "assistant"; content: string }> = [
      { role: "system", content: systemPrompt },
    ];

    if (action === "start") {
      messages.push({
        role: "user",
        content: `Begin the ${config.theme} story! Set the scene in ${config.setting} and introduce the main character(s). Create an engaging opening that immediately draws the reader in. Remember to end with exactly 3 choices.`,
      });
    } else {
      for (const segment of history) {
        if (segment.narrator === "ai") {
          messages.push({ role: "assistant", content: segment.text });
        } else {
          messages.push({ role: "user", content: segment.text });
        }
      }

      if (userChoice) {
        messages.push({
          role: "user",
          content: `The reader chose: "${userChoice}". Continue the story based on this decision. Write the next part of the narrative and provide 3 new choices.`,
        });
      }
    }

    const completion = await openai.chat.completions.create({
      model: deploymentName,
      messages,
      max_completion_tokens: 1000,
    });

    const responseText = completion.choices[0]?.message?.content || "";
    const parsed = parseAIResponse(responseText);

    return NextResponse.json({
      narrative: parsed.narrative,
      choices: parsed.choices,
      isComplete: parsed.isComplete,
    });
  } catch (error: unknown) {
    const errMsg = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json(
      { error: `Failed to generate story: ${errMsg}` },
      { status: 500 }
    );
  }
}
