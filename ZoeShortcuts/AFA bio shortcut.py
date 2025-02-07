import helper_functions as AFA
import resources as rsrc
recipe_0 = "Present the feedback in a concise manner with a probing question that encourages students to think critically."
recipe_1 = "Present the feedback in a concise manner with a probing question that encourages students to think critically. The probing question be any of the following depending on the context of the student response. Clarifying Questions: 'What do you mean by that?' or 'Can you provide an example?' Assumption Questions: 'What are you assuming here?' Probing Questions: 'What evidence supports your claim?' Implication Questions: 'What might be the consequences of this action?' Perspective Questions: 'How might someone with a different viewpoint see this issue?' The question should be open-ended to stimulate critcal thinking and challenge students to analyse their assumptions, evaluate evidence if any, synthesise information or reflect on their thinking process."
recipe_2 = "Provide feedback in a concise manner, followed by a probing, open-ended question to encourage critical thinking. Tailor the question to the context of the student’s response, selecting one of the following types: Clarifying Questions: 'What do you mean by that?' 'Can you provide an example?' Assumption Questions: 'What are you assuming here?' Probing Questions: 'What evidence supports your claim?' Implication Questions: 'What might be the consequences of this action?' Perspective Questions: 'How might someone with a different viewpoint see this issue?' The open-ended question should prompt students to analyse their assumptions, evaluate any evidence, synthesise information, or reflect on their thinking process to deepen their understanding."
recipe_3 = "Provide feedback in the form of a single probing, open-ended question to encourage critical thinking. Tailor the question to the context of the student response, selecting one of the following types: Clarifying Questions: 'What do you mean by that?' 'Can you provide an example?' Assumption Questions: 'What are you assuming here?' Probing Questions: 'What evidence supports your claim?' Implication Questions: 'What might be the consequences of this action?' Perspective Questions: 'How might someone with a different viewpoint see this issue?'The open-ended question should prompt students to analyse their assumptions, evaluate any evidence, synthesise information, or reflect on their thinking process to deepen their understanding."
recipe_process = "Get the student to reflect on whether they followed the required and correct processes to arrive at the answer, such as if they have read and understood the question, the process errors they made that caused them to write an inaccurate or incomplete description. Example: Have you linked your description to the question? Did you read carefully what the question is about? Does your description address what the question is about?"
recipe_direct ="Provide specific text replacement for students to improve the text "
recipe_hint="Provide subtle hints or clues without giving direct answers, allowing students to arrive at the correct answer on their own."
recipe_simple="Make it easy for 6 year old to understand by avoiding complex words and shortening sentences, but do not reveal the answer."

assembled_prompt = AFA.assemble_prompt("Biology", "Secondary 3", "What is the role of insulin after a heavy meal?", "There was too much glucose in the blood after consumption of breakfast, causing islets of Langerhans to be produced by the pancreas that secrete insulin. The liver then converts glucose into glucagon for storage and the blood glucose level decreases", recipe_simple, "(1 mark): At 9am, the concentration of glucose in the blood was high, causing the islets of Langerhans to secrete insulin. (1 mark): Insulin stimulates the liver to convert excess glucose into glycogen, (1 mark): causing the blood glucose level to decrease.", " ", " ")
raw_response = AFA.get_annotations(assembled_prompt)
display = AFA.display_output(raw_response)