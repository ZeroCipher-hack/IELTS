"""Bounded speaking practice configuration; no official scoring or payment access."""
from django.conf import settings
from .gemini import configured
CUE = {'title': 'Describe a place where you enjoy spending time.', 'points': ['Where it is', 'What you do there', 'Who you usually go with', 'Why you enjoy this place']}

def access(user):
    allowed = user.is_staff or settings.VOICE_PRACTICE_ENABLED
    return {'configured': configured(), 'allowed': allowed, 'reason': 'AI_NOT_CONFIGURED' if not configured() else '' if allowed else 'VOICE_PRACTICE_DISABLED', 'cue': CUE}

def constraints(part):
    instructions = {
        1: 'Conduct Part 1 practice. Ask short questions about home, studies, work and hobbies, one at a time. Ask a relevant follow-up after each complete answer.',
        2: 'Conduct Part 2 practice. The candidate has already had one minute to prepare this cue card: '+CUE['title']+' '+ '; '.join(CUE['points'])+'. Briefly invite them to begin. Let them speak at length; do not interrupt pauses or ask follow-up questions until they explicitly finish.',
        3: 'Conduct Part 3 practice, discussing public places and communities, related to this cue card: '+CUE['title']+'. Ask one abstract question at a time about changes, causes, comparisons and consequences. Wait for each full answer.'
    }
    return {'model': 'models/'+settings.GEMINI_LIVE_MODEL, 'generationConfig': {'responseModalities': ['AUDIO']}, 'inputAudioTranscription': {}, 'outputAudioTranscription': {},
        'systemInstruction': {'parts': [{'text': 'You are an AI English speaking practice examiner, not a human examiner. Speak only English. Do not translate, coach, give model answers, award bands or claim an official exam. Never request identity documents or private data. '+instructions[part]}]}
    }
