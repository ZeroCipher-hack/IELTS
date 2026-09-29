export type ScriptedTurn = { action: 'play' | 'replace' | 'ignore'; question: string };

function normal(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().replace(/\s+/g, ' ');
}

export function scriptedTurn(part: number, questions: string[], index: number, answered: boolean,
  spoken: string, cueTitle: string): ScriptedTurn {
  const question = part === 2 ? `Please begin your talk. ${cueTitle}` : questions[index];
  if (!question || (part === 2 && index > 0) || (index > 0 && !answered)) return { action: 'ignore', question: '' };
  const actual = normal(spoken);
  const valid = part === 2
    ? actual.includes(normal(cueTitle)) && /\b(begin|start)\b/.test(actual)
    : actual === normal(question);
  return { action: valid ? 'play' : 'replace', question };
}
