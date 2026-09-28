export type ListeningSource = 'file' | 'waiting' | 'speech' | 'transcript' | 'missing';

export function chooseListeningSource(audioUrl: string, transcript: string, fileFailed: boolean, voiceCount: number | null): ListeningSource {
  if (audioUrl && !fileFailed) return 'file';
  if (!transcript.trim()) return 'missing';
  if (voiceCount === null) return 'waiting';
  return voiceCount > 0 ? 'speech' : 'transcript';
}
