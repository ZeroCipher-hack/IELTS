import assert from 'node:assert/strict';
import { test } from 'node:test';
import { chooseListeningSource } from './listening-audio.ts';

test('playable file takes priority over browser speech', () => {
  assert.equal(chooseListeningSource('/media/exam_audio/demo.wav', 'Transcript', false, 0), 'file');
  assert.equal(chooseListeningSource('https://example.com/recording.mp3', 'Transcript', false, 1), 'file');
});

test('failed file waits for voices, then selects speech or visible transcript', () => {
  assert.equal(chooseListeningSource('/media/exam_audio/demo.wav', 'Transcript', true, null), 'waiting');
  assert.equal(chooseListeningSource('/media/exam_audio/demo.wav', 'Transcript', true, 2), 'speech');
  assert.equal(chooseListeningSource('/media/exam_audio/demo.wav', 'Transcript', true, 0), 'transcript');
  assert.equal(chooseListeningSource('', '', true, 0), 'missing');
});
