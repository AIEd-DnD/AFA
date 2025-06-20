import helper_functions as AFA
import resources as rsrc
recipe_0 = "Present the feedback in a concise manner with a probing question that encourages students to think critically."
recipe_1 = "Present the feedback in a concise manner with a probing question that encourages students to think critically. The probing question be any of the following depending on the context of the student response. Clarifying Questions: 'What do you mean by that?' or 'Can you provide an example?' Assumption Questions: 'What are you assuming here?' Probing Questions: 'What evidence supports your claim?' Implication Questions: 'What might be the consequences of this action?' Perspective Questions: 'How might someone with a different viewpoint see this issue?' The question should be open-ended to stimulate critcal thinking and challenge students to analyse their assumptions, evaluate evidence if any, synthesise information or reflect on their thinking process."
recipe_2 = "Provide feedback in a concise manner, followed by a probing, open-ended question to encourage critical thinking. Tailor the question to the context of the student’s response, selecting one of the following types: Clarifying Questions: 'What do you mean by that?' 'Can you provide an example?' Assumption Questions: 'What are you assuming here?' Probing Questions: 'What evidence supports your claim?' Implication Questions: 'What might be the consequences of this action?' Perspective Questions: 'How might someone with a different viewpoint see this issue?' The open-ended question should prompt students to analyse their assumptions, evaluate any evidence, synthesise information, or reflect on their thinking process to deepen their understanding."
recipe_3 = "Provide feedback in the form of a single probing, open-ended question to encourage critical thinking. Tailor the question to the context of the student response, selecting one of the following types: Clarifying Questions: 'What do you mean by that?' 'Can you provide an example?' Assumption Questions: 'What are you assuming here?' Probing Questions: 'What evidence supports your claim?' Implication Questions: 'What might be the consequences of this action?' Perspective Questions: 'How might someone with a different viewpoint see this issue?'The open-ended question should prompt students to analyse their assumptions, evaluate any evidence, synthesise information, or reflect on their thinking process to deepen their understanding."



subject = "Chinese"
level = "Primary 5"
question = "根据文章内容，作者为什么去了动物园?"
student_response = "作者去了动物园是因为他想和朋友一起玩和享受着大自然了。"
recipe = ""
suggested_answer ="作者去了动物园是因为 (一分): 他想看看动物，(一分): 学到一些关于动物的知识，(一分):还想放松一下，享受大自然。"
rubrics=""
error_tags=""

assembled_prompt = AFA.assemble_prompt(subject, level, question, student_response, recipe, suggested_answer, rubrics, error_tags)
raw_response = AFA.get_annotations(assembled_prompt)
display = AFA.display_output(raw_response)