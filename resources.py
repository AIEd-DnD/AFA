normans_prompt = """
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
lean_prompt = """
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
prod_prompt = """
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

system_prompt = """
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

After completing the task, double-check that you have tagged the student response with the appropriate error tags. If there are no errors, ensure that the first word is tagged.
"""
user_prompt = """
This is the student's response: <Student's response> {Students_response} </Student's response>
"""

recipes = {"Default":" ",
           "Hint-based Feedback":"""Provide subtle hints or clues without giving direct answers, allowing students to arrive at the correct answer on their own.""",
           "Direct Answer":"""Provide specific text replacement for students to improve the text.""",
           "Process-oriented Feedback":"""Get the student to reflect on whether they followed the required and correct processes to arrive at the answer, such as if they have read and understood the question, the process errors they made that caused them to write an inaccurate or incomplete description. If the student's response is lacking, provide a clear, actionable step for them to improve.""",
           "Socratic Feedback":"""Provide feedback in a concise manner, followed by a probing, open-ended question to encourage critical thinking. Tailor the question to the context of the student’s response, selecting one of the following types:
a. Clarifying Questions: 'What do you mean by that?' 'Can you provide an example?'
b. Assumption Questions: 'What are you assuming here?' Probing Questions: 'What evidence supports your claim?'
c. Implication Questions: 'What might be the consequences of this action?'
d. Perspective Questions: 'How might someone with a different viewpoint see this issue?'

The open-ended question should prompt students to analyse their assumptions, evaluate any evidence, synthesise information, or reflect on their thinking process to deepen their understanding.""",
           "Simple Feedback":"""Make it easy for young learners to understand by avoiding complex words and shortening sentences, but do not reveal the answer.""",
           "recipe 7":""" """,
           "recipe 8":""" """,
           "recipe 9":""" """
           }

prod_tools = [
        {
            "type": "function",
            "function": {
                "name": "get_annotated_feedback",
                "description": "Use the provided list of error tags, suggested answer or rubrics to carefully analyze the student's response and return feedback in a list format with the properties required in a JSON object",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "annotated_response": {
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
tools = [
  {
        "type": "function",
        "function": {
            "name": "get_annotated_feedback",
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

# Error mapping for the old LangFA-EL Errors to the new LangFA-EL Errors. This dictionary is sued in the WordDocx_AFA_converter.py file
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