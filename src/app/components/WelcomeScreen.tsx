"use client";

import { useMemo } from "react";
import { AppPhase } from "../types";

const PARTICLE_COUNT = 20;

interface WelcomeScreenProps {
  onStart: () => void;
  phase: AppPhase;
}

export default function WelcomeScreen({ onStart, phase }: WelcomeScreenProps) {
  const particles = useMemo(
    () =>
      Array.from({ length: PARTICLE_COUNT }, (_, i) => ({
        id: i,
        width: ((i * 7 + 3) % 10) + 4,
        height: ((i * 11 + 5) % 10) + 4,
        left: ((i * 37 + 13) % 100),
        top: ((i * 53 + 7) % 100),
        delay: ((i * 3 + 1) % 5),
        duration: ((i * 7 + 2) % 10) + 10,
      })),
    []
  );

  if (phase !== "welcome") return null;

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden">
        {particles.map((p) => (
          <div
            key={p.id}
            className={`absolute rounded-full bg-amber-400/10 animate-float particle-${p.id}`}
          />
        ))}
      </div>

      <div className="text-center z-10 px-4">
        {/* Book icon */}
        <div className="mb-8 animate-pulse-slow">
          <span className="text-8xl md:text-9xl block">📖</span>
        </div>

        <h1 className="text-5xl md:text-7xl font-bold mb-4 bg-linear-to-r from-amber-300 via-yellow-200 to-amber-400 bg-clip-text text-transparent drop-shadow-lg">
          Story Weaver
        </h1>

        <p className="text-xl md:text-2xl text-gray-300 mb-2 font-light tracking-wide">
          Interactive AI Storytelling Adventure
        </p>

        <p className="text-sm md:text-base text-gray-500 mb-12 max-w-lg mx-auto">
          Craft unique narratives with AI as your co-author. Choose your genre,
          create characters, and shape the story with every decision.
        </p>

        <button
          onClick={onStart}
          className="group relative px-10 py-4 bg-linear-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-gray-950 font-bold text-lg rounded-xl transition-all duration-300 transform hover:scale-105 hover:shadow-[0_0_40px_rgba(217,169,56,0.4)] active:scale-95"
        >
          <span className="flex items-center gap-3">
            <span>Begin Your Adventure</span>
            <span className="group-hover:translate-x-1 transition-transform">→</span>
          </span>
        </button>

        <div className="mt-16 flex justify-center gap-8 text-gray-600 text-sm">
          <div className="flex items-center gap-2">
            <span>🎭</span> Choose Your Genre
          </div>
          <div className="flex items-center gap-2">
            <span>👤</span> Create Characters
          </div>
          <div className="flex items-center gap-2">
            <span>🌿</span> Shape the Story
          </div>
        </div>
      </div>
    </div>
  );
}
