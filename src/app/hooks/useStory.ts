"use client";

import { useState, useCallback } from "react";
import {
  StoryConfig,
  StorySegment,
  StoryState,
  StoryChoice,
} from "../types";

export function useStory() {
  const [state, setState] = useState<StoryState>({
    config: null,
    segments: [],
    isLoading: false,
    isComplete: false,
    turnCount: 0,
  });

  const setConfig = useCallback((config: StoryConfig) => {
    setState((prev) => ({ ...prev, config }));
  }, []);

  const startStory = useCallback(async () => {
    if (!state.config) return;

    setState((prev) => ({ ...prev, isLoading: true }));

    try {
      const response = await fetch("/api/story", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          config: state.config,
          history: [],
          action: "start",
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to start story");
      }

      const segment: StorySegment = {
        id: crypto.randomUUID(),
        narrator: "ai",
        text: data.narrative,
        choices: data.choices,
        timestamp: new Date(),
      };

      setState((prev) => ({
        ...prev,
        segments: [segment],
        isLoading: false,
        isComplete: data.isComplete,
        turnCount: 1,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, isLoading: false }));
      throw error;
    }
  }, [state.config]);

  const makeChoice = useCallback(
    async (choice: StoryChoice) => {
      if (!state.config) return;

      const userSegment: StorySegment = {
        id: crypto.randomUUID(),
        narrator: "user",
        text: choice.text,
        timestamp: new Date(),
      };

      setState((prev) => ({
        ...prev,
        segments: [...prev.segments, userSegment],
        isLoading: true,
      }));

      try {
        const response = await fetch("/api/story", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            config: state.config,
            history: [...state.segments, userSegment],
            userChoice: choice.text,
            action: "continue",
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to continue story");
        }

        const aiSegment: StorySegment = {
          id: crypto.randomUUID(),
          narrator: "ai",
          text: data.narrative,
          choices: data.isComplete ? undefined : data.choices,
          timestamp: new Date(),
        };

        setState((prev) => ({
          ...prev,
          segments: [...prev.segments, aiSegment],
          isLoading: false,
          isComplete: data.isComplete,
          turnCount: prev.turnCount + 1,
        }));
      } catch (error) {
        setState((prev) => ({ ...prev, isLoading: false }));
        throw error;
      }
    },
    [state.config, state.segments]
  );

  const sendCustomInput = useCallback(
    async (text: string) => {
      if (!state.config) return;

      const userSegment: StorySegment = {
        id: crypto.randomUUID(),
        narrator: "user",
        text,
        timestamp: new Date(),
      };

      setState((prev) => ({
        ...prev,
        segments: [...prev.segments, userSegment],
        isLoading: true,
      }));

      try {
        const response = await fetch("/api/story", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            config: state.config,
            history: [...state.segments, userSegment],
            userChoice: text,
            action: "custom",
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to continue story");
        }

        const aiSegment: StorySegment = {
          id: crypto.randomUUID(),
          narrator: "ai",
          text: data.narrative,
          choices: data.isComplete ? undefined : data.choices,
          timestamp: new Date(),
        };

        setState((prev) => ({
          ...prev,
          segments: [...prev.segments, aiSegment],
          isLoading: false,
          isComplete: data.isComplete,
          turnCount: prev.turnCount + 1,
        }));
      } catch (error) {
        setState((prev) => ({ ...prev, isLoading: false }));
        throw error;
      }
    },
    [state.config, state.segments]
  );

  const resetStory = useCallback(() => {
    setState({
      config: null,
      segments: [],
      isLoading: false,
      isComplete: false,
      turnCount: 0,
    });
  }, []);

  const exportStory = useCallback(() => {
    if (state.segments.length === 0) return "";

    let exported = `# ${state.config?.theme} Story — ${state.config?.subgenre}\n`;
    exported += `**Setting:** ${state.config?.setting}\n`;
    exported += `**Tone:** ${state.config?.tone}\n\n`;
    exported += `## Characters\n`;
    state.config?.characters.forEach((c) => {
      exported += `- **${c.name}** (${c.role}): ${c.personality}\n`;
    });
    exported += `\n---\n\n`;

    state.segments.forEach((seg) => {
      if (seg.narrator === "ai") {
        exported += `${seg.text}\n\n`;
      } else {
        exported += `> *Your choice: ${seg.text}*\n\n`;
      }
    });

    return exported;
  }, [state.segments, state.config]);

  return {
    state,
    setConfig,
    startStory,
    makeChoice,
    sendCustomInput,
    resetStory,
    exportStory,
  };
}
