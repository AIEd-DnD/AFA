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
    filename = f"AFA_{file_name}_{timestamp}.csv"
    return filename

def write_into_record(filename, data):
    header = ['Subject','Level','Recipe','Error Tags','Suggested Answer','Rubrics','Question','Student Response','LLM Annotated Response','Gold Annotated Response','LLM Cards','Gold Cards','Identification TP Cards','Gold Identification Common Cards','Categorisation TP Cards','Identification TP Count','Categorisation TP Count','TP+FP','TP+FN','Identification F0.5','Categorisation F0.5']
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
    print(f"CSV file '{filename}' has been created successfully.")

def csv_to_list_of_dicts(file_path):
    result = list()
    with open(file_path, 'r') as csvfile:
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
    LLM_TP_first_identification = list()
    gold_common_first_identification = list()
    index_tracker = 0
    for annotation_card in gold_cards:
        for card_index in range(index_tracker, len(LLM_cards)):
            if LLM_cards[card_index]['phrase'] == annotation_card['phrase']:
                LLM_TP_first_identification.append(LLM_cards[card_index])
                gold_common_first_identification.append(annotation_card)
                index_tracker = card_index + 1
                break
    return LLM_TP_first_identification, gold_common_first_identification

def second_identification_checker(LLM_annotated_response, gold_annotated_response, LLM_TP_first_identification, gold_common_first_identification, tolerance):
    LLM_identified_TP = list()
    gold_identified_common = list()
    for i in range(len(gold_common_first_identification)):
        LLM_tag_id = '<tag id="' + str(LLM_TP_first_identification[i]['id']) + '">'
        gold_tag_id = '<tag id="' + str(gold_common_first_identification[i]['id']) + '">'
        LLM_tag_position = LLM_annotated_response.index(LLM_tag_id)
        gold_tag_position = gold_annotated_response.index(gold_tag_id)
        LLM_check_start = LLM_tag_position - tolerance
        gold_check_start = gold_tag_position - tolerance
        if LLM_annotated_response[LLM_check_start:LLM_tag_position] == gold_annotated_response[gold_check_start:gold_tag_position]:
            LLM_identified_TP.append(LLM_TP_first_identification[i])
            gold_identified_common.append(gold_common_first_identification[i])
    return LLM_identified_TP, gold_identified_common

def identification_checker(LLM_annotated_response, gold_annotated_response, LLM_cards, gold_cards, tolerance=20):
    LLM_TP_identified, gold_common_identified = first_identification_checker(LLM_cards, gold_cards)
    LLM_TP_identified_confirmed, gold_common_identified_confirmed = second_identification_checker(LLM_annotated_response, gold_annotated_response, LLM_TP_identified, gold_common_identified, tolerance)
    number_of_identified_TP = len(LLM_TP_identified_confirmed)
    return LLM_TP_identified_confirmed, gold_common_identified_confirmed, number_of_identified_TP

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

def identificationRecall(number_of_identified_TP, gold_cards):
    TP_plus_FN = len(gold_cards)
    identified_Recall = number_of_identified_TP/TP_plus_FN
    return identified_Recall

def identificationF05Score(number_of_identified_TP, LLM_cards, gold_cards):
    Precision = identificationPrecision(number_of_identified_TP, LLM_cards)
    Recall = identificationRecall(number_of_identified_TP, gold_cards)
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