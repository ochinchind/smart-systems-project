# Speaker notes — Smart Traffic Lights That Learn (midterm, 5 minutes)

Total: 731 words ≈ 4.9 minutes at 150 words per minute.

## Slide 1 — Smart traffic lights that learn

*≈ 23 seconds (57 words)*

Hello, we are Amangeldy and Aidar. Our project is a systematic literature review on traffic lights that learn by themselves using reinforcement learning. In the next five minutes we will show the problem, our research questions, how we run the review, what we have already built, and why we say the project is about fifty percent complete.

## Slide 2 — Why traffic lights should learn

*≈ 33 seconds (83 words)*

Most traffic lights in our cities still run on fixed timers. The green phase lasts the same time at three in the morning and in rush hour. A learning traffic light is different: it watches real traffic through cameras and road sensors and adapts its timing. Research on this is booming, and many papers show shorter waiting times, but almost all of those results come from computer simulations. Real field tests are very rare. Understanding that gap is the core of our project.

## Slide 3 — A smart system in a loop

*≈ 28 seconds (71 words)*

Why is this a smart system? Because it closes the full loop. It senses traffic with cameras and detectors, decides with an AI model, acts by switching the lights, and learns from a reward: the less people wait, the higher the reward. This is reinforcement learning, which learns by trial and error. That is also the catch: trial and error is cheap in a simulator but risky at a real intersection.

## Slide 4 — Six research questions

*≈ 25 seconds (62 words)*

Our proposal had four questions. We refined them into six that can actually be answered from published papers. Each one is linked to fields we will extract from every study. The two most important are RQ3, how realistically a method was tested, and RQ4, how much it really improves traffic. RQ5 and RQ6 turn the evidence into barriers and a research agenda.

## Slide 5 — How we review: PRISMA 2020

*≈ 30 seconds (75 words)*

We follow PRISMA 2020, the standard for systematic reviews. First we fixed a protocol, so the rules cannot change after we see the results. Then we search three databases, and two reviewers screen every paper independently, first by title and abstract, then by full text. Each included study gets a quality score out of ten. Data goes into one codebook, and every number is traced to its page or table. Finally we synthesise the evidence.

## Slide 6 — Search strategy

*≈ 29 seconds (72 words)*

Our search combines two concepts with AND: reinforcement learning, with all its common names, and traffic signals. We wrote the exact search strings for Scopus, Web of Science and IEEE Xplore, for papers from 2019 to 2026, journal and conference papers in English. Before we lock the search, we pilot it: it must find most of 20 papers we already know are relevant. If it misses some, we add the missing terms.

## Slide 7 — Our key idea: a validation realism scale

*≈ 31 seconds (77 words)*

This is our main contribution. Earlier reviews ask which algorithm is best. We also ask how realistically each method was tested. We code every study on a six-level scale: from a purely synthetic simulation at level zero, through simulations with real traffic data and real hardware, up to a field test and a sustained deployment in a city. Then we can compare the reported improvements level by level and see whether the gains survive contact with reality.

## Slide 8 — What the scoping search already shows

*≈ 26 seconds (66 words)*

Before designing the search, we ran a scoping search. Four things stood out. Simulators like SUMO and CityFlow dominate. Papers that focus on deployment say almost no RL signals run on live streets. The last systematic review stops in 2020. And many papers reuse the same few city datasets, so we must avoid counting the same evidence twice. These are design inputs, not our final results.

## Slide 9 — What we have built so far

*≈ 24 seconds (59 words)*

Here is what exists today. Fifteen planning and method documents, combined into one 32-page dossier. Search strings for all three databases, ready to run. A codebook with 64 extraction fields. And a small software pipeline with ten commands that imports database exports, removes duplicates, manages screening, and draws the PRISMA diagram directly from our records. Its tests all pass.

## Slide 10 — Progress: about 50% complete

*≈ 44 seconds (109 words)*

So how complete are we? We weighted the project by effort into six phases. Planning and the protocol are finished: 20 of 20 points. The search strategy is written for all three databases; only the pilot run and the formal lock are left, so 13 of 15. The tools for screening, quality scoring, extraction and synthesis are built and tested: 15 of 15. Synthesis has a draft taxonomy, worth 2 points. Searching, screening, extraction and writing have not started yet. That gives 50 out of 100. In other words, the design half of the review is complete, and the execution half starts now with the database searches. Thank you.
