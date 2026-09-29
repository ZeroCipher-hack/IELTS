import assert from 'node:assert/strict';
import test from 'node:test';
import { scriptedTurn } from './speaking-script.ts';

const questions = ['What is your hometown like?', 'How do you spend your free time?'];

test('accepts only the next exact scripted question', () => {
  assert.equal(scriptedTurn(1, questions, 0, false, 'What is your hometown like?', '').action, 'play');
  assert.deepEqual(scriptedTurn(1, questions, 0, false, 'Tell me about the holiday you mentioned.', ''),
    { action: 'replace', question: questions[0] });
  assert.equal(scriptedTurn(1, questions, 1, false, questions[1], '').action, 'ignore');
  assert.equal(scriptedTurn(1, questions, 1, true, questions[1], '').action, 'play');
  assert.equal(scriptedTurn(1, questions, 2, true, 'Where do you travel?', '').action, 'ignore');
});

test('Part 2 does not accept a different cue card', () => {
  const cue = 'Describe a place where you enjoy spending time.';
  assert.equal(scriptedTurn(2, [], 0, false, 'Please begin. Describe a place where you enjoy spending time.', cue).action, 'play');
  assert.equal(scriptedTurn(2, [], 0, false, 'Please begin describing a holiday abroad.', cue).action, 'replace');
  assert.equal(scriptedTurn(2, [], 1, true, 'What about your hobbies?', cue).action, 'ignore');
});
