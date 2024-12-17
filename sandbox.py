import helper_functions as AFA
import resources as rsrc
import LLM_helper_f05 as llm

subject = "English"
level = "Primary"
question = " "
student_answer = rsrc.full_59_error_sample
recipe = " "
suggested_answer = " "
rubrics = " "
error_tags = rsrc.LangFA_errors


message = AFA.assemble_prompt(subject,level,question,student_answer,recipe,suggested_answer,rubrics,error_tags)
response = AFA.get_annotations(message)
string_dict = response.choices[0].message.tool_calls[0].function.arguments
response_dict = llm.string_to_dict(string_dict)

#print(response_dict)

LLM_returned_errors = []
for annotation in response_dict["feedback_list"]:
    annotation_dict = {}
    annotation_dict['annotation'] = annotation['phrase']
    annotation_dict['error_tag'] = annotation['error_tag'][0]['errorType']
    LLM_returned_errors.append(annotation_dict)
print(LLM_returned_errors)

gold_rated = [] #this needs to be extracted from dataset and assembled in the same way as LLM_returned_errors
gold_rated_captured = []

TP_annotations_only = []

#for annotation_card in LLM_returned_errors:
    #gold_rated_copy = list()
    #gold_rated_copy = gold_rated
    #for card in gold_rated_copy:
        #if card['annotation'] == annotation_card['annotation']:
            #TP_annotations_only.append(annotation_card)
            #LLM_returned_errors.remove(annotation_card)
            #gold_rated_captured.append(card)
            #gold_rated_copy.remove(card)
            #break
        #else:
            #gold_rated.remove(card)


