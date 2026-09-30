import assert from 'node:assert/strict';
import test from 'node:test';
import {completeFullExamSection, finishFullExamSpeaking, nextFullExamPath, parseFullExamFlow, type FullExamFlow} from './full-exam-flow.ts';
const a = '11111111-1111-4111-8111-111111111111';
const b = '22222222-2222-4222-8222-222222222222';
const flow: FullExamFlow = {ids:[1,2,3], step:0, attempts:[], startedAt:'2026-09-30T00:00:00Z', speaking:'pending'};
test('legacy flows restore and malformed storage is rejected', () => {
  const {speaking, ...legacy} = flow;
  assert.equal(parseFullExamFlow(JSON.stringify(legacy))?.speaking, 'pending');
  for (const value of [null, {}, {...flow, step:99}, {...flow, ids:[1,1,3]}, {...flow, attempts:['invalid']}, {...flow, speaking:'invented'}]) {
    assert.equal(parseFullExamFlow(JSON.stringify(value)), null);
  }
});
test('section completion is idempotent and preserves the current step on revisit', () => {
  const reading = completeFullExamSection(flow,1,a);
  assert.equal(reading.step,1);
  assert.equal(nextFullExamPath(reading),'/dashboard/tests/2?full=1');
  assert.deepEqual(completeFullExamSection(reading,1,a),reading);
  assert.deepEqual(completeFullExamSection(reading,1,b),reading);
  assert.throws(() => completeFullExamSection(flow,3,a));
});
test('Speaking submission and skipping are distinct and cannot duplicate attempts', () => {
  const written = {...flow, step:3, attempts:[a]};
  assert.equal(nextFullExamPath(written),'/dashboard/speaking?full=1');
  const submitted = finishFullExamSpeaking(written,b);
  assert.equal(submitted.speaking,'submitted');
  assert.deepEqual(finishFullExamSpeaking(submitted,b).attempts,[a,b]);
  assert.equal(finishFullExamSpeaking(written).speaking,'skipped');
  assert.equal(nextFullExamPath(submitted),'/dashboard/full-exam?results=1');
  assert.throws(() => finishFullExamSpeaking(flow,b));
});
