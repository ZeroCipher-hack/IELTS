import assert from 'node:assert/strict';
import test from 'node:test';
import {assessmentMessage} from './assessment-message.ts';
test('known failure causes are localized without showing provider text', () => {
  assert.match(assessmentMessage('AI_RECORDING_UNAVAILABLE','uz')!,/qayta yozib/);
  assert.match(assessmentMessage('AI_INSUFFICIENT_AUDIO','en')!,/clear speech/);
  assert.match(assessmentMessage('AI_RATE_LIMIT','ru')!,/Лимит/);
  assert.equal(assessmentMessage('provider error with secret text','uz'),null);
  assert.equal(assessmentMessage(undefined,'uz'),null);
});
