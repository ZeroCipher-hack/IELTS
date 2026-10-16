"""IELTS Listening, 40 questions over four parts. Original content.

The transcript is the exam: manage.py generate_audio reads it aloud and stores
the recording on the exam, so this file is both the script and the answer key.
"""
from .reading_transport import unwrap

TITLE = 'Listening — Riverside: services, work and study'
DURATION = 2400

TRANSCRIPT = unwrap('''PART 1. You will hear a conversation between a woman and a clerk at the
Riverside Community Centre.

CLERK: Good morning, Riverside Community Centre.

WOMAN: Hello. I'd like to join, please.

CLERK: Of course. Can I take your name?

WOMAN: Yes, it's Marion Halvers. That's H-A-L-V-E-R-S.

CLERK: Thank you. And your address?

WOMAN: Forty-two Oakfield Road. I've been here about three months.

CLERK: And a phone number?

WOMAN: Oh seven double seven, three nine one, four oh two.

CLERK: Lovely. Now, membership is twenty-four pounds a year, or you can pay
monthly at two pounds fifty. The yearly option works out cheaper.

WOMAN: I'll take the yearly one. What does it include?

CLERK: Free entry to the library room, a discount on all classes, and use of
the garden. The swimming pool is separate, I'm afraid, because it's run by the
council rather than by us.

WOMAN: That's fine. What classes do you run?

CLERK: On Mondays there's pottery, Wednesdays we have conversational Spanish,
and Thursday evening is the choir. Pottery is the most popular, so there's
usually a short waiting list.

WOMAN: And what time does the choir start?

CLERK: Half past seven, and it finishes at nine. You don't need to read music,
but you do need to come to at least two rehearsals a month.

WOMAN: And is there parking?

CLERK: There is, but it's limited to twelve spaces, so most members walk or
cycle. There's a cycle rack by the side entrance.

PART 2. You will hear a talk about a town's new recycling scheme.

SPEAKER: Good evening, everyone. I'm here to explain the changes to collections
that start next month.

The biggest change is that food waste will now be collected every week, rather
than fortnightly as it is at present. Each household will receive a small
kitchen caddy and a larger outdoor bin. Please do not put food waste in plastic
bags; use the compostable liners we provide, which you can collect free from
the library.

Garden waste is different. That service is now charged, at thirty-five pounds a
year, and you have to register online before your first collection. If you do
not register, the bin will be left.

Glass, paper and metal will continue to be collected together in the blue bin
on alternate Tuesdays. The one thing we ask you to change is that bottles
should be rinsed but not crushed, because crushing makes the sorting machinery
less accurate.

Finally, we are opening a reuse shop at the recycling centre on Mill Lane. It
will sell furniture and bicycles that are still in good condition, and all the
money raised goes to the hospice. The shop opens on the fourteenth of March and
will be staffed entirely by volunteers.

PART 3. You will hear two students, Ravi and Jo, discussing a project.

RAVI: So we need to decide what we're actually measuring, Jo.

JO: I thought we'd settled on noise levels in the library.

RAVI: We had, but the department has only two sound meters and both are booked
until the end of term. I think we should switch to the questionnaire instead.

JO: A questionnaire is quicker, but people report what they think they ought
to say rather than what they do. We'd be measuring opinion, not noise.

RAVI: True. Although for our question that might be enough. We're asking
whether students avoid the library, not how loud it actually is.

JO: That's a fair point. All right, questionnaire. How many responses?

RAVI: Our supervisor said a hundred is the minimum for the statistics to mean
anything. I'd aim for a hundred and fifty, because some will be incomplete.

JO: Agreed. And we should pilot it first, on maybe ten people, to catch
confusing questions.

RAVI: Yes. One more thing: the deadline moved. It's now the twelfth of May,
not the nineteenth.

JO: That's a week earlier. We'll need the data collected by the end of April,
then, to leave time for the analysis.

RAVI: I'll draft the questions this weekend and send them to you on Sunday.

PART 4. You will hear part of a lecture about urban beekeeping.

LECTURER: Keeping bees in cities is not new, but the scale of it is. London
alone now has roughly five thousand registered hives, four times the number
recorded in two thousand and eight.

The enthusiasm is easy to understand. A hive is visible, it produces something
useful, and it feels like a direct contribution to conservation. The difficulty
is that honeybees are livestock, not wildlife. A managed colony contains tens
of thousands of individuals, all foraging from the same limited supply of
flowers, and in dense areas they compete with the wild bees the enthusiasm was
meant to protect.

Research in Paris found that where hive density passed about six hives per
square kilometre, the number of wild bee species recorded in nearby green space
began to fall. The effect was strongest in late summer, when flowering is at
its lowest.

This does not mean urban beekeeping is wrong. It means the order of priorities
is wrong. Planting for pollinators costs very little and benefits every species,
while a hive benefits one. If a city wants more bees, the first step is more
flowers, not more hives, and the most useful plantings are those that bloom in
August and September when little else is available.

The second point concerns training. An unmanaged hive is a source of disease
for every colony within flying distance, which is about three kilometres. Any
scheme that places hives without also funding instruction is likely to do more
harm than good.''')

# (prompt, choices, accepted, evidence, explanation, skill_tag)
ITEMS = [
    # --- Part 1: form completion (1-10) ---
    ('Surname: ________ (spell as given). Write ONE word.',
     [], ['Halvers'], "it's Marion Halvers", 'Ism harflab aytilgan.', 'Form completion'),
    ('Address: ________ Oakfield Road. Write a number.',
     [], ['42', 'forty-two', 'forty two'], 'Forty-two Oakfield Road',
     'Uy raqami aytilgan.', 'Form completion'),
    ('She has lived there for about ________ months. Write a number.',
     [], ['3', 'three'], "I've been here about three months",
     'Muddat suhbatda berilgan.', 'Form completion'),
    ('Yearly membership costs £________. Write a number.',
     [], ['24', 'twenty-four', 'twenty four'], 'membership is twenty-four pounds a year',
     'Yillik narx aytilgan.', 'Form completion'),
    ('Monthly membership costs £________. Write a number.',
     [], ['2.50', '2.5'], 'or you can pay monthly at two pounds fifty',
     'Oylik narx — 2 funt 50 pens.', 'Form completion'),
    ('Membership does NOT include the ________. Write ONE or TWO words.',
     [], ['swimming pool', 'pool'], 'The swimming pool is separate',
     'Basseyn alohida, kengash boshqaradi.', 'Form completion'),
    ('Spanish classes take place on ________. Write ONE word.',
     [], ['Wednesdays', 'Wednesday'], 'Wednesdays we have conversational Spanish',
     'Hafta kuni aytilgan.', 'Form completion'),
    ('The class with a waiting list is ________. Write ONE word.',
     [], ['pottery'], "Pottery is the most popular, so there's usually a short waiting list",
     'Eng mashhuri — kulolchilik.', 'Form completion'),
    ('The choir starts at ________. Write the time.',
     [], ['7.30', '19:30', '7:30', 'half past seven'], 'Half past seven, and it finishes at nine',
     'Boshlanish vaqti aytilgan.', 'Form completion'),
    ('There are only ________ parking spaces. Write a number.',
     [], ['12', 'twelve'], "it's limited to twelve spaces",
     'Joy soni aniq aytilgan.', 'Form completion'),

    # --- Part 2: multiple choice and completion (11-20) ---
    ('How often will food waste be collected?',
     ['Every week', 'Every fortnight', 'Every month', 'On request'],
     ['Every week'], 'food waste will now be collected every week',
     'Chastota o‘zgardi.', 'Multiple choice'),
    ('Food waste must NOT be put in',
     ['plastic bags', 'the kitchen caddy', 'the outdoor bin', 'compostable liners'],
     ['plastic bags'], 'Please do not put food waste in plastic bags',
     'Taqiq aniq aytilgan.', 'Multiple choice'),
    ('Compostable liners can be collected free from the ________. Write ONE word.',
     [], ['library'], 'which you can collect free from the library',
     'Joy aytilgan.', 'Sentence completion'),
    ('The garden waste service now costs £________ a year. Write a number.',
     [], ['35', 'thirty-five', 'thirty five'], 'That service is now charged, at thirty-five pounds a year',
     'Narx aytilgan.', 'Sentence completion'),
    ('Before the first garden waste collection, residents must ________ online. Write ONE word.',
     [], ['register'], 'you have to register online before your first collection',
     'Fe’l aytilgan.', 'Sentence completion'),
    ('Glass, paper and metal are collected in the ________ bin. Write ONE word.',
     [], ['blue'], 'collected together in the blue bin on alternate Tuesdays',
     'Rang aytilgan.', 'Sentence completion'),
    ('Bottles should be rinsed but not ________. Write ONE word.',
     [], ['crushed'], 'bottles should be rinsed but not crushed',
     'Talab aniq.', 'Sentence completion'),
    ('Why should bottles not be crushed?',
     ['It makes sorting machinery less accurate.',
      'It makes the bins too heavy.',
      'It reduces the resale value.',
      'It damages the blue bin.'],
     ['It makes sorting machinery less accurate.'],
     'because crushing makes the sorting machinery less accurate',
     'Sabab aniq aytilgan.', 'Multiple choice'),
    ('The reuse shop will be on ________ Lane. Write ONE word.',
     [], ['Mill'], 'a reuse shop at the recycling centre on Mill Lane',
     'Ko‘cha nomi aytilgan.', 'Sentence completion'),
    ('Money raised by the reuse shop goes to the ________. Write ONE word.',
     [], ['hospice'], 'all the money raised goes to the hospice',
     'Qabul qiluvchi aytilgan.', 'Sentence completion'),

    # --- Part 3: multiple choice and completion (21-30) ---
    ('Why do the students change their method?',
     ['The sound meters are unavailable.',
      'Their supervisor rejected the first plan.',
      'The library refused permission.',
      'Noise levels are too variable.'],
     ['The sound meters are unavailable.'],
     'the department has only two sound meters and both are booked until the end of term',
     'Asbob yo‘qligi sabab.', 'Multiple choice'),
    ('How many sound meters does the department own? Write a number.',
     [], ['2', 'two'], 'the department has only two sound meters',
     'Son aytilgan.', 'Short answer'),
    ("What is Jo's objection to a questionnaire?",
     ['It measures opinion rather than behaviour.',
      'It takes longer to analyse.',
      'It needs permission from the library.',
      'It cannot reach enough students.'],
     ['It measures opinion rather than behaviour.'],
     "We'd be measuring opinion, not noise.",
     'Jo fikrni o‘lchashdan xavotirda.', 'Multiple choice'),
    ('What is the minimum number of responses their supervisor advised? Write a number.',
     [], ['100', 'a hundred', 'one hundred'],
     'a hundred is the minimum for the statistics to mean anything',
     'Minimal son aytilgan.', 'Short answer'),
    ('How many responses does Ravi want to aim for? Write a number.',
     [], ['150', 'a hundred and fifty', 'one hundred and fifty'],
     "I'd aim for a hundred and fifty, because some will be incomplete",
     'Ravi ko‘proq maqsad qo‘yadi.', 'Short answer'),
    ('Why does Ravi want more than the minimum?',
     ['Some responses will be incomplete.',
      'The supervisor asked for more.',
      'The library is very large.',
      'They expect refusals.'],
     ['Some responses will be incomplete.'],
     'because some will be incomplete',
     'Sabab aniq.', 'Multiple choice'),
    ('They will pilot the questionnaire on about ________ people. Write a number.',
     [], ['10', 'ten'], 'we should pilot it first, on maybe ten people',
     'Sinov guruhi hajmi.', 'Sentence completion'),
    ('The purpose of the pilot is to catch ________ questions. Write ONE word.',
     [], ['confusing'], 'to catch confusing questions',
     'Maqsad aytilgan.', 'Sentence completion'),
    ('The new deadline is the ________ of May. Write a number.',
     [], ['12', 'twelfth'], "It's now the twelfth of May, not the nineteenth",
     'Yangi muddat.', 'Sentence completion'),
    ('Data must be collected by the end of ________. Write ONE word.',
     [], ['April'], "We'll need the data collected by the end of April",
     'Oy aytilgan.', 'Sentence completion'),

    # --- Part 4: lecture (31-40) ---
    ('London now has roughly ________ registered hives. Write a number.',
     [], ['5000', '5,000', 'five thousand'],
     'London alone now has roughly five thousand registered hives',
     'Son aytilgan.', 'Sentence completion'),
    ('That is ________ times the number recorded in 2008. Write a number.',
     [], ['4', 'four'], 'four times the number recorded in two thousand and eight',
     'Nisbat aytilgan.', 'Sentence completion'),
    ('The lecturer says honeybees should be thought of as',
     ['livestock', 'wildlife', 'pests', 'pollinator specialists'],
     ['livestock'], 'honeybees are livestock, not wildlife',
     'Asosiy tezis.', 'Multiple choice'),
    ('In dense areas managed colonies compete with ________ bees. Write ONE word.',
     [], ['wild'], 'they compete with the wild bees the enthusiasm was meant to protect',
     'Raqobat yovvoyi asalarilar bilan.', 'Sentence completion'),
    ('Wild bee species began to fall above about ________ hives per square kilometre. Write a number.',
     [], ['6', 'six'], 'where hive density passed about six hives per square kilometre',
     'Chegara aytilgan.', 'Sentence completion'),
    ('The effect was strongest in late ________. Write ONE word.',
     [], ['summer'], 'The effect was strongest in late summer',
     'Fasl aytilgan.', 'Sentence completion'),
    ('According to the lecturer, what should a city do first?',
     ['Plant more flowers', 'Install more hives', 'Ban urban beekeeping', 'Register all beekeepers'],
     ['Plant more flowers'],
     'the first step is more flowers, not more hives',
     'Ustuvorlik tartibi.', 'Multiple choice'),
    ('The most useful plantings bloom in August and ________. Write ONE word.',
     [], ['September'], 'those that bloom in August and September',
     'Oy aytilgan.', 'Sentence completion'),
    ('A hive can spread disease to colonies within about ________ kilometres. Write a number.',
     [], ['3', 'three'], 'which is about three kilometres',
     'Masofa aytilgan.', 'Sentence completion'),
    ('What does the lecturer say about schemes that place hives without funding instruction?',
     ['They are likely to do more harm than good.',
      'They should be expanded quickly.',
      'They work well in small towns.',
      'They are cheaper than planting.'],
     ['They are likely to do more harm than good.'],
     'is likely to do more harm than good',
     'Xulosa aniq.', 'Multiple choice'),
]
