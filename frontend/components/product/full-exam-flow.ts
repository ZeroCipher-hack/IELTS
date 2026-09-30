export const fullExamKey = 'ieltsqa-full-exam';
export type FullExamFlow = {ids: number[]; step: number; attempts: string[]; startedAt: string; speaking: 'pending' | 'submitted' | 'skipped'};

export function parseFullExamFlow(raw: string | null): FullExamFlow | null {
  if (!raw) return null;
  try {
    const value = JSON.parse(raw);
    if (!value || !Array.isArray(value.ids) || value.ids.length !== 3 ||
      value.ids.some((id: unknown) => !Number.isSafeInteger(id) || Number(id) < 1) || new Set(value.ids).size !== 3 ||
      !Number.isInteger(value.step) || value.step < 0 || value.step > 3 ||
      !Array.isArray(value.attempts) || value.attempts.length > 4 ||
      value.attempts.some((id: unknown) => typeof id !== 'string' || !/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(id)) ||
      new Set(value.attempts).size !== value.attempts.length ||
      typeof value.startedAt !== 'string' || !Number.isFinite(Date.parse(value.startedAt))) return null;
    const speaking = value.speaking ?? (value.attempts.length === 4 ? 'submitted' : 'pending');
    if (!['pending', 'submitted', 'skipped'].includes(speaking)) return null;
    return {ids: value.ids, step: value.step, attempts: value.attempts, startedAt: value.startedAt, speaking};
  } catch { return null; }
}

export function nextFullExamPath(flow: FullExamFlow): string {
  if (flow.step < flow.ids.length) return `/dashboard/tests/${flow.ids[flow.step]}?full=1`;
  return flow.speaking === 'pending' ? '/dashboard/speaking?full=1' : '/dashboard/full-exam?results=1';
}

export function completeFullExamSection(flow: FullExamFlow, examId: number, attemptId: string): FullExamFlow {
  if (flow.attempts.includes(attemptId)) return flow;
  if (flow.ids.indexOf(examId) >= 0 && flow.ids.indexOf(examId) < flow.step) return flow;
  if (flow.ids[flow.step] !== examId) throw new Error('Full exam section is out of order.');
  return {...flow, step: flow.step + 1, attempts: [...flow.attempts, attemptId]};
}

export function finishFullExamSpeaking(flow: FullExamFlow, attemptId?: string): FullExamFlow {
  if (flow.step !== 3) throw new Error('Finish the written sections first.');
  if (flow.speaking === 'submitted') return flow;
  return {...flow, speaking: attemptId ? 'submitted' : 'skipped',
    attempts: attemptId && !flow.attempts.includes(attemptId) ? [...flow.attempts, attemptId] : flow.attempts};
}
