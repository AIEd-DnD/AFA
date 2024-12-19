import helper_functions as AFA
import resources as rsrc
import LLM_helper_f05 as llm

subject = "English"
level = "Primary 5"
question = " "
students_response = rsrc.full_59_error_sample
recipe = " "
suggested_answer = " "
rubrics = " "
error_tags = rsrc.LangFA_errors


message = AFA.assemble_prompt(subject,level,question,students_response,recipe,suggested_answer,rubrics,error_tags)
string_dict = AFA.get_annotations(message)
response_dict = llm.string_to_dict(string_dict)
gold_rated_dict = rsrc.full_59_error_LangFA_conversion

LLM_annotated_response = response_dict['annotated_response']
gold_rated_annotated_response = gold_rated_dict['annotated_response']
LLM_cards = response_dict['feedback_list']
gold_rated_cards = gold_rated_dict['feedback_list']

common_cards = []
TP_annotations_only = []

index_tracker = 0

for annotation_card in gold_rated_cards:
    for card_index in range(index_tracker, len(LLM_cards)):
        print("Comparing AFA error: ***"+LLM_cards[card_index]['phrase']+"*** against LangFA-EL error: ***"+annotation_card['phrase']+"***")
        if LLM_cards[card_index]['phrase'] == annotation_card['phrase']:
            TP_annotations_only.append(LLM_cards[card_index])
            common_cards.append(annotation_card)
            index_tracker = card_index + 1
            print("Match detected!")
            break

#print(TP_annotations_only)
#print("")
#print(common_cards)

#print("There are "+ str(len(TP_annotations_only)) + " True Positives and " + str(len(common_cards)) + " common cards.")

confirmed_LLM_TP = []
confirmed_common_cards = []

for i in range(len(common_cards)):
    print("Checking card number "+str(i+1))
    LLM_tag_id = '<tag id="' + str(TP_annotations_only[i]['id']) + '">'
    gold_tag_id = '<tag id="' + str(common_cards[i]['id']) + '">'
    LLM_tag_position = LLM_annotated_response.index(LLM_tag_id)
    gold_tag_position = gold_rated_annotated_response.index(gold_tag_id)
    LLM_check_start = LLM_tag_position - 20
    gold_check_start = gold_tag_position - 20
    if LLM_annotated_response[LLM_check_start:LLM_tag_position] == gold_rated_annotated_response[gold_check_start:gold_tag_position]:
        print("True positive confirmed "+"number "+str(i+1))
        confirmed_LLM_TP.append(TP_annotations_only[i])
        confirmed_common_cards.append(common_cards[i])

#print(confirmed_LLM_TP)
#print("")
#print(confirmed_common_cards)

identification_TP_count = len(confirmed_LLM_TP)

categorisation_TP_list = []

test_LLM = [{'id': 8, 'phrase': 'but', 'error_tag': [{'errorType': 'Remove: Conjunction'}], 'comment': "Remove 'but' as it is redundant with 'although'."}, {'id': 10, 'phrase': 'using', 'error_tag': [{'errorType': 'Replace: Word/Phrase'}], 'comment': "Use 'use' instead of 'using' for correct form."}, {'id': 14, 'phrase': 'researches', 'error_tag': [{'errorType': 'Replace: Noun'}], 'comment': "Use 'research' as it is uncountable."}, {'id': 15, 'phrase': 'a', 'error_tag': [{'errorType': 'Replace: Determiner'}], 'comment': "Use 'an' before 'early' for correct article usage."}, {'id': 19, 'phrase': 'can', 'error_tag': [{'errorType': 'Replace: Verb Form'}], 'comment': "Use 'could' for past tense."}, {'id': 21, 'phrase': 'thought', 'error_tag': [{'errorType': 'Replace: Noun'}], 'comment': "Use 'thoughts' for plural form."}, {'id': 23, 'phrase': 'suprised', 'error_tag': [{'errorType': 'Replace: Spelling'}], 'comment': "Correct spelling is 'surprised'."}, {'id': 25, 'phrase': 'hours', 'error_tag': [{'errorType': 'Replace: Possessive'}], 'comment': "Use 'hour's' for singular possessive form."}, {'id': 26, 'phrase': 'knows', 'error_tag': [{'errorType': 'Replace: Verb Form'}], 'comment': "Use 'knew' for past tense."}, {'id': 27, 'phrase': 'overcomed', 'error_tag': [{'errorType': 'Replace: Verb Form'}], 'comment': "Use 'overcome' for correct past participle."}, {'id': 28, 'phrase': 'eat', 'error_tag': [{'errorType': 'Replace: Verb Form'}], 'comment': "Use 'eats' for correct subject-verb agreement."}, {'id': 29, 'phrase': 'lesser', 'error_tag': [{'errorType': 'Replace: Adjective'}], 'comment': "Use 'less' for correct comparative form."}, {'id': 30, 'phrase': 'laughters', 'error_tag': [{'errorType': 'Replace: Noun'}], 'comment': "Use 'laughter' as it is uncountable."}]

test_gold = [{'id': 19, 'phrase': 'but', 'error_tag': [{'errorType': 'Remove: Conjunction'}], 'comment': 'Consider removing the highlighted conjunction., '}, {'id': 24, 'phrase': 'using', 'error_tag': [{'errorType': 'Remove: Verb'}], 'comment': 'Consider removing the highlighted verb., '}, {'id': 33, 'phrase': 'researches', 'error_tag': [{'errorType': 'Replace: Noun Number'}], 'comment': 'Consider if the highlighted noun should be singular or plural. Suggestion(s):, research'}, {'id': 35, 'phrase': 'a', 'error_tag': [{'errorType': 'Replace: Determiner'}], 'comment': 'Consider changing the highlighted determiner. Suggestion(s):, an'}, {'id': 42, 'phrase': 'can', 'error_tag': [{'errorType': 'Replace: Verb'}], 'comment': 'Consider changing the highlighted verb. Suggestion(s):, could'}, {'id': 45, 'phrase': 'thought', 'error_tag': [{'errorType': 'Replace: Word Form'}], 'comment': 'Consider changing the form of the highlighted word. Suggestion(s):, thoughts'}, {'id': 48, 'phrase': 'suprised', 'error_tag': [{'errorType': 'Replace: Spelling'}], 'comment': 'Consider if the spelling of the highlighted word is accurate. Suggestions:, surprised'}, {'id': 50, 'phrase': 'hours', 'error_tag': [{'errorType': 'Replace: Possessive Noun'}], 'comment': "Consider if the highlighted noun should be in possessive form. Suggestion(s):, hour's"}, {'id': 51, 'phrase': 'knows', 'error_tag': [{'errorType': 'Replace: Verb Form'}], 'comment': 'Consider changing the form of the highlighted verb. Suggestion(s):, know'}, {'id': 52, 'phrase': 'overcomed', 'error_tag': [{'errorType': 'Replace: Verb Spelling'}], 'comment': 'Consider if the spelling of the highlighted verb is accurate. Suggestion(s):, overcome'}, {'id': 53, 'phrase': 'eat', 'error_tag': [{'errorType': 'Replace: Subject-Verb Agreement'}], 'comment': 'Consider if the highlighted verb agrees with the subject. Suggestion(s):, eats'}, {'id': 54, 'phrase': 'lesser', 'error_tag': [{'errorType': 'Replace: Adjective'}], 'comment': 'Consider changing the form of the highlighted adjective. Suggestion(s):, less'}, {'id': 55, 'phrase': 'laughters', 'error_tag': [{'errorType': 'Replace: Noun Number'}], 'comment': 'Consider if the highlighted noun is uncountable. Suggestion(s):, laughter'}]

for i in range(len(test_LLM)):
    LLM_error_tag = test_LLM[i]['error_tag'][0]['errorType']
    gold_error_tag = test_gold[i]['error_tag'][0]['errorType']
    if LLM_error_tag == gold_error_tag:
        categorisation_TP_list.append(test_LLM[i])

print("")
print(categorisation_TP_list)
print("")
print("There are actually " + str(len(categorisation_TP_list)) + " True Positives.")