import assert from 'node:assert/strict';
import { test } from 'node:test';
import { audioTime, chooseEnglishVoice, chooseListeningSource } from './listening-audio.ts';

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

test('English fallback never selects an unrelated language', () => {
  assert.equal(chooseEnglishVoice([{lang: 'ru-RU'}]), null);
  assert.deepEqual(chooseEnglishVoice([{lang: 'ru-RU'}, {lang: 'en-US'}, {lang: 'en-GB'}]), {lang: 'en-GB'});
  assert.deepEqual(chooseEnglishVoice([{lang: 'en-US'}]), {lang: 'en-US'});
  assert.equal(chooseEnglishVoice([]), null);
});

test('audio timestamps handle unknown metadata safely', () => {
  assert.equal(audioTime(125.8), '2:05');
  assert.equal(audioTime(NaN), '0:00');
  assert.equal(audioTime(Infinity), '0:00');
  assert.equal(audioTime(-10), '0:00');
});
