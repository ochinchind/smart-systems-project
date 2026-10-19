# Speaker notes — Smart Traffic Lights That Learn (midterm, 10 minutes)

Total: 1488 words ≈ 9.9 minutes at 150 words per minute (about one minute per slide).

## Slide 1 — Smart traffic lights that learn

*≈ 0:46 min (116 words)*

Good morning. We are Rakhimzhanov Amangeldy and Nurkin Aidar. Our project is called Smart Traffic Lights That Learn. It is a systematic literature review of reinforcement learning for traffic signal control, and the subtitle says what we care about most: the road from simulation to real streets. In a systematic review we do not run our own experiments. Instead, we collect, filter and analyse published research using a strict and reproducible method. In the next ten minutes we will explain the problem, our research questions, how we search and screen the literature, the main idea of our review, what we have already built, and finally why we consider the project to be about fifty percent complete.

## Slide 2 — Why traffic lights should learn

*≈ 1:00 min (149 words)*

Let us start with the problem. Most traffic lights in our cities still work on fixed timers. The green and red phases last the same time at three in the morning, when the road is empty, and at six in the evening, when it is jammed. Some lights react to a detector, but they still follow rules written by hand. A learning traffic light is different. It watches real traffic through cameras and road sensors and changes its timing on the fly, based on what it has learned works best. Research on this idea is booming, and hundreds of papers report shorter waiting times and shorter queues. But when we look closer, almost all of these results come from computer simulations. Peer-reviewed tests on real intersections are still very rare. Our review asks a simple question: why does this gap exist, and what would it take to close it?

## Slide 3 — A smart system in a loop

*≈ 1:00 min (151 words)*

Why is this a smart system? Because a learning traffic light closes the full smart-system loop, shown here in four steps. First, it senses: cameras and road sensors measure how many cars are waiting. Second, it decides: a reinforcement learning agent, usually a neural network, chooses which direction gets the next green phase. Third, it acts: the signal switches on the road. Fourth, it learns: after each decision it receives a reward, which is higher when people wait less, and step by step it improves its policy. This is reinforcement learning, learning by trial and error instead of following a hand-made timing plan. And this is exactly where the difficulty comes from. Trial and error is cheap and safe inside a simulator, where a bad decision costs nothing. At a real intersection, a bad decision means real people stuck in traffic, and possibly safety risks. That explains much of the gap.

## Slide 4 — Six research questions

*≈ 0:58 min (145 words)*

Our project proposal asked four questions. During planning we refined them into six, because a good systematic review only asks questions that can be answered from published papers. The table shows each question and the information we will extract to answer it. RQ1 looks at the landscape: how fast the field is growing, in which venues and in which countries. RQ2 looks at the methods: which algorithms are used, and how the state, action and reward are designed. RQ3 asks how the methods are validated: only in simulators, or also on real roads. RQ4 asks how much they actually improve waiting time, queues and travel time compared with baselines such as fixed-time plans. RQ5 collects the barriers that stop deployment, together with the fixes researchers propose. And RQ6 turns everything into gaps and future research directions. RQ3 and RQ4 are the heart of our review.

## Slide 5 — How we review: PRISMA 2020

*≈ 0:58 min (146 words)*

To answer these questions we follow PRISMA 2020, the international reporting standard for systematic reviews. It has six stages. First, plan: our protocol fixes the questions, the inclusion and exclusion criteria and the analysis before we search, so we cannot change the rules after seeing the results. Second, search: we search Scopus, Web of Science and IEEE Xplore for papers from 2019 to 2026. Third, screen: the two of us screen every record independently, first by title and abstract, then by full text, and we measure our agreement with Cohen's kappa. Every excluded paper gets one coded reason. Fourth, assess quality: each included study is scored on five criteria, zero to two points each, so ten points maximum. Fifth, extract: all data goes into one codebook, and every number is traced to its page or table. Sixth, synthesise the evidence and draw the PRISMA flow diagram.

## Slide 6 — Search strategy

*≈ 0:58 min (145 words)*

Here is how the search works. We split the topic into two concepts and combine them with AND. Concept A is the method: reinforcement learning, together with its common names, such as Q-learning, deep Q-network, actor-critic, policy gradient and PPO. Concept B is the application: traffic signals, together with traffic lights, signalized intersections, signal timing and signal phases. A paper must match both concepts to be found. We wrote the exact search string separately for each database, because Scopus, Web of Science and IEEE Xplore use different syntax. We limit the search to 2019 to 2026, to journal and conference papers, and to English. Before we lock the search, we run a pilot. We prepared a list of 20 papers we already know are relevant. The pilot must find most of them. If it misses some, we add the missing terms and document the change.

## Slide 7 — Our key idea: a validation realism scale

*≈ 1:01 min (153 words)*

This slide shows the main contribution of our review. Earlier reviews mostly ask which algorithm performs best. We also ask how realistically each method was tested. For this we defined a validation realism scale with six levels. Level zero is a purely synthetic simulation, an artificial grid with invented traffic. Level one uses a real road map but made-up traffic. Level two is a simulation driven by real traffic data. Level three puts real hardware, such as a real signal controller, in the loop, but the lights on the street are not controlled. Level four is a field test, where the agent actually switches the lights at a real intersection for a limited time. Level five is a sustained deployment in a city. Every study gets the highest level it reaches. Then we can compare the reported improvements level by level and see whether the gains shrink as the tests become more real.

## Slide 8 — What the scoping search already shows

*≈ 0:56 min (139 words)*

Before designing the formal search, we ran a short scoping search to understand the field. These are design inputs, not results of our review, and they are not counted in the PRISMA numbers. Four observations stood out. First, simulators dominate: recent reviews name SUMO and CityFlow as the main test platforms. Second, field tests are rare: papers from 2021 and 2022 that focus on deployment report that RL signal controllers have almost never run on live streets. Third, the last systematic review on this topic, by Noaeen and colleagues, covered 160 papers but only up to March 2020, so recent years have not been systematically reviewed. Fourth, many papers reuse the same few city datasets, such as Jinan, Hangzhou and New York. So we must be careful not to count the same evidence twice, and our method handles that.

## Slide 9 — What we have built so far

*≈ 0:54 min (135 words)*

So what have we actually produced so far? First, fifteen planning and method documents, covering all 27 steps of our review guideline, combined into one 32-page project dossier. Second, ready-to-run search strings for all three databases. Third, a codebook with 64 extraction fields, so that every study is described in exactly the same way. Fourth, a small software pipeline with ten commands. It imports the search results exported from the databases, removes duplicates, prepares the screening sheets for both reviewers, calculates our agreement, produces the quality and extraction sheets, and draws the PRISMA flow diagram. The key design rule is that every count and every statistic is computed from the records, never typed by hand. That makes our review reproducible and easy to audit. The pipeline has ten automated tests, and all of them pass.

## Slide 10 — Progress: about 50% complete

*≈ 1:24 min (209 words)*

Finally, the question we were asked: how complete is the project, and why do we say fifty percent? We divided the whole project into six phases and gave each a weight based on the effort it needs, adding up to one hundred points. We only count work that is actually finished. Phase one, planning and the protocol, is complete: 20 out of 20. Phase two, the search strategy: the concepts, databases and search strings are done; only the pilot run and the formal lock are left, so 13 out of 15. Phase three, the review tools for screening, quality scoring, extraction and synthesis, is built and tested: 15 out of 15. Phase four, running the searches and screening, is next, so zero. Phase five, quality assessment and extraction, has not started: zero. Phase six, synthesis and writing, has a draft taxonomy, worth 2 out of 15. Together that is 50 out of 100. Put simply, the design half of the review is complete: we know exactly what to search, how to judge each paper and how to analyse the results. The execution half starts now, with the pilot search and the locked protocol as our next milestone. Thank you for your attention. We are happy to answer your questions.
