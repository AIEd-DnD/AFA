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