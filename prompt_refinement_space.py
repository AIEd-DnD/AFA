import AFA_eval_functions as AFA
import resources as rsrc
import student_response_repo as SRR

subject = "English"
level = "Secondary 4"
question = " "
#question = "竞争往往会给人带来前进的动力，然而最近发生的一件事，却让你明白恶性竞争会带来不良的结果。试描述这件事，并谈谈你从中得到的启示。"
#recipe = rsrc.recipes["Direct Answer"]

rubrics="内容 - 5 - 内容不足，不切合题意。内容层次不清楚，没有条理或重复，甚至杂乱无章。, 内容 - 4 - 内容不太充实，不太切合题意。内容层次不太清楚，说明也不太详尽、不太有条理。, 内容 - 3 - 内容还算充实，还算切合题意。内容还算有层次，说明还算详尽、有条理。, 内容 - 2 - 内容相当充实，相当切合题意。内容相当有层次，说明相当详尽，也相当有条理。, 内容 - 1 - 内容充实，切合题意。内容有层次，说明详尽、有条理。, 语文与结构 - 5 - 语句不通顺，汉字的书写、词语、语法及标点符号的运用错误非常多。词汇贫乏，遣词造句错误多，表达不清楚。组织凌乱，没有衔接。, 语文与结构 - 4 - 语句不太通顺，汉字的书写、词语、及标点符号的运用错误多。词汇有限，句式简单，没有变化，表达不太清楚。组织不太得当，衔接不太紧凑，段落不太分明。, 语文与结构 - 3 - 语句还算通顺，汉字的书写、词语、语法及标点符号的运用有些错误。用词还算适当，句式简单，变化少，表达还算清楚。组织还算得当，衔接还算紧凑，段落还算分明。, 语文与结构 - 2 - 语句相当通顺，汉字的书写、词语、语法及标点符号的运用有一些小错误。用词适当，句式相当正确且有变化，表达相当清楚。组织相当得当，衔接相当紧凑，段落相当分明。, 语文与结构 - 1 - 语句通顺，汉字的书写、词语、语法及标点符号的运用绝大多数正确。如有错误，也是极小的。用词丰富适当，句式正确且多样化，表达清楚。组织得当，衔接紧凑，段落分明。"
rubrics_simple="内容 - 1 - 内容充实，切合题意。内容有层次，说明详尽、有条理。, 语文与结构 - 1 - 语句通顺，汉字的书写、词语、语法及标点符号的运用绝大多数正确。如有错误，也是极小的。用词丰富适当，句式正确且多样化，表达清楚。组织得当，衔接紧凑，段落分明。"

student_response = """
我一直认为竞争是非常重要的，它能让我们变得更，取得更好的成绩。最近，我遇到了一次竞赛，它让我意识到恶性竞争有时也能带来不好的后果。 
 
 
有一天，我们班举行了一场英语比赛，很多同学都很紧张，因为这次比赛很重要，能影响到我们的成绩。我的同学小华非常历害，他总是考试得第一，大家都觉得他是最聪明的。我也很想超越他，赢得第一名。 
 
 
我开始拼命的复习，做了很多试题，甚至放弃了和朋友们一起玩的时间。可是，复习的时候，我开始变得不耐烦，看到小华做的题目总是很轻松，我就觉得自己不如他。于是，我开始不喜欢和他一起讨论问题，觉得他总是能轻松答对那些我做错的题目。我们之间的关戏变得越来越冷淡，我甚至开始怀义他是不是有什么不正当的手段。 
 
 
终于，竞赛来了。我紧张得不得了，手心里全是汗。虽然我尽力发挥，但最终还是没能超越小华。我很失望，觉得自己付出的努力没有得到回报。我看到小华得了第一名，虽然他看起来很开心，但我心里有种不太舒服的感觉，因为我觉得自己和他竞争时太过用力，失去了很多友谊和快乐。 
 
 
从这件事中，我意识到虽然竞争可以让我们变得更好，但过度的竞争有时会让我们失去更多东西，比如朋友之间的信任和关戏。如果我们只想着急败别人，而忽视了与他人合作和互相帮助的意义，那么这种竞争就变得没有意义，反而会带来不好的后果。以后我会更加主重和同学们一起合作，而不是只故着抄越别人。 我一直认为竞争是非常重要的，它能让我们变得更，取得更好的成绩。最近，我遇到了一次竞赛，它让我意识到恶性竞争有时也能带来不好的后果。有一天，我们班举行了一场英语比赛，很多同学都很紧张，因为这次比赛很重要，能影响到我们的成绩。我的同学小华非常历害，他总是考试得第一，大家都觉得他是最聪明的。我也很想超越他，赢得第一名。我开始拼命的复习，做了很多试题，甚至放弃了和朋友们一起玩的时间。可是，复习的时候，我开始变得不耐烦，看到小华做的题目总是很轻松，我就觉得自己不如他。于是，我开始不喜欢和他一起讨论问题，觉得他总是能轻松答对那些我做错的题目。我们之间的关戏变得越来越冷淡，我甚至开始怀义他是不是有什么不正当的手段。终于，竞赛来了。我紧张得不得了，手心里全是汗。虽然我尽力发挥，但最终还是没能超越小华。我很失望，觉得自己付出的努力没有得到回报。我看到小华得了第一名，虽然他看起来很开心，但我心里有种不太舒服的感觉，因为我觉得自己和他竞争时太过用力，失去了很多友谊和快乐。从这件事中，我意识到虽然竞争可以让我们变得更好，但过度的竞争有时会让我们失去更多东西，比如朋友之间的信任和关戏。如果我们只想着急败别人，而忽视了与他人合作和互相帮助的意义，那么这种竞争就变得没有意义，反而会带来不好的后果。以后我会更加主重和同学们一起合作，而不是只故着抄越别人。" \
"""
el_response = """
Homework is something most students dread and claim to be a waste of time and hence, this brought about many contrasting views towards homework being a waste of time. while some people think that homework is a waste of time, I think that home work is actually useful for students. Therefore, I disagree that homework is a waste of time. Firstly, homework acts as a mini test or a revision of a topic you did. So although you might think that you learnt everything you need to learn in school, homework actually tests your application skills. In other words, homework test how you can use what you have learnt to answer questions. Therefore, homeworks can act as a mini test not only to test your knowledge of the topic, but also to test how you answer the topic. Secondly, especially for subjects like mathematics, homework can also act as a practice. Mathematics is a subject that many require practice as the more you practice, the more you get to familiarise the question types that might be tested for an exam. In addition, you do not have to mark your work yourself and if you are unsure of a question or got something wrong, the teacher would be able to go through the homework with the whole class. Thus, I think that homework can act as a practice for students. Lastly, I think that homework works as good revision notes to refer to for example, with the past worksheets or homework you did, you can take note of the questions you got incorrect and memorise the corrections or how to avoid that mistake. Therefore, worksheets can work as a helpful last-minute revision tool. In a nutshell, homework is a very useful learning tool that can play a part in how well you do in an exam. Although only doing homework is not enough to secure your results, I hope that people would start taking homework more seriously as it could play a huge role in you doing well for your examinations.
"""
EL_error_tags = """
Adjective - Incorrect or inappropriate use of adjectives, such as using the wrong form (comparative, superlative): Incorrect: "She is more prettier than her sister." Correct: "She is prettier than her sister.",

Adverb - Incorrect use of adverbs, such as using an adjective instead of an adverb: Incorrect: "He runs quick." Correct: "He runs quickly.",

Capitalisation/ case - Incorrect use of uppercase and lowercase letters, especially for proper nouns and sentence beginnings: Incorrect: "i went to paris last summer." Correct: "I went to Paris last summer.",

Collocation - Incorrect pairing of words that do not naturally go together in English: Incorrect: "She made a big effort." Correct: "She made a great effort.",

Conjunction - Incorrect use or omission of conjunctions to link sentences or clauses. Incorrect: "Although it was cold outside, but I still went for a walk." Correct: "Although it was cold outside, I still went for a walk.",

Contraction - Incorrect use or omission of contractions, leading to confusion: Incorrect: "Its raining today." Correct: "It’s raining today.",

Determiner - Incorrect use or omission of determiners, such as articles, quantifiers and possessive determiners (e.g., a, an, the, much, many, my, your). Incorrect: "I love the nature." Correct: "I love nature.",

Noun - Incorrect noun forms, including pluralisation or uncountable nouns: Incorrect: "I have many homeworks." Correct: "I have a lot of homework.",

Other - Miscellaneous errors that don’t fit other categories: Incorrect: "I enjoy to the fullest life." Correct: "I enjoy life to the fullest.",

Particle - Incorrect use of particles, especially in phrasal verbs. Incorrect: "Please fill the form before leaving." Correct: "Please fill out the form before leaving.",

Possessive - Incorrect use of possessive forms (’s or s’). Incorrect: "The dog wagged it's tail." Correct: "The dog wagged its tail.",

Preposition - Incorrect or missing prepositions, leading to grammatical errors: Incorrect: "She is good in math." Correct: "She is good at math.",

Pronoun - Incorrect pronoun usage, including unclear references or agreement issues. Incorrect: "Each student must bring their book." Correct: "Each student must bring his or her book.",

Punctuation - Incorrect or missing punctuation marks that change the meaning. Incorrect: "Let’s eat Grandma." Correct: "Let’s eat, Grandma.",

Sentence - Errors related to sentence structure, such as fragments or run-ons: Incorrect: "When I arrived. I saw him." Correct: "When I arrived, I saw him.",

Space - Missing or extra spaces between words or punctuation: Incorrect: "I went tothe park." Correct: "I went to the park.",

Spelling - Incorrect spelling of words, affecting comprehension: Incorrect: "She recieved a letter." Correct: "She received a letter.",

Verb - Incorrect verb tense, agreement, or form (including gerunds/infinitives). Incorrect: "I look forward to meet you." Correct: "I look forward to meeting you.",

Word choice - Using an incorrect or suboptimal word that does not fit the context. Incorrect: "He is a criminal who has alluded capture." Correct: "He is a criminal who has eluded capture.",

Word order - Incorrect word order, making sentences sound unnatural or confusing: Incorrect: "She always is late." Correct: "She is always late."
"""

system_msg = AFA.assemble_system_prompt(subject, level, question, error_tags=EL_error_tags)
user_msg = AFA.assemble_user_prompt(el_response)
response = AFA.get_annotations_system_user(system_msg, user_msg)
print(response)
print(" ")
if "</tag>" in response:
    print(True)
else:
    print(False)
#AFA.display_output(response)