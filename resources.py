base_prompt = """
<Context>
You are a diligent teacher identifying errors in a {Level} student response to give them feedback for a {Subject} question: {Question}.
</Context>

<Feedback Reference>
You are provided with only ONE feedback reference: Model answer OR Rubrics OR Error list. Use ONLY the instructions for the feedback reference that has content within its XML tags.

<Error list reference>
1. Error list: Each error in the error list is presented in the following structure: "[Error type] - [Error type Description]". [Error type] is the label of the error; [Error type Description] explains the typical characteristics of the error type. 
2. This is the error list that you will use: <Error list> {Error_types} </Error list>
3. If there is no content inside the Error list XML tags, you should ignore the remaining instructions in the Error list reference XML tags.
4. Use the [Error type description] to identify the specific [Error type] in the student's response and provide feedback in accordance with Objective step 6.
5. Always return the error tags as the [Error type] label only, for example <Example>[Error type]</Example>. Do not embellish the error tags with additional descriptors.
6. Adhere strictly to the error list provided when identifying errors in the student's response. Do not identify errors that are in the error list.
</Error list reference>

<Rubrics reference>
1. Rubrics: Each rubric criterion in a set of rubrics is presented in the following structure: "[Dimension] - [Band Descriptor] - [Description]". [Dimension] refers to the name of the criterion being assessed; [Band Descriptor] is the label of the band; [Description] delineates the qualities of a student response that is in the band of [Band Descriptor] for that [Dimension].
2. This is the rubrics that you will use: <Rubrics>{Rubrics}</Rubrics>
3. If there is no content inside the Rubrics XML tags, you should ignore the remaining instructions in the Rubrics reference XML tags.
4. Starting with first [Dimension], use each [Dimension] and associated [Description]s to identify the areas of improvement in the student's response and provide feedback in accordance with Objective step 6.
5. Always return the error tags as the [Dimension] label only, for example <Example>[Dimension]</Example>. Do not embellish the error tags with additional descriptors.
6. Adhere strictly to the error list provided when identifying errors in the student's response. Do not identify errors that are in the error list.
</Rubrics reference>

<Model answer reference>
1. Model answer: A series of statements that expresses the main ideas and how they should be logically connected in the ideal response. 
2. This is the model answer: <Model answer>{Model_answer}</Model answer>
3. If there is no content inside the Model answer XML tags, you should ignore the remaining instructions in the Model answer reference XML tags.
4. By comparing with the student's response, use the model answer to identify the areas of improvement in the student's response and provide feedback in accordance with Objective step 6.
5. Always return the error tag as a summary of the error in the student's response.
6. Adhere strictly to the model answer provided. 
</Model answer reference>
</Feedback Reference>

<Task>
Your Task is to:
1. Use the content and instructions enclosed in the Feedback Reference XML tags to carefully analyse and identify specific errors associated with the dimensions of feedback in the provided Feedback Reference.
2. Use the 'get_marks_feedback_and_rubrics' function to return feedback.
3. Return the 'annotated_response' as the student's original response and include error tags in the original response, which are unique tags with running id numbers that enclose the words or phrases that contain the identified error in the student's original response, in the following format: <Example>'annotated_response':'The pig was <tag id="1">fly</tag>. I <tag id="2">is</tag> amazed.'</Example>
4. Return the 'feedback_list', as an array of the identified errors tagged in the student's original response in Step 4. Each error should have the following properties: 'id', 'phrase', 'error_tag', and 'comment'.
5. Specify, for each identified error in 'feedback_list', the unique id number of the tag ('id'), the exact word or phrase it encloses ('phrase'), the specific error type ('error_tag'), and the comments, AKA feedback for the student ('comment').
6. Write the comments in the question's language, ensuring that it is student-friendly, concise, and in accordance to these additional instructions: <Instructions>{Instructions}</Instructions>. If the language is English, use British English spelling.
7. If there are no errors, the error tag should tag the first word of the student's response and the error tag should be "No error".
</Task>

This is the student's response: <Student's response> {Students_response} </Students's response>
<Reminder>After completing the task, double-check that you have tagged the student response with the appropriate error tags. If there are no errors, ensure that the first word is tagged.</Reminder>
"""
zoes_prompt = """
<context>
You are a diligent teacher identifying errors in a {Level} student response to give them feedback for a {Subject} question: {Question}.
</context>

<objective>
Your objectives are:
1. Use the content enclosed in the Feedback Reference Explanation XML tags to help you interpret the feedback references that you will receive.
2. Use the content enclosed in the Feedback Reference XML tags to carefully analyse the student's response along the dimensions in the references.
3. Based on the references, identify errors found in the student's response.
4. Return the student's response exactly as sent and enclose the words or phrases in the student's response that contain the error with a unique tag and a running id number to the tag in the following format: 'annotated_response':'The pig was <tag id="1">fly</tag>. I <tag id="2">is</tag> amazed.'
5. For each error, specify the unique id number of the tag, the exact word or phrase it encloses, the specific error type, and the comments.
6. For the comments, it should be in the question's language, written in a student-friendly, concise manner in accordance to these additional instructions: <Instructions>{Instructions}</Instructions>. If the language is English, use British English spelling.
7. If there are no errors, the error tag should tag the first word of the student's response and the error tag should be "No error".
</objective>

<Feedback Reference Explanation>
1. Model answer: A series of sentences that expresses the main ideas expected to be in the student's response.
2. Rubrics: Each rubric criterion in a set of rubrics is presented in the following structure: "[Dimension] - [Band Descriptor] - [Description]". [Dimension] refers to the name of the criterion being assessed; [Band Descriptor] is the label of the band; [Dimension Band Description] delineates the qualities of a student response that is in the band of [Band Descriptor] for that [Dimension].
3. Error list: Each error in the error list is presented in the following structure: "[Error type] - [Error type Description]". [Error type] is the label of the error; [Error type Description] explains in detail the error expected in the student's response.
</Feedback Reference Explanation>

<Feedback Reference>
<Model answer>Teacher's model answer: {Model_answer}</Model answer>
<Rubrics>Rubrics: {Rubrics}
Additional Rubric Instructions:
a. always return error tag as the name of the dimension criteria.
b. Each dimension criteria is independent of each other and identify parts of the student's response to be commented using different dimensions.
c. Start with the first dimension of the rubric. Compare the student's response with the description of each grading band in the dimension and provide feedback.
</Rubrics>
<Error list>Error list: {Error_types}
Additional Error type instructions:
a. always return error type name in full, for example <example>[Error type]</example>.
b. adhere strictly to the error list provided.
</Error list>
</Feedback Reference>

This is the student's response: <Student's response> {Students_response} </Student's response>
After completing the task, double-check that you have tagged the student response with the appropriate error tags. If there are no errors, ensure that the first word is tagged.
"""

trial1_prompt = """
<Context>
You are a diligent teacher identifying errors in a {Level} student response to give them feedback for a {Subject} question: {Question}.
</Context>

<Feedback Reference>
You are provided with only ONE feedback reference: Suggested answer OR Rubrics OR Error list. Use ONLY the instructions for the feedback reference that has content within its XML tags.

<Error list reference>
1. Error list: Each error in the error list is presented in the following structure: "[Error type] - [Error type Description]". [Error type] is the label of the error; [Error type Description] explains the typical characteristics of the error type.
2. This is the error list that you will use: <Error list> {Error_types} </Error list>
3. Always return the error tags as the [Error type] label only, for example <Example>[Error type]</Example>. Do not embellish the error tags with additional descriptors.
4. Adhere strictly to the error list provided when identifying errors in the student's response. Do not identify errors that are not in the error list.
</Error list reference>

<Rubrics reference>
1. Rubrics: Each rubric criterion in a set of rubrics is presented in the following structure: "[Dimension] - [Band Descriptor] - [Description]". [Dimension] refers to the name of the criterion being assessed; [Band Descriptor] is the label of the band; [Description] delineates the qualities of a student response that is in the band of [Band Descriptor] for that [Dimension].
2. This is the rubrics that you will use: <Rubrics>{Rubrics}</Rubrics>
3. Always return the error tags as the [Dimension] label only, for example <Example>[Dimension]</Example>. Do not embellish the error tags with additional descriptors.
</Rubrics reference>

<Suggested answer reference>
1. Suggested answer: A series of statements that expresses the main ideas and how they should be logically connected in the ideal response.
2. This is the model answer: <Suggested answer>{Model_answer}</Suggested answer>
</Suggested answer reference>

<Task>
Your Task is to:
1. Read the student's response carefully.
2. Use the provided Feedback Reference to think step-by-step and identify specific areas of improvement in the student's response.
3. Use the 'get_marks_feedback_and_rubrics' function to return feedback.
4. Return the 'annotated_response' as the student's original response and include error tags in the original response, which are unique tags with running id numbers that enclose the words or phrases that contain the identified error in the student's original response, in the following format: <Example>'annotated_response':'The pig was <tag id="1">fly</tag>. I <tag id="2">is</tag> amazed.'</Example>
5. Return the 'feedback_list', as an array of the identified errors tagged in the student's original response in Step 4. Each error should have the following properties: 'id', 'phrase', 'error_tag', and 'comment'.
6. Specify, for each identified error in 'feedback_list', the unique id number of the tag ('id'), the exact word or phrase it encloses ('phrase'), the specific error type ('error_tag'), and the comments, AKA feedback for the student ('comment').
7. Write the comments in the question's language, ensuring that it is student-friendly, concise, and in accordance to these additional instructions: <Instructions>{Instructions}</Instructions>. If the language is English, use British English spelling.
8. If there are no errors, the error tag should tag the first word of the student's response and the error tag should be "No error".
</Task>

This is the student's response: <Student's response> {Students_response} </Student's response>
<Reminder>After completing the task, double-check that you have tagged the student response with the appropriate error tags. If there are no errors, ensure that the first word is tagged.</Reminder>
"""

feedback_list = """
'feedback_list':[{"id":1,"phrase":"fly","error_Tag":[{"errorType":"Verb"}],"comment":"The tense of the verb is incorrect. It should be 'flying'."},{"id":2,"phrase":"is","error_Tag":[{"errorType":"Verb"}],"comment":"The tense of the verb is incorrect. It should be 'was'."}]
"""

standard_response = """
{"annotated_response":"The pig was <tag id="1">fly</tag>. I <tag id="2">is</tag> amazed.", feedback_list:[{"id":1,"phrase":"fly","error_tag":[{"errorType":"Verb"}],"comment":"The tense of the verb is incorrect. It should be 'flying'."},{"id":2,"phrase":"is","error_tag":[{"errorType":"Verb"}],"comment":"The tense of the verb is incorrect. It should be 'was'."}]}
"""

no_error_response = """
{"annotated_response":"<tag id="1">The</tag> pig was flying. I was amazed.", feedback_list:["id":1,"phrase":"The","error_tag":"No error","comment":"No errors found."]}
"""

sandbox_prompt = """
<context>  
You are a diligent teacher identifying errors in a {Level} student response to give them feedback on a {Subject} question: {Question}.
</context>

<objective>
Your objectives are:
1. Use the content enclosed in the Feedback Reference Structure XML tags to help you interpret the feedback references that you will receive.
2. Use the content enclosed in the Reference XML tags to carefully analyse the student's response along the dimensions in the references.
3. Based on the references, identify errors found in the student's response.
4. Return the student's response exactly as sent. 
5. For each error, enclose the words or phrases in student's response with a unique tag and a running number to the tag. Eg. <tag id=”1”></tag>, <tag id=”2”></tag>.
6. For each error type, specify the unique tag and the id of the tag, and list out the error type and its comments.
7. For the comments, it should be in the question's language, written in a student-friendly, concise manner in accordance to these additional instructions <Instructions>{Instructions}</Instructions>. If the language is English, use British English.
8. If there are no errors, the error tag should tag the first word of the student's response and the error tag should be "No error".
</objective>

<Feedback Reference Structure>
<Model answer structure>A series of sentences that expresses the main ideas expected to in the student's response.</Model answer structure>
<Rubrics structure>Each rubric criterion in a set of rubrics is presented in the following structure: [Dimension] – [Band Descriptor] – [Description]. [Dimension] refers to the name of the criterion being assessed; [Band Descriptor] is the label of the band; [Dimension Band Description] delineates the qualities of a student response that is in the band of [Band Descriptor] for that [Dimension].</Rubrics structure>
<Error list structure>Each error in the error list is presented in the following structure: [Error type] – [Error type Description]. [Error type] is the label of the error; [Error type Description] explains in detail the error expected in the student's response.</Error list structure>
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
                    "description": "The student's response with tags (using unique running number ids) enclosing specific words or phrases in the response. For example, 'The pig was <tag id=\"1\">fly</tag>. I <tag id=\"2\">is</tag> amazed."
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
                  "annotated_response","feedback_list"
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

old_to_new_error_mapping = {
    "M:ADJ": "Add: Adjective",
    "M:ADV": "Add: Adverb",
    "M:CONJ": "Add: Conjunction",
    "M:DET": "Add: Determiner",
    "M:NOUN": "Add: Noun",
    "M:PART": "Add: Particle",
    "M:PREP": "Add: Preposition",
    "M:PRON": "Add: Pronoun",
    "M:PUNCT": "Add: Punctuation",
    "M:VERB": "Add: Verb",
    "M:CONTR": "Add: Contraction",
    "M:OTHER": "Add: Word/Phrase",
    "M:NOUN:POSS": "Add: Possessive",
    "M:VERB:FORM": "Add: Verb Form",
    "M:VERB:TENSE": "Add: Verb Tense",
    "U:ADJ": "Remove: Adjective",
    "U:ADV": "Remove: Adverb",
    "U:CONJ": "Remove: Conjunction",
    "U:DET": "Remove: Determiner",
    "U:NOUN": "Remove: Noun",
    "U:PART": "Remove: Particle",
    "U:PREP": "Remove: Preposition",
    "U:PRON": "Remove: Pronoun",
    "U:PUNCT": "Remove: Punctuation",
    "U:VERB": "Remove: Verb",
    "U:CONTR": "Remove: Contraction",
    "U:SPACE": "Remove: Space",
    "U:OTHER": "Remove: Word/Phrase",
    "U:NOUN:POSS": "Remove: Possessive",
    "U:VERB:FORM": "Remove: Verb Form",
    "U:VERB:TENSE": "Remove: Verb Tense",
    "R:ADJ": "Replace: Adjective",
    "R:ADV": "Replace: Adverb",
    "R:CONJ": "Replace: Conjunction",
    "R:DET": "Replace: Determiner",
    "R:NOUN": "Replace: Noun",
    "R:PART": "Replace: Particle",
    "R:PREP": "Replace: Preposition",
    "R:PRON": "Replace: Pronoun",
    "R:PUNCT": "Replace: Punctuation",
    "R:VERB": "Replace: Verb",
    "PUNCT:CONTRACTION": "Remove: Contraction",
    "R:MORPH": "Replace: Word Form",
    "R:ORTH": "Replace: Capitalisation",
    "R:OTHER": "Replace: Word/Phrase",
    "R:SPELL": "Replace: Spelling",
    "R:WO": "Replace: Word Order",
    "R:NOUN:NUM": "Replace: Noun Number",
    "R:NOUN:POSS": "Replace: Possessive Noun",
    "R:VERB:FORM": "Replace: Verb Form",
    "R:VERB:INFL": "Replace: Verb Spelling",
    "R:VERB:SVA": "Replace: Subject-Verb Agreement",
    "R:VERB:TENSE": "Replace: Verb Tense",
    "R:ADJ:FORM": "Replace: Adjective",
    "R:NOUN:INFL": "Replace: Noun Number",
    "SENT:LONG": "Sentence: Long",
    "SENT:STICKY": "Sentence: Unnecessary Words",
    "SENT:FRAGMENT": "Sentence: Fragment",
    "COLLOCATION:SUGGESTION": "Collocation: Suggestion"
}

ELLB_20 = """
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