export interface Character {
  name: string;
  personality: string;
  background: string;
  role: string;
}

export interface StoryChoice {
  id: string;
  text: string;
}

export interface StorySegment {
  id: string;
  narrator: "ai" | "user";
  text: string;
  choices?: StoryChoice[];
  chosenOption?: string;
  timestamp: Date;
}

export interface StoryConfig {
  theme: string;
  subgenre: string;
  setting: string;
  tone: string;
  characters: Character[];
}

export interface StoryState {
  config: StoryConfig | null;
  segments: StorySegment[];
  isLoading: boolean;
  isComplete: boolean;
  turnCount: number;
}

export type AppPhase = "welcome" | "setup" | "playing" | "complete";

export const THEMES = [
  {
    id: "fantasy",
    name: "Fantasy",
    icon: "🏰",
    description: "Magic, mythical creatures, and epic quests",
    subgenres: ["High Fantasy", "Dark Fantasy", "Fairy Tale", "Mythological"],
  },
  {
    id: "scifi",
    name: "Science Fiction",
    icon: "🚀",
    description: "Space exploration, future tech, and alien worlds",
    subgenres: ["Space Opera", "Cyberpunk", "Post-Apocalyptic", "Time Travel"],
  },
  {
    id: "mystery",
    name: "Mystery",
    icon: "🔍",
    description: "Puzzles, clues, and thrilling investigations",
    subgenres: ["Detective Noir", "Cozy Mystery", "Psychological Thriller", "Heist"],
  },
  {
    id: "adventure",
    name: "Adventure",
    icon: "⚔️",
    description: "Daring exploits, treasure hunts, and survival",
    subgenres: ["Exploration", "Treasure Hunt", "Survival", "Swashbuckling"],
  },
  {
    id: "horror",
    name: "Horror",
    icon: "👻",
    description: "Spine-chilling tales and supernatural encounters",
    subgenres: ["Gothic", "Cosmic Horror", "Haunted", "Survival Horror"],
  },
  {
    id: "romance",
    name: "Romance",
    icon: "💕",
    description: "Love, relationships, and emotional journeys",
    subgenres: ["Historical Romance", "Contemporary", "Fantasy Romance", "Star-Crossed"],
  },
];

export const TONES = [
  { id: "epic", name: "Epic & Grand", icon: "⚡" },
  { id: "lighthearted", name: "Lighthearted & Fun", icon: "🌈" },
  { id: "dark", name: "Dark & Gritty", icon: "🌑" },
  { id: "mysterious", name: "Mysterious & Suspenseful", icon: "🌫️" },
  { id: "whimsical", name: "Whimsical & Playful", icon: "✨" },
  { id: "dramatic", name: "Dramatic & Intense", icon: "🔥" },
];

export const CHARACTER_ROLES = [
  "Hero / Protagonist",
  "Mentor / Guide",
  "Sidekick / Companion",
  "Villain / Antagonist",
  "Mysterious Stranger",
  "Love Interest",
];
