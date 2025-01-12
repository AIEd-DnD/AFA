import openai
import resources as rsrc
import ast
import os
import csv
from dotenv import load_dotenv
from datetime import datetime

load_dotenv('.env')
openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

def start_new_record(file_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Records/AFA_{file_name}_{timestamp}.csv"
    return filename

def write_into_record(filename, data):
    header = ['Subject','Level','Recipe','Error Tags','Suggested Answer','Rubrics','Question','Student Response','LLM Annotated Response','Gold Annotated Response','LLM Cards','Gold Cards','Identification TP Cards','Gold Identification Common Cards','Identification TP Count','Common Gold Count','TP+FP (Total LLM)','TP+FN (Total Gold)','Precision','Recall','F05 Score']
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
    print(f"CSV file '{filename}' has been created successfully.")

def csv_to_list_of_dicts(file_path):
    result = list()
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            result.append(row)
    return result

def extract_parameters(parameter_dict):
    subject = parameter_dict['subject']
    level = parameter_dict['level']
    question = parameter_dict['question']
    students_response = parameter_dict['students_response']
    recipe = parameter_dict['recipe']
    suggested_answer = parameter_dict['suggested_answer'] 
    rubrics = parameter_dict['rubrics']
    error_tags = parameter_dict['error_tags']
    gold_response = parameter_dict['gold_rated_response']
    return subject, level, question, students_response, recipe, suggested_answer, rubrics, error_tags, gold_response

def assemble_prompt(subject, level, question, students_response, recipe=" ", suggested_answer=" ", rubrics=" ", error_tags=" "):
   assembled_prompt = rsrc.base_prompt.format(
     Subject=subject,
     Level=level,
     Question=question,
     Model_answer=suggested_answer, 
     Rubrics=rubrics, 
     Error_types=error_tags, 
     Instructions=recipe,
     Students_response=students_response 
     )
   
   return assembled_prompt

def get_annotations(assembled_prompt):
   response = client.chat.completions.create(
     model="gpt-4o-2024-08-06",
     temperature = 0.1,
     max_tokens = 4000,
     tools = rsrc.tools,
     messages = [{"role": "user", "content": assembled_prompt}]
   )
   return response.choices[0].message.tool_calls[0].function.arguments

def string_to_dict(dict_string):
    try:
        return ast.literal_eval(dict_string)
    except (ValueError, SyntaxError):
        raise ValueError("Invalid dictionary string format")

def extract_annotation_details(LLM_dict, gold_dict):
    LLM_annotated_response = LLM_dict['annotated_response']
    gold_annotated_response = gold_dict['annotated_response']
    LLM_cards = LLM_dict['feedback_list']
    gold_cards = gold_dict['feedback_list']
    return LLM_annotated_response, gold_annotated_response, LLM_cards, gold_cards

def first_identification_checker(LLM_cards, gold_cards):
    print("Running First Checker")
    LLM_TP_first_identification = list()
    gold_common_first_identification = list()
    LLM_return_size = len(LLM_cards)
    gold_size = len(gold_cards)
    LLM_identification_counter = dict()
    gold_identification_counter = dict()

    for i in range(LLM_return_size):
        LLM_identification_counter[i] = 0

    for e in range(gold_size):
        gold_identification_counter[e] = 0
    
    for annotation_card in gold_cards:
        for card_index in range(LLM_return_size):
            if LLM_cards[card_index]['phrase'] == annotation_card['phrase']:
                LLM_TP_first_identification.append(LLM_cards[card_index])
                gold_common_first_identification.append(annotation_card)
                LLM_identification_counter[card_index] += 1
                gold_identification_counter[gold_cards.index(annotation_card)] += 1

    print(len(LLM_TP_first_identification))
    return LLM_TP_first_identification, gold_common_first_identification, LLM_identification_counter, gold_identification_counter

def tag_removal(annotated_response, annotation_card_list):
    cleaned_text = annotated_response.replace('</tag>', '', len(annotation_card_list))
    for i in range(len(annotation_card_list)):
        cleaned_text = cleaned_text.replace(f'<tag id="{annotation_card_list[i]["id"]}">', '')
    return cleaned_text

def wrapping_character_counter(phrase, sub_phrase):
    phrase_length = len(phrase)
    sub_phrase_start_position = phrase.index(sub_phrase)
    sub_phrase_end_position = sub_phrase_start_position + len(sub_phrase)
    left_side_length = sub_phrase_start_position
    right_side_length = phrase_length - sub_phrase_end_position
    return left_side_length, right_side_length

def tag_locator(annotation_number, annotated_response):
    tag_id = '<tag id="' + str(annotation_number) + '">'
    tag_position = annotated_response.index(tag_id)
    end_tag_position = annotated_response.index('</tag>', tag_position) + len('</tag>')
    return tag_position, end_tag_position

def expand_subphrase_to_phrase(cleaned_text, sub_phrase, annotation_number, annotated_response, annotation_card_list, tag_position, end_tag_position, left_side_length, right_side_length):
    card_number = annotation_number
    left_end_tag_count = annotated_response[:tag_position].count('</tag>')
    left_start_tag_count = annotated_response[:tag_position].count('<tag')
    left_XML_tag_char_count = left_end_tag_count * len('</tag>')
    for i in range(left_start_tag_count):
        left_tag_id = f'<tag id="{annotation_card_list[i]['id']}">'
        left_tag_char_count = len(left_tag_id)
        left_XML_tag_char_count += left_tag_char_count
    
    sub_phrase_start_position_cleaned = tag_position - left_XML_tag_char_count
    sub_phrase_end_position_cleaned = end_tag_position - left_XML_tag_char_count - len('</tag>') - len(f'<tag id="{card_number}">')

    left_slice_start = sub_phrase_start_position_cleaned - left_side_length
    right_slice_end = sub_phrase_end_position_cleaned + right_side_length
    if left_slice_start < 0:
        left_slice_start = 0
    if right_slice_end > len(cleaned_text):
        right_slice_end = len(cleaned_text)
    left_slice = cleaned_text[left_slice_start:sub_phrase_start_position_cleaned]
    right_slice = cleaned_text[sub_phrase_end_position_cleaned:right_slice_end]
    expanded_phrase = left_slice + sub_phrase + right_slice
    return expanded_phrase

def second_identification_checker(LLM_annotated_response, gold_annotated_response, LLM_TP_first_identification, gold_common_first_identification, LLM_cards, gold_cards, strictness, LLM_identification_counter, gold_identification_counter):
    print("Running Second Checker")
    LLM_TP_waitlist = list()
    gold_common_waitlist = list()
    LLM_identified_TP = list()
    gold_identified_common = list()
    for i in range(len(gold_common_first_identification)):
        LLM_tag_position, LLM_end_tag_position = tag_locator(LLM_TP_first_identification[i]['id'], LLM_annotated_response)
        gold_tag_position, gold_end_tag_position = tag_locator(gold_common_first_identification[i]['id'], gold_annotated_response)

        LLM_cleaned_text = tag_removal(LLM_annotated_response, LLM_cards)
        gold_cleaned_text = tag_removal(gold_annotated_response, gold_cards)
        #print(f"Post first check LLM Phrase: {LLM_TP_first_identification[i]['phrase']}")
        #print(f"Post first check gold Phrase: {gold_common_first_identification[i]['phrase']}")
        LLM_expanded_phrase = expand_subphrase_to_phrase(LLM_cleaned_text, LLM_TP_first_identification[i]['phrase'], LLM_TP_first_identification[i]['id'], LLM_annotated_response, LLM_cards, LLM_tag_position, LLM_end_tag_position, left_side_length=strictness, right_side_length=strictness)
        #print(f"LLM_expanded_phrase: {LLM_expanded_phrase}")
        gold_expanded_phrase = expand_subphrase_to_phrase(gold_cleaned_text, gold_common_first_identification[i]['phrase'], gold_common_first_identification[i]['id'], gold_annotated_response, gold_cards, gold_tag_position, gold_end_tag_position, left_side_length=strictness, right_side_length=strictness)
        #print(f"gold_expanded_phrase: {gold_expanded_phrase}")
        
        if LLM_expanded_phrase == gold_expanded_phrase:
            LLM_identified_TP.append(LLM_TP_first_identification[i])
            gold_identified_common.append(gold_common_first_identification[i])
            #print("Match found.")
        else:
            find_LLM_index = LLM_cards.index(LLM_TP_first_identification[i])
            find_gold_index = gold_cards.index(gold_common_first_identification[i])
            LLM_identification_counter[find_LLM_index] -= 1
            gold_identification_counter[find_gold_index] -= 1
            #print("Match not found.")
        
    for key in LLM_identification_counter:
        if LLM_identification_counter[key] == 0:
            LLM_TP_waitlist.append(LLM_cards[key])
    
    for key in gold_identification_counter:
        if gold_identification_counter[key] == 0:
            gold_common_waitlist.append(gold_cards[key])

    return LLM_identified_TP, gold_identified_common, LLM_TP_waitlist, gold_common_waitlist

def third_identification_checker(LLM_TP_waitlist, gold_common_waitlist, LLM_identified_TP, gold_identified_common, LLM_annotated_response, gold_annotated_response, LLM_cards, gold_cards):
    print("Running Third Checker")
    print(len(LLM_TP_waitlist))
    for annotation_card in gold_common_waitlist:
        print(f"Annotation Card: {annotation_card}")
        for card_index in range(len(LLM_TP_waitlist)):
            if len(LLM_TP_waitlist[card_index]['phrase']) < len(annotation_card['phrase']) and LLM_TP_waitlist[card_index]['phrase'] in annotation_card['phrase']:
                LLM_left_side, LLM_right_side = wrapping_character_counter(annotation_card['phrase'], LLM_TP_waitlist[card_index]['phrase'])
                LLM_tag_position, LLM_end_tag_position = tag_locator(LLM_TP_waitlist[card_index]['id'], LLM_annotated_response)
                gold_tag_position, gold_end_tag_position = tag_locator(annotation_card['id'], gold_annotated_response)
                cleaned_text = tag_removal(LLM_annotated_response, LLM_cards)
                LLM_phrase_check = expand_subphrase_to_phrase(cleaned_text, LLM_TP_waitlist[card_index]['phrase'], LLM_TP_waitlist[card_index]['id'], LLM_annotated_response, LLM_cards, LLM_tag_position, LLM_end_tag_position, left_side_length=LLM_left_side+20, right_side_length=LLM_right_side+20)
                gold_phrase_check = expand_subphrase_to_phrase(cleaned_text, annotation_card['phrase'], annotation_card['id'], gold_annotated_response, gold_cards, gold_tag_position, gold_end_tag_position, 20, 20)

                if LLM_phrase_check == gold_phrase_check:
                    #print("llm longer than gold")
                    #print(LLM_TP_waitlist[card_index])
                    #print(" ")
                    LLM_identified_TP.append(LLM_TP_waitlist[card_index])
                    if annotation_card not in gold_identified_common:
                        gold_identified_common.append(annotation_card)

            elif len(LLM_TP_waitlist[card_index]['phrase']) > len(annotation_card['phrase']) and annotation_card['phrase'] in LLM_TP_waitlist[card_index]['phrase']:
                gold_left_side, gold_right_side = wrapping_character_counter(LLM_TP_waitlist[card_index]['phrase'], annotation_card['phrase'])
                gold_tag_position, gold_end_tag_position = tag_locator(annotation_card['id'], gold_annotated_response)
                LLM_tag_position, LLM_end_tag_position = tag_locator(LLM_TP_waitlist[card_index]['id'], LLM_annotated_response)
                cleaned_text = tag_removal(gold_annotated_response, gold_cards)
                gold_phrase_check = expand_subphrase_to_phrase(cleaned_text, annotation_card['phrase'], annotation_card['id'], gold_annotated_response, gold_cards, gold_tag_position, gold_end_tag_position, left_side_length=gold_left_side+20, right_side_length=gold_right_side+20)
                LLM_phrase_check = expand_subphrase_to_phrase(cleaned_text, LLM_TP_waitlist[card_index]['phrase'], LLM_TP_waitlist[card_index]['id'], LLM_annotated_response, LLM_cards, LLM_tag_position, LLM_end_tag_position, 20, 20)

                if gold_phrase_check == LLM_phrase_check:
                    #print("gold longer than llm")
                    #print(LLM_TP_waitlist[card_index])
                    #print(" ")
                    if LLM_TP_waitlist[card_index] not in LLM_identified_TP:
                        LLM_identified_TP.append(LLM_TP_waitlist[card_index])
                    gold_identified_common.append(annotation_card)

    return LLM_identified_TP, gold_identified_common

def identification_checker(LLM_annotated_response, gold_annotated_response, LLM_cards, gold_cards, strictness=20):
    LLM_TP_identified, gold_common_identified, LLM_TP_id_counter, gold_common_id_counter = first_identification_checker(LLM_cards, gold_cards)
    LLM_identified_TP, gold_identified_common, LLM_TP_waitlist, gold_common_waitlist = second_identification_checker(LLM_annotated_response, gold_annotated_response, LLM_TP_identified, gold_common_identified, LLM_cards, gold_cards, strictness, LLM_TP_id_counter, gold_common_id_counter)
    #print(f"LLM_identified_TP: {LLM_identified_TP}")
    LLM_TP_identified_confirmed, gold_common_identified_confirmed = third_identification_checker(LLM_TP_waitlist, gold_common_waitlist, LLM_identified_TP, gold_identified_common, LLM_annotated_response, gold_annotated_response, LLM_cards, gold_cards)
    #print(f"LLM_TP_identified_confirmed: {LLM_TP_identified_confirmed}")
    number_of_identified_TP = len(LLM_TP_identified_confirmed)
    number_of_common_gold = len(gold_common_identified_confirmed)
    return LLM_TP_identified_confirmed, gold_common_identified_confirmed, number_of_identified_TP, number_of_common_gold

def categorisation_checker(LLM_TP_identified_confirmed, gold_common_identified_confirmed, number_of_identified_TP):
    categorisation_TP = list()
    for i in range(number_of_identified_TP):
        LLM_error_tag = LLM_TP_identified_confirmed[i]['error_tag'][0]['errorType']
        gold_error_tag = gold_common_identified_confirmed[i]['error_tag'][0]['errorType']
        if LLM_error_tag == gold_error_tag:
            categorisation_TP.append(LLM_TP_identified_confirmed[i])
        number_of_categorised_TP = len(categorisation_TP)
    return categorisation_TP, number_of_categorised_TP

def identificationPrecision(number_of_identified_TP, LLM_cards):
    TP_plus_FP = len(LLM_cards) 
    identified_Precision = number_of_identified_TP/TP_plus_FP
    return identified_Precision

def identificationRecall(number_of_common_gold, gold_cards):
    TP_plus_FN = len(gold_cards)
    identified_Recall = number_of_common_gold/TP_plus_FN
    return identified_Recall

def identificationF05Score(number_of_identified_TP, number_of_common_gold, LLM_cards, gold_cards):
    Precision = identificationPrecision(number_of_identified_TP, LLM_cards)
    Recall = identificationRecall(number_of_common_gold, gold_cards)
    identified_F05 = (1 + 0.25)*(Precision*Recall)/((0.25*Precision)+Recall)
    return identified_F05

def categorisationPrecision(number_of_categorised_TP, LLM_cards):
    TP_plus_FP = len(LLM_cards) 
    categorised_Precision = number_of_categorised_TP/TP_plus_FP
    return categorised_Precision

def categorisationRecall(number_of_categorised_TP, gold_cards):
    TP_plus_FN = len(gold_cards)
    categorised_Recall = number_of_categorised_TP/TP_plus_FN
    return categorised_Recall

def categorisationF05Score(number_of_categorised_TP, LLM_cards, gold_cards):
    Precision = categorisationPrecision(number_of_categorised_TP, LLM_cards)
    Recall = categorisationRecall(number_of_categorised_TP, gold_cards)
    categorised_F05 = (1 + 0.25)*(Precision*Recall)/((0.25*Precision)+Recall)
    return categorised_F05