import AFA_eval_functions as AFA

subject="English"
level="Primary 5"
question="Write about a time when you had to make up to a loved one."
students_response = """
Homework is something most students dread and claim to be a waste of time and hence, this brought about many contrasting views towards homework being a waste of time. while some people think that homework is a waste of time, I think that home work is actually useful for students. Therefore, I disagree that homework is a waste of time. Firstly, homework acts as a mini test or a revision of a topic you did. So although you might think that you learnt everything you need to learn in school, homework actually tests your application skills. In other words, homework test how you can use what you have learnt to answer questions. Therefore, homeworks can act as a mini test not only to test your knowledge of the topic, but also to test how you answer the topic. Secondly, especially for subjects like mathematics, homework can also act as a practice. Mathematics is a subject that many require practice as the more you practice, the more you get to familiarise the question types that might be tested for an exam. In addition, you do not have to mark your work yourself and if you are unsure of a question or got something wrong, the teacher would be able to go through the homework with the whole class. Thus, I think that homework can act as a practice for students. Lastly, I think that homework works as good revision notes to refer to for example, with the past worksheets or homework you did, you can take note of the questions you got incorrect and memorise the corrections or how to avoid that mistake. Therefore, worksheets can work as a helpful last-minute revision tool. In a nutshell, homework is a very useful learning tool that can play a part in how well you do in an exam. Although only doing homework is not enough to secure your results, I hope that people would start taking homework more seriously as it could play a huge role in you doing well for your examinations.
"""
error_tags = """
Adjective - Incorrect or inappropriate use of adjectives, such as using the wrong form (comparative, superlative).,

Adverb - Incorrect use of adverbs, such as using an adjective instead of an adverb.,

Capitalisation/case - Incorrect use of uppercase and lowercase letters, especially for proper nouns and sentence beginnings.,

Collocation - Incorrect pairing of words that do not naturally go together in English.,

Conjunction - Incorrect use or omission of conjunctions to link sentences or clauses.,

Contraction - Incorrect use or omission of contractions, leading to confusion.,

Determiner - Incorrect use or omission of determiners, such as articles, quantifiers and possessive determiners (e.g., a, an, the, much, many, my, your).,

Noun - Incorrect noun forms, including pluralisation or uncountable nouns.,

Other - Miscellaneous errors that don’t fit other categories.,

Particle - Incorrect use of particles, especially in phrasal verbs.,

Possessive - Incorrect use of possessive forms (’s or s’).,

Preposition - Incorrect or missing prepositions, leading to grammatical errors.,

Pronoun - Incorrect pronoun usage, including unclear references or agreement issues.,

Punctuation - Incorrect or missing punctuation marks that change the meaning.,

Sentence - Errors related to sentence structure, such as fragments or run-ons.,

Space - Missing or extra spaces between words or punctuation.,

Spelling - Incorrect spelling of words, affecting comprehension.,

Verb - Incorrect verb tense, agreement, or form (including gerunds/infinitives).,

Word choice - Using an incorrect or suboptimal word that does not fit the context.,

Word order - Incorrect word order, making sentences sound unnatural or confusing.
"""

user_prompt = AFA.assemble_prompt(subject, level, question, students_response, error_tags)
response = AFA.get_annotations(user_prompt)
dict_response = AFA.string_to_dict(response)
annotated_response = dict_response["annotated_response"]
print(annotated_response)
print(" ")
feedback_list = dict_response["feedback_list"]
print("There are {} annotations".format(len(feedback_list)))
for feedback in feedback_list:
    print(" ")
    print("Annotation: "+feedback["phrase"])
    print(" Error Tag: "+feedback["error_tag"][0]["errorType"])
    print("  Feedback: "+feedback["comment"])