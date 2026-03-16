"use client";

import { useState } from "react";
import { AppPhase, StoryConfig } from "./types";
import { useStory } from "./hooks/useStory";
import WelcomeScreen from "./components/WelcomeScreen";
import StorySetup from "./components/StorySetup";
import StoryPlayer from "./components/StoryPlayer";

export default function Home() {
  const [phase, setPhase] = useState<AppPhase>("welcome");
  const [error, setError] = useState<string | null>(null);
  const story = useStory();

  const handleSetupComplete = async (config: StoryConfig) => {
    story.setConfig(config);
    setPhase("playing");
    setError(null);

    try {
      const response = await fetch("/api/story", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          config,
          history: [],
          action: "start",
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to start story");
      }

      story.state.segments.push({
        id: crypto.randomUUID(),
        narrator: "ai",
        text: data.narrative,
        choices: data.choices,
        timestamp: new Date(),
      });
      story.state.turnCount = 1;
      story.setConfig({ ...config });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to start story";
      setError(msg);
    }
  };

  const handleReset = () => {
    story.resetStory();
    setPhase("welcome");
    setError(null);
  };

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100">
      {error && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 px-6 py-3 bg-red-900/90 border border-red-700 rounded-xl text-red-200 text-sm backdrop-blur-sm animate-fadeIn">
          <div className="flex items-center gap-3">
            <span>\u26a0\ufe0f</span>
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-200 ml-4"
            >
              \u2715
            </button>
          </div>
        </div>
      )}

      <WelcomeScreen phase={phase} onStart={() => setPhase("setup")} />

      <StorySetup
        phase={phase}
        onComplete={handleSetupComplete}
        onBack={() => setPhase("welcome")}
      />

      {phase === "playing" && (
        <StoryPlayer
          segments={story.state.segments}
          isLoading={story.state.isLoading}
          isComplete={story.state.isComplete}
          turnCount={story.state.turnCount}
          config={story.state.config}
          onChoice={async (choice) => {
            setError(null);
            try {
              await story.makeChoice(choice);
            } catch (err) {
              const msg = err instanceof Error ? err.message : "Story error";
              setError(msg);
            }
          }}
          onCustomInput={async (text) => {
            setError(null);
            try {
              await story.sendCustomInput(text);
            } catch (err) {
              const msg = err instanceof Error ? err.message : "Story error";
              setError(msg);
            }
          }}
          onExport={story.exportStory}
          onReset={handleReset}
        />
      )}
    </main>
  );
}
