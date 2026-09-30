export type ListeningSource = 'file' | 'waiting' | 'speech' | 'transcript' | 'missing';

export function chooseListeningSource(audioUrl: string, transcript: string, fileFailed: boolean, voiceCount: number | null): ListeningSource {
  if (audioUrl && !fileFailed) return 'file';
  if (!transcript.trim()) return 'missing';
  if (voiceCount === null) return 'waiting';
  return voiceCount > 0 ? 'speech' : 'transcript';
}

export function chooseEnglishVoice<T extends {lang: string}>(voices: T[]): T | null {
  return voices.find(voice => /^en[-_]GB$/i.test(voice.lang))
    || voices.find(voice => /^en(?:[-_]|$)/i.test(voice.lang)) || null;
}

export function audioTime(value: number): string {
  const seconds = Number.isFinite(value) ? Math.max(0, Math.floor(value)) : 0;
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
}
