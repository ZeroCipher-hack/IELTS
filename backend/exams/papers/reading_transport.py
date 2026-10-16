"""Academic Reading, 40 questions over three passages. Original content."""

TITLE = 'Academic Reading — Movement, materials and memory'
DURATION = 3600


def unwrap(text):
    """Join the hard line breaks inside each paragraph.

    The source is wrapped for reading here, but evidence quotes are matched
    against the stored passage character for character: a quote that crosses a
    line break would never be found, and the results page would show no
    evidence at all for that question.
    """
    return '\n\n'.join(' '.join(block.split())
                        for block in text.strip().split('\n\n'))


PASSAGE = unwrap('''PASSAGE 1 — The return of the tram

For most of the twentieth century the tram was treated as an obstacle. Cities
across Europe and North America tore up their rails to make room for cars,
and by 1970 only a handful of systems survived. The reversal since has been
remarkable: more than two hundred cities have opened a tram or light-rail line
since 1980, and several of them are the same cities that removed one.

The usual explanation is congestion, but congestion alone does not account for
the pattern. Bus lanes are far cheaper and can be installed in months rather
than years. What trams offer that buses do not is permanence. A rail line
cannot be quietly rerouted when a budget tightens, and developers read that
permanence as a promise. In Nantes, property values within three hundred
metres of the first new line rose faster than the city average for a decade
after it opened, while an express bus corridor introduced in the same period
produced no measurable effect.

Permanence cuts both ways. A tram line fixed in concrete serves the city that
existed when it was planned, and planning takes years. Grenoble's network was
designed around an industrial district that had largely closed before the
second line opened. Operators responded by extending the line rather than
admitting the error, and the extension carried fewer passengers per kilometre
than any other section.

Cost is the argument that will not go away. A kilometre of tram track costs
roughly fifteen to thirty times a kilometre of bus lane, and the gap has
widened as utility diversion has become more complex. Defenders answer that
the comparison is unfair, because a tram lasts forty years and carries more
people per driver. Critics reply that the saving assumes the line is full, and
most are not. Neither side has produced a study that both accept.

What is agreed is that the decision is rarely made on transport grounds alone.
A tram is visible in a way a bus is not. It appears in tourist photographs and
on city logos. Officials interviewed for a 2019 survey of eleven French cities
named image and regeneration more often than journey times when asked why
their network had been built.


PASSAGE 2 — Reading the rings

A tree records the weather. In temperate climates a trunk adds a pale band of
fast spring growth and a dark band of slow summer growth each year, and the
width of that pair depends on how good the year was. Counting the rings gives
the age of the tree; measuring them gives a chronology of the climate it grew
in. The discipline that does this is called dendrochronology, and it began not
with climate but with sunspots.

In the early twentieth century the astronomer A. E. Douglass was looking for
evidence that solar cycles influenced rainfall. He needed a long record of
rainfall and found one in pine trees in Arizona. The trees did not settle the
sunspot question, but Douglass noticed something more useful: the pattern of
wide and narrow rings was shared between trees growing in the same region. A
distinctive run of narrow rings in one trunk could be matched to the same run
in another, and if the second tree was older, the record could be extended
backwards. Repeated across overlapping samples, the technique reaches back
thousands of years.

Cross-dating, as the matching is called, is what makes the method rigorous. A
single trunk can mislead: a tree may miss a ring entirely in a year of drought,
or add a false one after an unseasonal frost. Those errors do not repeat across
a stand, so a chronology built from many trees corrects them. It also means
that a sample which cannot be cross-dated is discarded rather than estimated.

The technique has been borrowed well beyond climate science. Timber in a
building can be matched to a regional chronology and dated to a particular
year, sometimes to a particular season. The method has confirmed the age of
medieval roofs, exposed forged furniture and dated the wood of violins. It
cannot, however, date a tree that grew where seasons are weak: in much of the
tropics growth is continuous, rings are faint or absent, and the record the
method depends on was never written.


PASSAGE 3 — The limits of eyewitness memory

Courts have long treated an eyewitness as the strongest evidence available. A
confident witness who identifies a suspect is persuasive in a way that physical
evidence often is not, and juries weight that confidence heavily. Four decades
of laboratory work suggest the weighting is misplaced.

Memory is not a recording. What is retrieved is assembled, and the assembly
draws on everything learned since the event as well as the event itself.
Elizabeth Loftus demonstrated this in a series of studies in which participants
watched a staged collision and were then questioned about it. Those asked how
fast the cars were going when they smashed into each other gave higher speed
estimates than those asked about cars that hit each other, and a week later
were more likely to report broken glass that had never been shown. A single
verb had altered what they believed they had seen.

Identification parades compound the problem. A witness shown a line-up tends to
choose the person who most resembles their memory rather than deciding whether
the culprit is present at all. If the culprit is absent, the closest match is
chosen anyway. Confidence then grows after the fact: a witness told that they
picked the suspect becomes markedly more certain, and recalls having had a
better view than they originally reported.

Reform has been slow but real. Several jurisdictions now require that the
officer running a line-up does not know which member is the suspect, so that no
unconscious signal can be given. Witnesses are told explicitly that the culprit
may not be present. Confidence is recorded at the moment of identification,
before any feedback, because a confidence statement taken then does carry
information, while one taken at trial does not.

What reform has not achieved is a change in how juries respond. Mock-jury
studies find that instructions about the unreliability of eyewitness memory
have little effect on verdicts, and that an articulate, confident witness
remains convincing whatever the judge has said. The problem is not that jurors
lack the information. It is that confidence is read as a sign of accuracy, and
the two are only loosely related.''')

# (prompt, choices, accepted, evidence, explanation, skill_tag)
ITEMS = [
    # --- Passage 1: True / False / Not Given (1-6) ---
    ('Some cities that removed their tram systems have since built new ones.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['TRUE'],
     'several of them are the same cities that removed one',
     'Matnda aynan shu holat keltirilgan.', 'True / False / Not Given'),
    ('Bus lanes take longer to build than tram lines.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['FALSE'],
     'Bus lanes are far cheaper and can be installed in months rather than years.',
     'Aksincha — avtobus yo‘laklari tezroq quriladi.', 'True / False / Not Given'),
    ('The express bus corridor in Nantes raised property values.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['FALSE'],
     'an express bus corridor introduced in the same period produced no measurable effect',
     'Hech qanday ta’sir qayd etilmagan.', 'True / False / Not Given'),
    ('Grenoble admitted that its second line had been planned badly.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['FALSE'],
     'Operators responded by extending the line rather than admitting the error',
     'Xatoni tan olish o‘rniga liniya uzaytirilgan.', 'True / False / Not Given'),
    ('Trams carry more passengers per driver than buses.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['TRUE'],
     'a tram lasts forty years and carries more people per driver',
     'Himoyachilarning dalili sifatida keltirilgan.', 'True / False / Not Given'),
    ('Most tram lines operate at full capacity.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['FALSE'],
     'the saving assumes the line is full, and most are not',
     'Ko‘pchiligi to‘la emas deb aytilgan.', 'True / False / Not Given'),
    # --- Passage 1: short answer (7-10) ---
    ('How many cities have opened a tram or light-rail line since 1980, according to the passage? '
     'Write ONE word or a number.',
     [], ['two hundred', '200', 'more than two hundred'],
     'more than two hundred cities have opened a tram or light-rail line since 1980',
     'Son matndan to‘g‘ridan-to‘g‘ri olinadi.', 'Short answer'),
    ('Within how many metres of the Nantes line did property values rise fastest? Write a number.',
     [], ['300', 'three hundred'],
     'property values within three hundred metres of the first new line rose faster',
     'Masofa matnda aniq berilgan.', 'Short answer'),
    ('What quality do trams offer that buses do not? Write ONE word.',
     [], ['permanence'],
     'What trams offer that buses do not is permanence.',
     'Bitta so‘z bilan javob beriladi.', 'Short answer'),
    ('In the 2019 survey, how many French cities were studied? Write a number.',
     [], ['11', 'eleven'],
     'a 2019 survey of eleven French cities',
     'Son matnda keltirilgan.', 'Short answer'),
    # --- Passage 1: multiple choice (11-13) ---
    ('What does the writer suggest about the cost comparison between trams and buses?',
     ['Neither side accepts the other’s evidence.',
      'Trams have been proved cheaper over forty years.',
      'Buses are cheaper only in small cities.',
      'The comparison has now been settled by research.'],
     ['Neither side accepts the other’s evidence.'],
     'Neither side has produced a study that both accept.',
     'Muallif bahs hal bo‘lmaganini aytadi.', 'Multiple choice'),
    ('According to Passage 1, why is permanence a disadvantage?',
     ['A fixed line serves a city that may have changed.',
      'Rails wear out faster than road surfaces.',
      'Permanent lines attract fewer developers.',
      'Tram drivers cannot be retrained.'],
     ['A fixed line serves a city that may have changed.'],
     'A tram line fixed in concrete serves the city that existed when it was planned',
     'Grenoble misoli shu fikrni tasdiqlaydi.', 'Multiple choice'),
    ('What did officials most often give as a reason for building a tram network?',
     ['Image and regeneration', 'Journey times', 'Operating costs', 'Driver shortages'],
     ['Image and regeneration'],
     'named image and regeneration more often than journey times',
     'So‘rov natijasi matnda aniq.', 'Multiple choice'),

    # --- Passage 2: sentence completion (14-19) ---
    ('In temperate climates a trunk adds a pale band of fast ________ growth each year. Write ONE word.',
     [], ['spring'],
     'a trunk adds a pale band of fast spring growth',
     'Faslning nomi matndan olinadi.', 'Sentence completion'),
    ('The study of dating events using tree rings is called ________. Write ONE word.',
     [], ['dendrochronology'],
     'The discipline that does this is called dendrochronology',
     'Atama matnda berilgan.', 'Sentence completion'),
    ('Douglass was originally investigating a link between solar cycles and ________. Write ONE word.',
     [], ['rainfall'],
     'evidence that solar cycles influenced rainfall',
     'Dastlabki maqsad — yog‘ingarchilik bilan bog‘liqlik.', 'Sentence completion'),
    ('The matching of ring patterns between trees is known as ________. Write ONE or TWO words.',
     [], ['cross-dating', 'cross dating'],
     'Cross-dating, as the matching is called, is what makes the method rigorous.',
     'Usulning nomi matnda.', 'Sentence completion'),
    ('A tree may add a false ring after an unseasonal ________. Write ONE word.',
     [], ['frost'],
     'or add a false one after an unseasonal frost',
     'Sabab matnda aniq.', 'Sentence completion'),
    ('Samples that cannot be cross-dated are ________ rather than estimated. Write ONE word.',
     [], ['discarded'],
     'a sample which cannot be cross-dated is discarded rather than estimated',
     'Fe’l matndan aynan olinadi.', 'Sentence completion'),
    # --- Passage 2: True / False / Not Given (20-24) ---
    ('Douglass proved that sunspots control rainfall.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['FALSE'],
     'The trees did not settle the sunspot question',
     'Savol hal qilinmagan.', 'True / False / Not Given'),
    ('A single tree trunk can give a misleading record.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['TRUE'],
     'A single trunk can mislead',
     'Matnda to‘g‘ridan-to‘g‘ri aytilgan.', 'True / False / Not Given'),
    ('Dendrochronology has been used to detect forged furniture.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['TRUE'],
     'exposed forged furniture and dated the wood of violins',
     'Qo‘llanish sohalaridan biri.', 'True / False / Not Given'),
    ('The method is more accurate in tropical forests than in temperate ones.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['FALSE'],
     'in much of the tropics growth is continuous, rings are faint or absent',
     'Tropiklarda usul umuman ishlamaydi.', 'True / False / Not Given'),
    ('Dendrochronology is now taught in most universities.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['NOT GIVEN'],
     '',
     'Ta’lim haqida matnda hech narsa yo‘q.', 'True / False / Not Given'),
    # --- Passage 2: multiple choice (25-27) ---
    ('What makes a chronology built from many trees reliable?',
     ['Errors in one trunk are not repeated across a stand.',
      'Older trees are always more accurate.',
      'Rings are wider in large forests.',
      'Climate is identical across a region.'],
     ['Errors in one trunk are not repeated across a stand.'],
     'Those errors do not repeat across a stand, so a chronology built from many trees corrects them.',
     'Ko‘p namuna xatolarni to‘g‘rilaydi.', 'Multiple choice'),
    ('How far back can overlapping samples extend a chronology?',
     ['Thousands of years', 'About two centuries', 'Roughly forty years', 'One human lifetime'],
     ['Thousands of years'],
     'Repeated across overlapping samples, the technique reaches back thousands of years.',
     'Matnda aniq ko‘rsatilgan.', 'Multiple choice'),
    ('Timber in a building can sometimes be dated to a particular',
     ['season', 'decade', 'century', 'region only'],
     ['season'],
     'dated to a particular year, sometimes to a particular season',
     'Eng aniq daraja — fasl.', 'Multiple choice'),

    # --- Passage 3: True / False / Not Given (28-33) ---
    ('Juries give a confident eyewitness more weight than physical evidence.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['TRUE'],
     'A confident witness who identifies a suspect is persuasive in a way that physical evidence often is not',
     'Matnda aynan shunday aytilgan.', 'True / False / Not Given'),
    ('Loftus showed that the wording of a question can change what a witness reports.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['TRUE'],
     'A single verb had altered what they believed they had seen.',
     'Fe’l tanlovi javoblarni o‘zgartirgan.', 'True / False / Not Given'),
    ('Participants in the Loftus studies were shown broken glass.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['FALSE'],
     'were more likely to report broken glass that had never been shown',
     'Oyna ko‘rsatilmagan.', 'True / False / Not Given'),
    ('A witness will usually refuse to choose if the culprit is absent from a line-up.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['FALSE'],
     'If the culprit is absent, the closest match is chosen anyway.',
     'Aksincha — eng o‘xshashi tanlanadi.', 'True / False / Not Given'),
    ('Telling a witness that they picked the suspect increases their confidence.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['TRUE'],
     'a witness told that they picked the suspect becomes markedly more certain',
     'Qayta aloqa ishonchni oshiradi.', 'True / False / Not Given'),
    ('Most countries have now adopted the reforms described.',
     ['TRUE', 'FALSE', 'NOT GIVEN'], ['NOT GIVEN'],
     '',
     'Faqat «several jurisdictions» deyilgan, umumiy ulush aytilmagan.', 'True / False / Not Given'),
    # --- Passage 3: sentence completion (34-37) ---
    ('Memory is not a ________; what is retrieved is assembled. Write ONE word.',
     [], ['recording'],
     'Memory is not a recording.',
     'Metafora matndan olinadi.', 'Sentence completion'),
    ('In some jurisdictions the officer running a line-up does not know which member is the ________. '
     'Write ONE word.',
     [], ['suspect'],
     'the officer running a line-up does not know which member is the suspect',
     'Islohotning mazmuni.', 'Sentence completion'),
    ('Witnesses are now told that the culprit may not be ________. Write ONE word.',
     [], ['present'],
     'Witnesses are told explicitly that the culprit may not be present.',
     'Ogohlantirish matni.', 'Sentence completion'),
    ('Confidence is recorded before any ________ is given. Write ONE word.',
     [], ['feedback'],
     'Confidence is recorded at the moment of identification, before any feedback',
     'Qayta aloqadan oldin qayd etiladi.', 'Sentence completion'),
    # --- Passage 3: multiple choice (38-40) ---
    ('What do mock-jury studies suggest about judicial instructions?',
     ['They have little effect on verdicts.',
      'They make juries distrust all witnesses.',
      'They work only in serious cases.',
      'They increase the length of deliberation.'],
     ['They have little effect on verdicts.'],
     'instructions about the unreliability of eyewitness memory have little effect on verdicts',
     'Ko‘rsatmalar deyarli ta’sir qilmaydi.', 'Multiple choice'),
    ('According to the final paragraph, the central problem is that',
     ['confidence is treated as a sign of accuracy.',
      'jurors are not given enough information.',
      'judges misunderstand the research.',
      'witnesses deliberately exaggerate.'],
     ['confidence is treated as a sign of accuracy.'],
     'confidence is read as a sign of accuracy, and the two are only loosely related',
     'Oxirgi jumla xulosani beradi.', 'Multiple choice'),
    ('A confidence statement carries information when it is taken',
     ['at the moment of identification.',
      'at trial.',
      'after the officer confirms the choice.',
      'during cross-examination.'],
     ['at the moment of identification.'],
     'a confidence statement taken then does carry information, while one taken at trial does not',
     'Vaqt hal qiluvchi omil.', 'Multiple choice'),
]
