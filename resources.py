base_prompt = """
<context>
You are a diligent teacher identifying errors in a {Level} student response to give them feedback on a {Subject} question: {Question}.
</context>

<objective>
Your objectives are:
1. Use the content enclosed in the Feedback Reference Structure XML tags to help you interpret the feedback references that you will receive.
2. Use the content enclosed in the Reference XML tags to carefully analyse the student's response along the dimensions in the references.
3. Based on the references, identify errors found in the student response.
4. Return the student's response exactly as sent. 
5. For each error, enclose the words or phrases in student's response with a unique tag and a running number to the tag. Eg. <tag id=”1”></tag>, <tag id=”2”></tag>.
6. For each error type, specify the unique tag and the id of the tag, and list out the error type and its comments.
7. For the comments, it should be in the question's language, written in a student-friendly, concise manner in accordance to these additional instructions <Instructions>{Instructions}</Instructions>. If the language is English, use British English.
8. If there are no errors, the error tag should tag the first word of the student's response and the error tag should be "No error".
</objective>

<Feedback Reference Structure>
<Model answer structure>A series of sentences that expresses the main ideas expected to in the student's response.</Model answer structure>
<Rubrics structure>Each rubric criterion in a set of rubrics is presented in the following structure: [Dimension] - [Band Descriptor] - [Description]. [Dimension] refers to the name of the criterion being assessed; [Band Descriptor] is the label of the band; [Dimension Band Description] delineates the qualities of a student response that is in the band of [Band Descriptor] for that [Dimension].</Rubrics structure>
<Error list structure>Each error in the error list is presented in the following structure: [Error type] - [Error type Description]. [Error type] is the label of the error; [Error type Description] explains in detail the error expected in the student's response.</Error list structure>
</Feedback Reference Structure>

<reference>
<modelanswer>Teacher's model answer: {Model_answer}</modelanswer>
<rubrics>Rubrics: {Rubrics}
Additional Rubric Instructions: 
a. always return error tag as the name of the dimension criteria.
b. Each dimension criteria is independent of each other and identify parts of the student's response to be commented using different dimensions. 
c. Start with the first dimension of the rubric. Compare the student's response with the description of each grading band in the dimension and provide feedback. 
</rubrics>
<error list>Error list: {Error_types}
Additional Error type instructions:
a. always return error type name in full, for example <example>[Error type]</example>.
b. adhere strictly to the error list provided.
</error type>
</reference>

This is the student's response: {Students_response}

"""

recipes = {"Default":" ",
           "recipe 2":" ",
           "recipe 3":" ",
           "recipe 4":" ",
           "recipe 5":" ",
           "recipe 6":" ",
           "recipe 7":" ",
           "recipe 8":" ",
           "recipe 9":" "
           }

tools = [
  {
        "type": "function",
        "function": {
            "name": "get_marks_feedback_and_rubrics",
            "description": "Use the provided list of error tags, suggested answer or rubrics to carefully analyze the student's response and return feedback in a list format with the properties required in a JSON object",
            "parameters": {
                "type": "object",
                "properties": {
                  "annotated_response" : {
                    "type": "string",
                    "description": "student’s response and enclose the words or phrases and return with a unique tag and a running number to the tag."
                  },
                  "feedback_list": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "id": {
                          "type": "integer",
                          "description": "tag id"
                        },
                        "phrase": {
                          "type": "string",
                          "description": "the specific part of the sentence containing an error"
                        },
                        "error_tag": {
                          "type": "array",
                          "items": {
                            "type": "object",
                            "properties": {
                                "errorType": {
                                    "type": "string",
                                    "description": "error type"
                                }
                            }
                          },
                          "description": "list of concise error category based on error types"
                        },
                        "comment": {
                          "type": "string",
                          "description": "a concise student-friendly explanation or suggestion"
                        }
                      }
                    }
                  }
                },
                "required": [
                  "feedback_list"
                ]
            }
        }
      }
]

LangFA_errors = """
Add: Conjunction -  Omission of conjunctions to link sentences or clauses: Incorrect: "He didn't study he failed the exam." Correct: "He didn't study, so he failed the exam." (A conjunction is needed to show the cause-effect relationship), 

Add: Determiner - Omission of determiners, such as articles, quantifiers, and possessive determiners:Incorrect: "She bought apple and orange." Correct: "She bought an apple and an orange." (Articles "an" are needed for singular nouns), 

Add: Particle - Omission of particles, especially in phrasal verbs: Incorrect: "She looked up the dictionary." Correct: "She looked up the word in the dictionary." (The object placement in the phrasal verb is incorrect),

Add: Preposition - Omission of prepositions, leading to grammatical errors: Incorrect: "She is good math." Correct: "She is good at math." ("Good at" is the correct prepositional phrase in this context),

Add: Punctuation - Punctuation - Incorrect or missing punctuation marks that change the meaning: Incorrect: "Let's eat grandma." Correct: "Let's eat, grandma." (The comma clarifies that the speaker is addressing "grandma" rather than suggesting cannibalism)

Add: Contraction - Omission of contractions, leading to confusion: Incorrect: "Its raining today." Correct: "Its raining today." ("Its" is possessive, while "it's" is the contraction for "it is"),

Add: Possessive - Incorrect use of possessive forms ('s or s'): Incorrect: "The dogs bone was lost." Correct: "The dog's bone was lost." ("Dog's" shows possession correctly),

Remove: Conjunction - Incorrect use of conjunctions to link sentences or clauses: Incorrect: "Although it was cold outside, but I still went for a walk." Correct: "Although it was cold outside, I still went for a walk." ('Although' and 'but' are redundant together.),

Remove: Determiner - Incorrect use of determiners, such as articles, quantifiers, and possessive determiners: Incorrect: "I love the nature." Correct: "I love nature." ("Nature" is uncountable and does not typically take the definite article "the"),

Remove: Possessive - Incorrect use of possessive forms ('s or s'): Incorrect: "The dog wagged it's tail." Correct: "The dog wagged its tail." ("Its" is the possessive form, while "it's" is the contraction for "it is");

Remove: Space - Missing or extra spaces between words or punctuation: Incorrect: "I went tothe park." Correct: "I went to the park." (A missing space between "to" and "the"),

Replace: Adjective - Incorrect or inappropriate use of adjectives, such as using the wrong form (comparative, superlative): Incorrect: "She is more prettier than her sister." Correct: "She is prettier than her sister." ("More" is unnecessary because "prettier" is already in its comparative form); Incorrect: "He is a very sensible player." Correct: "He is a very sensitive player." ("Sensitive" is the appropriate term depending on context),

Replace: Adverb - Incorrect use of adverbs, such as using an adjective instead of an adverb: Incorrect: "He runs quick." Correct: "He runs quickly." ("Quick" is an adjective, but "quickly" is the correct adverb form to describe the verb "runs"),

Replace: Conjunction - Incorrect use of conjunctions to link sentences or clauses: Incorrect: "She is intelligent or beautiful." Correct: "She is intelligent and beautiful." ("Or" implies a choice, which isn't appropriate here),

Replace: Determiner - Incorrect use of determiners, such as articles, quantifiers, and possessive determiners: Incorrect: "I need few help with this problem." Correct: "I need a little help with this problem." ("A little" is the correct quantifier for uncountable nouns like "help");

Replace: Noun - Incorrect noun forms, including pluralization or uncountable nouns: Incorrect: "I have many homeworks." Correct: "I have a lot of homework." ("Homework" is uncountable and cannot take a plural form),

Replace: Particle - Incorrect use of particles, especially in phrasal verbs: Incorrect: "Nearly 50 percent of adults fall under this category." Correct: "Nearly 50 percent of adults fall into this category." ("Fall into" is the correct phrasal verb to describe categorization),

Replace: Preposition - Incorrect prepositions, leading to grammatical errors: Incorrect: "She is good in math." Correct: "She is good at math." ("Good at" is the correct prepositional phrase in this context),

Replace: Pronoun - Incorrect pronoun usage, including unclear references or agreement issues: Incorrect: "Each student must bring their book." Correct: "Each student must bring his or her book." ("His or her" agrees with the singular subject "student"),

Replace: Capitalisation - Incorrect use of uppercase and lowercase letters, especially for proper nouns and sentence beginnings: Incorrect: "i went to paris last summer." Correct: "I went to Paris last summer." (Proper nouns like "Paris" and sentence beginnings require capitalization),

Replace: Word/Phrase - Miscellaneous errors that don't fit other categories: Incorrect: "I enjoy to the fullest life." Correct: "I enjoy life to the fullest." (Reordering the sentence is necessary for natural phrasing),

Replace: Spelling - Incorrect spelling of words, affecting comprehension: Incorrect: "She recieved a letter." Correct: "She received a letter." ("Received" is the correct spelling),

Replace: Word Order - Incorrect word order, making sentences sound unnatural or confusing: Incorrect: "She always is late." Correct: "She is always late." ("Always" should come after the verb "is"),

Replace: Verb Form - Incorrect verb form (including gerunds/infinitives): Incorrect: "I look forward to meet you." Correct: "I look forward to meeting you." ("Meeting" is the correct gerund form after "look forward to"),

Replace: Subject-Verb Agreement - Incorrect verb agreement: Incorrect: "She have a car." Correct: "She has a car." ("Have" does not agree with the singular subject "She"),

Collocation: Suggestion - Incorrect pairing of words that do not naturally go together in English: Incorrect: "She made a big effort." Correct: "She made a great effort." ("Great" collocates naturally with "effort" in English)

Sentence: Fragment - Errors related to sentence structure, such as fragments or run-ons: Incorrect: "When I arrived. I saw him." Correct: "When I arrived, I saw him." (A dependent clause cannot stand alone as a sentence)

"""

biology_errors = """
Misconception of Process - Fundamental misunderstanding of the biological process (e.g., thinking photosynthesis occurs at night),  
Incomplete Explanation - Provides an incomplete or partial elaboration of a biological concept,  
Incorrect Sequence - Describes a biological process in the wrong order (e.g., incorrect stages of mitosis or meiosis),  
Lack of Specificity - Uses vague language or fails to specify key details (e.g., not mentioning ' active transport' when describing how ions move through membranes),  
Wrong Function - Assigns the wrong function to an organ, structure, or cell component (e.g., stating that the liver filters blood like the kidneys),  
Overgeneralization - Applies a concept too broadly (e.g., assuming all organisms undergo respiration the same way),  
Confusion Between Terms - Confuses two related but distinct biological terms (e.g., meiosis vs. mitosis, genotype vs. phenotype),  
Mislabeling - Mislabels a diagram, graph, or biological structure (e.g., labeling an artery as a vein in a circulatory system diagram),  
Wrong Unit of Measurement - Uses the wrong unit to express a biological quantity (e.g., using kilograms instead of grams for body mass),  
Misinterpretation of Graphs - Misreads or misinterprets data from a biological graph or chart (e.g., mixing up dependent and independent variables in experimental results),  
Incorrect Calculation - Makes an error in a biological calculation (e.g., calculating magnification incorrectly in microscopy),  
Incorrect Cause-Effect - Incorrectly explains the cause and effect in biological processes (e.g., stating that heart rate slows during exercise instead of increasing),  
Failure to Link Concepts - Fails to connect related concepts (e.g., not linking the role of enzymes to digestion in the stomach),  
Misunderstanding of Scale - Misunderstands biological scales (e.g., confusing cell sizes with organism sizes or misrepresenting the scale of ecosystems),  
Overcomplication - Provides an overly complex explanation where a simpler, more direct one is correct,  
Misidentification - Identifies the wrong species, tissue, or cell type in a question (e.g., confusing plant cells for animal cells in a diagram),  
Irrelevant Information - Includes irrelevant information that does not answer the question or address the biological concept,  
Incomplete Comparison - Makes an incomplete comparison between biological concepts (e.g., not fully explaining differences between aerobic and anaerobic respiration),  
Misuse of Terminology - Uses biological terminology incorrectly (e.g., using 'diffusion' instead of 'osmosis' in the context of water movement)
"""

full_59_error_sample = """
To build trust, belief, motivation and a plethora more of key traits, one must co-operate with others in order to make their life, at the very least, a little bit brighter. This is because when everyone is contributing, the net level of productivity rises and everyone becomes much efficient. However, I have only been in South East Asia, never once stepped out into Europe or East Asia. She did that in hope of him giving up his seat. In Singapore, shopping is not the only that brings visitors to Singapore. I took my small bag and put my towel and my water bottle. Before he could reply me, I froze. So he went to give the wallet. For example they would bring their own chips bought from the convenience store next to the school, or eat them after school. I sincerely hope that you will me the approval to proceed with the arrangement. I tried arguing with him, despite that it was of no use. I looked at my classmates faces and knew that they were as nervous as I was. It is when we re-visit the same topic that we become more familiar and experienced, allowing us remember the skills taught. What your home be like in the future? After showering and freshening ourselves up from being in the water the entire day, we finally decided to go grab a big meal. Although the book Auntie Snowdrop gave me was not very expensive, but to me, it is the most valuable gift and is priceless. More importantly, it is the peer support that would make learning in school enjoyable and less stressful. Different people have different ways of cooking up a dish. Dad then me passed me the box and asked me to open it. I was super unhealthy, until I joined Campus, thinking this was a waste of time. A recent development of technology is the growth using of big-data technologies. It's was a bright and sunny Saturday morning. I am going to the bungalow stay,  which has free recreation room usage and meals are provided. Moreover, you should avoid of the online jobs. Alex's went to town. One day during the school holidays, my brother and I were to told to clean the house. I had got a 100 on my paper! One would definitely want to buy the whole store. Henceforth, being cooperative enhances the chances of success. Imagine doing researches all by yourself, without any assistance nor different ideas. It was a early morning where most people will wake up. Going to collage is too expensive. After hearing what she said, I agreed on lend her. He walked in the shop. Them are friends. Hours flew by, It was time to go home as the clock chimed. I ran home as fast as I can. He said, "I cant expect you to pay." I’m your friend. He should not have been greedy and had those thought. i hope to hear from you soon! Teachers do everything they can to try and get everyone involved. My entire class suprised me with a birthday celebration. That should not be taken granted for. It would only depart in an hours time. Why did no one knows it was my birthday today? Problems will be overcomed more efficiently. John eat fish. In an environment with lesser tension, one would be able to work efficiently. All spectators burst into laughters. They went home, and they took care of the dogs, but they separated after having dinner together in the restaurant, and they have never seen each other since. She did all that was asked, then went away for a little while, but should come back with something new. Great idea. It is time to figure out why. There is ample evidence the region receives only an inch of rainfall every year. They need to contribute to the improvement of the area.
"""

full_59_error_LangFA_conversion = {'annotated_response': 'To build trust, belief, motivation and a plethora <tag id="1">more</tag> of<tag id="2"> </tag>key traits, one must co-operate with others in order to make their life, at the very least, a little <tag id="3">bit</tag> brighter. This is because when everyone is contributing, the net level of productivity rises and everyone becomes much<tag id="4"> </tag>efficient. However, I have only been in South East Asia,<tag id="5"> </tag>never once stepped out into Europe or East Asia. She did that in<tag id="6"> </tag>hope of him giving up his seat. In Singapore, shopping is not the only<tag id="7"> </tag>that brings visitors to Singapore. I took my small bag and put<tag id="8"> </tag>my towel and my water bottle. Before he could reply<tag id="9"> </tag>me, I froze. So he went to give<tag id="10"> </tag>the wallet. For example<tag id="11"> </tag>they would bring their own chips bought from the convenience store next to the school, or eat them after school. I sincerely hope that you will<tag id="12"> </tag>me the approval to proceed with the arrangement. I tried arguing with him, despite<tag id="13"> </tag>that it was of no use. I looked at my classmates<tag id="14"> </tag>faces and knew <tag id="15">that</tag> they were as nervous as I was. It is when we re-visit the same topic that we become more familiar and experienced, allowing us<tag id="16"> </tag>remember the skills taught. What<tag id="17"> </tag>your home be like in the future? After showering and freshening ourselves up from being in the water the entire day, we <tag id="18">finally</tag> decided to go grab a big meal. Although the book Auntie Snowdrop gave me was not very expensive, <tag id="19">but</tag> to me, it is the most valuable gift and is priceless. More importantly, it is <tag id="20">the</tag> peer support that would make learning in school enjoyable and less stressful. Different people have different ways of cooking <tag id="21">up</tag> a dish. Dad then <tag id="22">me</tag> passed me the box and asked me to open it. I was super unhealthy<tag id="23">,</tag> until I joined Campus, thinking this was a waste of time. A recent development of technology is the growth <tag id="24">using</tag> of big-data technologies. It<tag id="25">\'s</tag> was a bright and sunny Saturday morning. I am going to the bungalow stay, <tag id="26"> </tag>which has free recreation room usage and meals are provided. Moreover, you should avoid <tag id="27">of the</tag> online jobs. Alex<tag id="28">\'s</tag> went to town. One day during the school holidays, my brother and I were <tag id="29">to</tag> told to clean the house. I <tag id="30">had</tag> got a 100 on my paper! One would definitely want to buy the <tag id="31">whole</tag> store. <tag id="32">Henceforth</tag>, being cooperative enhances the chances of success. Imagine doing <tag id="33">researches</tag> all by yourself, without any assistance <tag id="34">nor</tag> different ideas. It was <tag id="35">a</tag> early morning where most people <tag id="36">will</tag> wake up. Going to <tag id="37">collage</tag> is too expensive. After hearing what she said, I agreed <tag id="38">on</tag> lend her. He walked <tag id="39">in</tag> the shop. <tag id="40">Them</tag> are friends. Hours flew by<tag id="41">,</tag> It was time to go home as the clock chimed. I ran home as fast as I <tag id="42">can</tag>. He said, "I ca<tag id="43">nt</tag> expect you to pay." <tag id="44">I’m</tag> your friend. He should not have been greedy and had those <tag id="45">thought</tag>. <tag id="46">i</tag> hope to hear from you soon! Teachers do everything they can to try <tag id="47">and</tag> get everyone involved. My entire class <tag id="48">suprised</tag> me with a birthday celebration. That should not be taken <tag id="49">granted for</tag>. It would only depart in an <tag id="50">hours</tag> time. Why did no one <tag id="51">knows</tag> it was my birthday today? Problems will be <tag id="52">overcomed</tag> more efficiently. John <tag id="53">eat</tag> fish. In an environment with <tag id="54">lesser</tag> tension, one would be able to work efficiently. All spectators burst into <tag id="55">laughters</tag>. <tag id="56">They went home, and they took care of the dogs, but they separated after having dinner together in the restaurant, and they have never seen each other since.</tag> <tag id="57">She did all that was asked, then went away for a little while, but should come back with something new.</tag> <tag id="58">Great idea.</tag> It is time to figure out why. There is ample evidence the region receives only an inch of rainfall every year. They need to <tag id="59">contribute to the improvement</tag> of the area.',
                                   'feedback_list': [{'id': 1, 'phrase': 'more', 'error_tag': [{'errorType': 'Remove: Adjective'}], 'comment': 'Consider removing the highlighted adjective., '}, {'id': 2, 'phrase': '', 'error_tag': [{'errorType': 'Add: Adjective'}], 'comment': 'Consider adding an adjective. Suggestion(s):,  other '}, {'id': 3, 'phrase': 'bit', 'error_tag': [{'errorType': 'Remove: Noun'}], 'comment': 'Consider removing the highlighted noun., '}, {'id': 4, 'phrase': '', 'error_tag': [{'errorType': 'Add: Adverb'}], 'comment': 'Consider adding an adverb. Suggestion(s):,  more '}, {'id': 5, 'phrase': '', 'error_tag': [{'errorType': 'Add: Conjunction'}], 'comment': 'Consider adding a conjunction. Suggestion(s):,  and '}, {'id': 6, 'phrase': '', 'error_tag': [{'errorType': 'Add: Determiner'}], 'comment': 'Consider adding a determiner. Suggestion(s):,  the '}, {'id': 7, 'phrase': '', 'error_tag': [{'errorType': 'Add: Noun'}], 'comment': 'Consider adding a noun. Suggestion(s):,  thing '}, {'id': 8, 'phrase': '', 'error_tag': [{'errorType': 'Add: Particle'}], 'comment': 'Consider adding a particle. Suggestion(s):,  on '}, {'id': 9, 'phrase': '', 'error_tag': [{'errorType': 'Add: Preposition'}], 'comment': 'Consider adding a preposition. Suggestion(s):,  to '}, {'id': 10, 'phrase': '', 'error_tag': [{'errorType': 'Add: Pronoun'}], 'comment': 'Consider adding a pronoun. Suggestion(s):,  him '}, {'id': 11, 'phrase': '', 'error_tag': [{'errorType': 'Add: Punctuation'}], 'comment': 'Consider adding a punctuation mark. Suggestion(s):, ,'}, {'id': 12, 'phrase': '', 'error_tag': [{'errorType': 'Add: Verb'}], 'comment': 'Consider adding a verb. Suggestion(s):,  give '}, {'id': 13, 'phrase': '', 'error_tag': [{'errorType': 'Add: Word/Phrase'}], 'comment': 'Consider if something is missing here. Suggestion(s):, the fact'}, {'id': 14, 'phrase': '', 'error_tag': [{'errorType': 'Add: Possessive'}], 'comment': "Consider adding a possessive. Suggestion(s):, '"}, {'id': 15, 'phrase': 'that', 'error_tag': [{'errorType': 'Remove: Preposition'}], 'comment': 'Consider removing the highlighted preposition., '}, {'id': 16, 'phrase': '', 'error_tag': [{'errorType': 'Add: Verb Form'}], 'comment': 'Consider adding word(s) to the verb phrase. Suggestion(s):,  to '}, {'id': 17, 'phrase': '', 'error_tag': [{'errorType': 'Add: Verb Tense'}], 'comment': 'Consider adding word(s) to change the tense of this verb. Suggestion(s):,  will '}, {'id': 18, 'phrase': 'finally', 'error_tag': [{'errorType': 'Remove: Adverb'}], 'comment': 'Consider removing the highlighted adverb., '}, {'id': 19, 'phrase': 'but', 'error_tag': [{'errorType': 'Remove: Conjunction'}], 'comment': 'Consider removing the highlighted conjunction., '}, {'id': 20, 'phrase': 'the', 'error_tag': [{'errorType': 'Remove: Determiner'}], 'comment': 'Consider removing the highlighted determiner., '}, {'id': 21, 'phrase': 'up', 'error_tag': [{'errorType': 'Remove: Particle'}], 'comment': 'Consider removing the highlighted particle., '}, {'id': 22, 'phrase': 'me', 'error_tag': [{'errorType': 'Remove: Pronoun'}], 'comment': 'Consider removing the highlighted pronoun., '}, {'id': 23, 'phrase': ',', 'error_tag': [{'errorType': 'Remove: Punctuation'}], 'comment': 'Consider removing the highlighted punctuation mark., '}, {'id': 24, 'phrase': 'using', 'error_tag': [{'errorType': 'Remove: Verb'}], 'comment': 'Consider removing the highlighted verb., '}, {'id': 25, 'phrase': "'s", 'error_tag': [{'errorType': 'Remove: Contraction'}], 'comment': 'Consider removing the highlighted contraction., '}, {'id': 26, 'phrase': ' ', 'error_tag': [{'errorType': 'Remove: Space'}], 'comment': 'Consider removing the highlighted space., '}, {'id': 27, 'phrase': 'of the', 'error_tag': [{'errorType': 'Remove: Word/Phrase'}], 'comment': 'Consider removing the highlighted word/phrase., '}, {'id': 28, 'phrase': "'s", 'error_tag': [{'errorType': 'Remove: Possessive'}], 'comment': 'Consider removing the highlighted possessive., '}, {'id': 29, 'phrase': 'to', 'error_tag': [{'errorType': 'Remove: Verb Form'}], 'comment': 'Consider removing the highlighted word(s) from the verb phrase., '}, {'id': 30, 'phrase': 'had', 'error_tag': [{'errorType': 'Remove: Verb Tense'}], 'comment': 'Consider removing the highlighted word(s) to change the verb tense., '}, {'id': 31, 'phrase': 'whole', 'error_tag': [{'errorType': 'Replace: Adjective'}], 'comment': 'Consider changing the highlighted adjective. Suggestion(s):, entire'}, {'id': 32, 'phrase': 'Henceforth', 'error_tag': [{'errorType': 'Replace: Adverb'}], 'comment': 'Consider changing the highlighted adverb. Suggestion(s):, Therefore'}, {'id': 33, 'phrase': 'researches', 'error_tag': [{'errorType': 'Replace: Noun Number'}], 'comment': 'Consider if the highlighted noun should be singular or plural. Suggestion(s):, research'}, {'id': 34, 'phrase': 'nor', 'error_tag': [{'errorType': 'Replace: Conjunction'}], 'comment': 'Consider changing the highlighted conjunction. Suggestion(s):, or'}, {'id': 35, 'phrase': 'a', 'error_tag': [{'errorType': 'Replace: Determiner'}], 'comment': 'Consider changing the highlighted determiner. Suggestion(s):, an'}, {'id': 36, 'phrase': 'will', 'error_tag': [{'errorType': 'Replace: Verb Tense'}], 'comment': 'Consider changing the tense of the highlighted verb. Suggestion(s):, would'}, {'id': 37, 'phrase': 'collage', 'error_tag': [{'errorType': 'Replace: Noun'}], 'comment': 'Consider changing the highlighted noun. Suggestion(s):, college'}, {'id': 38, 'phrase': 'on', 'error_tag': [{'errorType': 'Replace: Particle'}], 'comment': 'Consider changing the highlighted particle. Suggestion(s):, to'}, {'id': 39, 'phrase': 'in', 'error_tag': [{'errorType': 'Replace: Preposition'}], 'comment': 'Consider changing the highlighted preposition. Suggestion(s):, into'}, {'id': 40, 'phrase': 'Them', 'error_tag': [{'errorType': 'Replace: Pronoun'}], 'comment': 'Consider changing the highlighted pronoun. Suggestion(s):, They'}, {'id': 41, 'phrase': ',', 'error_tag': [{'errorType': 'Replace: Punctuation'}], 'comment': 'Consider changing the highlighted punctuation mark. Suggestion(s):, .'}, {'id': 42, 'phrase': 'can', 'error_tag': [{'errorType': 'Replace: Verb'}], 'comment': 'Consider changing the highlighted verb. Suggestion(s):, could'}, {'id': 43, 'phrase': 'nt', 'error_tag': [{'errorType': 'Add: Contraction'}], 'comment': "Consider if a contraction should be used here. Suggestion(s):, n't"}, {'id': 44, 'phrase': 'Iâ€™m', 'error_tag': [{'errorType': 'Remove: Contraction'}], 'comment': 'Consider removing the highlighted contraction if not in quotes.'}, {'id': 45, 'phrase': 'thought', 'error_tag': [{'errorType': 'Replace: Word Form'}], 'comment': 'Consider changing the form of the highlighted word. Suggestion(s):, thoughts'}, {'id': 46, 'phrase': 'i', 'error_tag': [{'errorType': 'Replace: Capitalisation'}], 'comment': 'Consider changing the capitalisation of the highlighted word. Suggestion(s):, I'}, {'id': 47, 'phrase': 'and', 'error_tag': [{'errorType': 'Replace: Word/Phrase'}], 'comment': 'Consider changing the highlighted word/phrase. Suggestion(s):, to'}, {'id': 48, 'phrase': 'suprised', 'error_tag': [{'errorType': 'Replace: Spelling'}], 'comment': 'Consider if the spelling of the highlighted word is accurate. Suggestions:, surprised'}, {'id': 49, 'phrase': 'granted for', 'error_tag': [{'errorType': 'Replace: Word Order'}], 'comment':'Consider changing the order of the highlighted words. Suggestion(s):, for granted'}, {'id': 50, 'phrase': 'hours', 'error_tag': [{'errorType': 'Replace: Possessive Noun'}], 'comment': "Consider if the highlighted noun should be in possessive form. Suggestion(s):, hour's"}, {'id': 51, 'phrase': 'knows', 'error_tag': [{'errorType': 'Replace: Verb Form'}], 'comment': 'Consider changing the form of the highlighted verb. Suggestion(s):, know'}, {'id': 52, 'phrase': 'overcomed', 'error_tag': [{'errorType': 'Replace: Verb Spelling'}], 'comment': 'Consider if the spelling of the highlighted verb is accurate. Suggestion(s):, overcome'}, {'id': 53, 'phrase': 'eat', 'error_tag': [{'errorType': 'Replace: Subject-Verb Agreement'}], 'comment': 'Consider if the highlighted verb agrees with the subject. Suggestion(s):, eats'}, {'id': 54, 'phrase': 'lesser', 'error_tag': [{'errorType': 'Replace: Adjective'}], 'comment': 'Consider changing the form of the highlighted adjective. Suggestion(s):, less'}, {'id': 55, 'phrase': 'laughters', 'error_tag': [{'errorType': 'Replace: Noun Number'}], 'comment': 'Consider if the highlighted noun is uncountable. Suggestion(s):, laughter'}, {'id': 56, 'phrase': 'They went home, and they took care of the dogs, but they separated after having dinner together in the restaurant, and they have never seen each other since.', 'error_tag': [{'errorType': 'Sentence: Long'}], 'comment': 'Consider if the highlighted sentence should be shortened.'}, {'id': 57, 'phrase': 'She did all that was asked, then went away for a little while, but should come back with something new.', 'error_tag': [{'errorType': 'Sentence: Unnecessary Words'}], 'comment': 'Consider removing unnecessary words in the highlighted sentence. Suggestion(s):, a, all, asked, away, but, come, did, for, little, new, should, that, then, was, went, with'}, {'id': 58, 'phrase': 'Great idea.', 'error_tag': [{'errorType': 'Sentence: Fragment'}], 'comment': 'Consider if the highlighted sentence is a complete sentence.'}, {'id': 59, 'phrase': 'contribute to the improvement', 'error_tag': [{'errorType': 'Collocation: Suggestion'}], 'comment': 'Consider replacing the highlighted phrase. Suggestion(s):, contribute to the development'}]}


full_59_error_AFA_returns = [{'annotation': 'efficient', 'error_tag': 'Replace: Adverb'}, 
                       {'annotation': 'that', 'error_tag': 'Remove: Word/Phrase'}, 
                       {'annotation': 'reply', 'error_tag': 'Replace: Preposition'}, 
                       {'annotation': 'me', 'error_tag': 'Add: Word/Phrase'}, 
                       {'annotation': 'classmates', 'error_tag': 'Add: Possessive'}, 
                       {'annotation': 'remember', 'error_tag': 'Add: Particle'}, 
                       {'annotation': 'be', 'error_tag': 'Add: Word/Phrase'}, 
                       {'annotation': 'but', 'error_tag': 'Remove: Conjunction'}, 
                       {'annotation': 'using', 'error_tag': 'Replace: Preposition'}, 
                       {'annotation': "It's", 'error_tag': 'Replace: Contraction'}, 
                       {'annotation': 'of', 'error_tag': 'Remove: Preposition'}, 
                       {'annotation': 'researches', 'error_tag': 'Replace: Noun'}, 
                       {'annotation': 'a', 'error_tag': 'Replace: Determiner'}, 
                       {'annotation': 'collage', 'error_tag': 'Replace: Spelling'}, 
                       {'annotation': 'lend', 'error_tag': 'Replace: Verb Form'}, 
                       {'annotation': 'Them', 'error_tag': 'Replace: Pronoun'}, 
                       {'annotation': 'It', 'error_tag': 'Replace: Capitalisation'}, 
                       {'annotation': 'can', 'error_tag': 'Replace: Verb Form'}, 
                       {'annotation': 'cant', 'error_tag': 'Replace: Spelling'}, 
                       {'annotation': 'I’m', 'error_tag': 'Replace: Capitalisation'}, 
                       {'annotation': 'thought', 'error_tag': 'Replace: Noun'}, 
                       {'annotation': 'i', 'error_tag': 'Replace: Capitalisation'}, 
                       {'annotation': 'suprised', 'error_tag': 'Replace: Spelling'}, 
                       {'annotation': 'granted', 'error_tag': 'Add: Word/Phrase'}, 
                       {'annotation': 'hours', 'error_tag': 'Add: Word/Phrase'}, 
                       {'annotation': 'knows', 'error_tag': 'Replace: Verb Form'}, 
                       {'annotation': 'overcomed', 'error_tag': 'Replace: Verb Form'}, 
                       {'annotation': 'eat', 'error_tag': 'Replace: Verb Form'}, 
                       {'annotation': 'lesser', 'error_tag': 'Replace: Adjective'}, 
                       {'annotation': 'laughters', 'error_tag': 'Replace: Noun'}]

sec_sample_m1 = """
Homework is something most students dread and claim to be a waste of time and hence, this brought about many contrasting views towards homework being a waste of time. while some people think that homework is a waste of time, I think that home work is actually useful for students. Therefore, I disagree that homework is a waste of time.

Firstly, homework acts as a mini test or a revision of a topic you did. So although you might think that you learnt everything you need to learn in school, homework actually tests your  application skills. In other words, homework test how you can use what you have learnt to answer questions. Therefore, homeworks can act as a mini test not only to test your knowledge of the topic, but also to test how you answer the topic.  

Secondly, especially for subjects like mathematics, homework can also act as a practice . Mathematics is a subject that many require practice as the more you practice, the more you get to familiarise the question types that might be tested for an exam. In addition, you do not have to mark your  work yourself and if you are unsure of a question or got something wrong , the teacher would be able to go through the homework with the whole class. Thus, I think that homework can act as a practice for students.

Lastly, I think that homework works as good revision notes to refer to for example, with the past worksheets or homework you did, you can take note of the questions you got incorrect and memorise the corrections or how to avoid that mistake. Therefore, worksheets can work as a helpful last-minute revision tool.  

In a nutshell, homework is a very useful learning tool that can play a part in how well you do in an exam. Although only doing homework is not enough to secure your results, I hope that people would start taking homework more seriously as it could play a huge role in you doing well for your examinations.
"""

sec_sample_m1_annotations = """
"Keep calm and love homework."-Anonymous. Homework is an essential tool in our lives, and many people get pressured and stressed by the overload of homework that they receive from their teachers <tag id = "1">over days</tags><tag id = "2"> </tag>some even going to the extent of crying. Homework was invented in 1905 by Robert Nevilin and is still very much present in today's modern schools. In my opinion, homework can be very useful to us and I do not agree with this statement. Many people complain that homework is useless. 

To begin with, homework is useful as it helps students learn to manage their time properly. Homework allows students to plan their time, so that they have sufficient time to study, do their homework, and also for leisure. The students will be able to learn how to put their homework as their first priority so that in the future, when they are working, they will be efficient and fast. However, there are also downsides to having homework. One may feel too stressed from <tag id = "3">keeping up deadlines</tag> and may not be able to cope with the enormous stress that they gain from it. 

Furthermore, homework can also help to improve one's grades<tag id = "4">,</tag> it can motivate students to continue studying and may even teach them a thing or two. In 2020, <tag id = "5">a research</tag> was conducted by Oxford University. They found out that 95% of students who consistently do their homework, do extraordinarily well in grades compared to students who are lazy and refuse to do their homework. In addition, homework <tag id = "6">also is</tag> a good way <tag id = "7">for revision</tag>. You can refer to it anytime you want <tag id = "8">one</tag> it has been marked and if there is any <tag id = "9">questions</tag> that needs to be clarified or<tag id = "10">,</tag> one may get wrong<tag id = "11"> </tag>they can always ask the teacher how to solve the problem. <tag id = "12">Whatever</tag> homework<tag id = "13"> </tag>students may not be able to do well in their studies and might not be motivated for school. 

Finally, homework is not a waste of time as without homework, many people will not be able to check if they are doing well in their studies or not. Homework helps to improve one's knowledge on the topic that they are doing and allows one to get better at it. If they are getting all the questions in the homework wrong, they will know which areas require <tag id = "14">improvements</tag>. <tag id = "15">From</tag> doing this, their grades will also improve and the students will be scoring higher marks <tag id = "15">compared to the homework as did not exist</tag>. Many people make the argument that people will have to sleep late if there is homework. However, if one has enough discipline and integrity, <tag id = "16">they</tag> will be able to finish <tag id = "17">their</tag> homework <tag id = "18">in</tag> time and be able to sleep early. 

In conclusion, homework is not a waste of time<tag id = "19"> </tag>and it is very essential and useful in a student's life. Without it, many students may not be able to cope with their studies and eventually, their grades will <tag id = "20">dwindle</tag>.
"""