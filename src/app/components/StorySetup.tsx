"use client";

import { useState } from "react";
import {
  AppPhase,
  StoryConfig,
  Character,
  THEMES,
  TONES,
  CHARACTER_ROLES,
} from "../types";

interface StorySetupProps {
  phase: AppPhase;
  onComplete: (config: StoryConfig) => void;
  onBack: () => void;
}

type SetupStep = "theme" | "subgenre" | "setting" | "tone" | "characters" | "review";

export default function StorySetup({ phase, onComplete, onBack }: StorySetupProps) {
  const [step, setStep] = useState<SetupStep>("theme");
  const [selectedTheme, setSelectedTheme] = useState("");
  const [selectedSubgenre, setSelectedSubgenre] = useState("");
  const [setting, setSetting] = useState("");
  const [selectedTone, setSelectedTone] = useState("");
  const [characters, setCharacters] = useState<Character[]>([
    { name: "", personality: "", background: "", role: CHARACTER_ROLES[0] },
  ]);

  if (phase !== "setup") return null;

  const currentTheme = THEMES.find((t) => t.id === selectedTheme);

  const addCharacter = () => {
    if (characters.length < 4) {
      setCharacters([
        ...characters,
        { name: "", personality: "", background: "", role: CHARACTER_ROLES[1] },
      ]);
    }
  };

  const removeCharacter = (index: number) => {
    if (characters.length > 1) {
      setCharacters(characters.filter((_, i) => i !== index));
    }
  };

  const updateCharacter = (index: number, field: keyof Character, value: string) => {
    const updated = [...characters];
    updated[index] = { ...updated[index], [field]: value };
    setCharacters(updated);
  };

  const handleComplete = () => {
    const config: StoryConfig = {
      theme: currentTheme?.name || "",
      subgenre: selectedSubgenre,
      setting,
      tone: TONES.find((t) => t.id === selectedTone)?.name || "",
      characters: characters.filter((c) => c.name.trim() !== ""),
    };
    onComplete(config);
  };

  const canProceed = () => {
    switch (step) {
      case "theme":
        return selectedTheme !== "";
      case "subgenre":
        return selectedSubgenre !== "";
      case "setting":
        return setting.trim() !== "";
      case "tone":
        return selectedTone !== "";
      case "characters":
        return characters.some(
          (c) => c.name.trim() !== "" && c.personality.trim() !== ""
        );
      case "review":
        return true;
      default:
        return false;
    }
  };

  const nextStep = () => {
    const steps: SetupStep[] = ["theme", "subgenre", "setting", "tone", "characters", "review"];
    const idx = steps.indexOf(step);
    if (idx < steps.length - 1) setStep(steps[idx + 1]);
  };

  const prevStep = () => {
    const steps: SetupStep[] = ["theme", "subgenre", "setting", "tone", "characters", "review"];
    const idx = steps.indexOf(step);
    if (idx > 0) setStep(steps[idx - 1]);
    else onBack();
  };

  const stepNumber = ["theme", "subgenre", "setting", "tone", "characters", "review"].indexOf(step) + 1;

  const STEP_WIDTH_CLASS: Record<number, string> = {
    1: "w-[17%]",
    2: "w-[33%]",
    3: "w-1/2",
    4: "w-[67%]",
    5: "w-[83%]",
    6: "w-full",
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-8">
      {/* Progress bar */}
      <div className="w-full max-w-2xl mb-8">
        <div className="flex justify-between text-xs text-gray-500 mb-2">
          <span>Step {stepNumber} of 6</span>
          <span>{Math.round((stepNumber / 6) * 100)}%</span>
        </div>
        <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
          <div
            className={`h-full bg-linear-to-r from-amber-600 to-amber-400 rounded-full transition-all duration-500 ${STEP_WIDTH_CLASS[stepNumber]}`}
          />
        </div>
        <progress
          className="sr-only"
          value={stepNumber}
          max={6}
        >
          Step {stepNumber} of 6
        </progress>
      </div>

      <div className="w-full max-w-2xl">
        {/* Theme Selection */}
        {step === "theme" && (
          <div className="animate-fadeIn">
            <h2 className="text-3xl font-bold text-center mb-2 text-amber-200">
              Choose Your Genre
            </h2>
            <p className="text-gray-400 text-center mb-8">
              What kind of story would you like to tell?
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {THEMES.map((theme) => (
                <button
                  key={theme.id}
                  onClick={() => setSelectedTheme(theme.id)}
                  className={`p-5 rounded-xl border-2 transition-all duration-300 text-left hover:scale-[1.02] ${
                    selectedTheme === theme.id
                      ? "border-amber-500 bg-amber-500/10 shadow-[0_0_20px_rgba(217,169,56,0.2)]"
                      : "border-gray-700/50 bg-gray-900/50 hover:border-gray-600"
                  }`}
                >
                  <span className="text-3xl block mb-2">{theme.icon}</span>
                  <span className="font-semibold text-gray-200 block">
                    {theme.name}
                  </span>
                  <span className="text-xs text-gray-500 block mt-1">
                    {theme.description}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Subgenre Selection */}
        {step === "subgenre" && currentTheme && (
          <div className="animate-fadeIn">
            <h2 className="text-3xl font-bold text-center mb-2 text-amber-200">
              {currentTheme.icon} Refine Your {currentTheme.name}
            </h2>
            <p className="text-gray-400 text-center mb-8">
              Pick a subgenre to shape the story&apos;s style
            </p>
            <div className="grid grid-cols-2 gap-4">
              {currentTheme.subgenres.map((sub) => (
                <button
                  key={sub}
                  onClick={() => setSelectedSubgenre(sub)}
                  className={`p-5 rounded-xl border-2 transition-all duration-300 text-center hover:scale-[1.02] ${
                    selectedSubgenre === sub
                      ? "border-amber-500 bg-amber-500/10 shadow-[0_0_20px_rgba(217,169,56,0.2)]"
                      : "border-gray-700/50 bg-gray-900/50 hover:border-gray-600"
                  }`}
                >
                  <span className="font-semibold text-gray-200">{sub}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Setting */}
        {step === "setting" && (
          <div className="animate-fadeIn">
            <h2 className="text-3xl font-bold text-center mb-2 text-amber-200">
              Describe the Setting
            </h2>
            <p className="text-gray-400 text-center mb-8">
              Where does your story take place? Be as creative as you want!
            </p>
            <textarea
              value={setting}
              onChange={(e) => setSetting(e.target.value)}
              placeholder={`e.g., "A forgotten kingdom floating above the clouds, where ancient libraries hold the secrets of lost civilizations..."`}
              className="w-full h-40 p-4 bg-gray-900/50 border-2 border-gray-700/50 rounded-xl text-gray-200 placeholder:text-gray-600 focus:outline-none focus:border-amber-500/50 resize-none transition-colors"
            />
            <p className="text-xs text-gray-600 mt-2 text-right">
              {setting.length} characters
            </p>
          </div>
        )}

        {/* Tone Selection */}
        {step === "tone" && (
          <div className="animate-fadeIn">
            <h2 className="text-3xl font-bold text-center mb-2 text-amber-200">
              Set the Tone
            </h2>
            <p className="text-gray-400 text-center mb-8">
              How should the story feel?
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {TONES.map((tone) => (
                <button
                  key={tone.id}
                  onClick={() => setSelectedTone(tone.id)}
                  className={`p-5 rounded-xl border-2 transition-all duration-300 text-center hover:scale-[1.02] ${
                    selectedTone === tone.id
                      ? "border-amber-500 bg-amber-500/10 shadow-[0_0_20px_rgba(217,169,56,0.2)]"
                      : "border-gray-700/50 bg-gray-900/50 hover:border-gray-600"
                  }`}
                >
                  <span className="text-2xl block mb-2">{tone.icon}</span>
                  <span className="font-semibold text-gray-200 text-sm">
                    {tone.name}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Character Creation */}
        {step === "characters" && (
          <div className="animate-fadeIn">
            <h2 className="text-3xl font-bold text-center mb-2 text-amber-200">
              Create Your Characters
            </h2>
            <p className="text-gray-400 text-center mb-8">
              Introduce the people who will bring your story to life
            </p>
            <div className="space-y-6">
              {characters.map((char, idx) => (
                <div
                  key={idx}
                  className="p-5 bg-gray-900/50 border border-gray-700/50 rounded-xl space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-amber-400 font-semibold text-sm">
                      Character {idx + 1}
                    </span>
                    {characters.length > 1 && (
                      <button
                        onClick={() => removeCharacter(idx)}
                        className="text-red-500/60 hover:text-red-400 text-sm transition-colors"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <input
                      type="text"
                      value={char.name}
                      onChange={(e) => updateCharacter(idx, "name", e.target.value)}
                      placeholder="Character name"
                      className="p-3 bg-gray-800/50 border border-gray-700/50 rounded-lg text-gray-200 placeholder:text-gray-600 focus:outline-none focus:border-amber-500/50 text-sm"
                    />
                    <select
                      value={char.role}
                      onChange={(e) => updateCharacter(idx, "role", e.target.value)}
                      aria-label={`Role for character ${idx + 1}`}
                      className="p-3 bg-gray-800/50 border border-gray-700/50 rounded-lg text-gray-200 focus:outline-none focus:border-amber-500/50 text-sm"
                    >
                      {CHARACTER_ROLES.map((role) => (
                        <option key={role} value={role}>
                          {role}
                        </option>
                      ))}
                    </select>
                  </div>
                  <input
                    type="text"
                    value={char.personality}
                    onChange={(e) => updateCharacter(idx, "personality", e.target.value)}
                    placeholder="Personality traits (e.g., brave, cunning, compassionate)"
                    className="w-full p-3 bg-gray-800/50 border border-gray-700/50 rounded-lg text-gray-200 placeholder:text-gray-600 focus:outline-none focus:border-amber-500/50 text-sm"
                  />
                  <input
                    type="text"
                    value={char.background}
                    onChange={(e) => updateCharacter(idx, "background", e.target.value)}
                    placeholder="Brief background (e.g., an exiled prince seeking redemption)"
                    className="w-full p-3 bg-gray-800/50 border border-gray-700/50 rounded-lg text-gray-200 placeholder:text-gray-600 focus:outline-none focus:border-amber-500/50 text-sm"
                  />
                </div>
              ))}
              {characters.length < 4 && (
                <button
                  onClick={addCharacter}
                  className="w-full p-3 border-2 border-dashed border-gray-700 rounded-xl text-gray-500 hover:border-amber-600/50 hover:text-amber-400 transition-colors text-sm"
                >
                  + Add Another Character
                </button>
              )}
            </div>
          </div>
        )}

        {/* Review */}
        {step === "review" && (
          <div className="animate-fadeIn">
            <h2 className="text-3xl font-bold text-center mb-2 text-amber-200">
              Your Story Awaits
            </h2>
            <p className="text-gray-400 text-center mb-8">
              Review your story setup before embarking on your adventure
            </p>
            <div className="bg-gray-900/50 border border-gray-700/50 rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{currentTheme?.icon}</span>
                <div>
                  <span className="text-amber-400 text-xs uppercase tracking-wider">
                    Genre
                  </span>
                  <p className="text-gray-200 font-semibold">
                    {currentTheme?.name} — {selectedSubgenre}
                  </p>
                </div>
              </div>
              <hr className="border-gray-800" />
              <div>
                <span className="text-amber-400 text-xs uppercase tracking-wider">
                  Setting
                </span>
                <p className="text-gray-300 mt-1">{setting}</p>
              </div>
              <hr className="border-gray-800" />
              <div>
                <span className="text-amber-400 text-xs uppercase tracking-wider">
                  Tone
                </span>
                <p className="text-gray-300 mt-1">
                  {TONES.find((t) => t.id === selectedTone)?.icon}{" "}
                  {TONES.find((t) => t.id === selectedTone)?.name}
                </p>
              </div>
              <hr className="border-gray-800" />
              <div>
                <span className="text-amber-400 text-xs uppercase tracking-wider">
                  Characters
                </span>
                <div className="mt-2 space-y-2">
                  {characters
                    .filter((c) => c.name.trim())
                    .map((c, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <span className="text-amber-500">•</span>
                        <div>
                          <span className="text-gray-200 font-semibold">
                            {c.name}
                          </span>
                          <span className="text-gray-500"> ({c.role})</span>
                          <p className="text-gray-400 text-sm">
                            {c.personality}
                            {c.background ? ` — ${c.background}` : ""}
                          </p>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between mt-8">
          <button
            onClick={prevStep}
            className="px-6 py-3 text-gray-400 hover:text-gray-200 transition-colors flex items-center gap-2"
          >
            <span>←</span> Back
          </button>
          {step === "review" ? (
            <button
              onClick={handleComplete}
              className="px-8 py-3 bg-linear-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-gray-950 font-bold rounded-xl transition-all duration-300 hover:shadow-[0_0_30px_rgba(217,169,56,0.3)] flex items-center gap-2"
            >
              <span>🚀</span> Start the Adventure
            </button>
          ) : (
            <button
              onClick={nextStep}
              disabled={!canProceed()}
              className="px-8 py-3 bg-amber-600 hover:bg-amber-500 disabled:bg-gray-800 disabled:text-gray-600 text-gray-950 disabled:cursor-not-allowed font-semibold rounded-xl transition-all duration-300 flex items-center gap-2"
            >
              Next <span>→</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
