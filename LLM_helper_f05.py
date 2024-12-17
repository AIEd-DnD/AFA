#import json
import re
import ast
import csv

def errant_counter(code_list):
    counter = 0
    for cat in rsrc.errant_list:
        for code in code_list:
            if code in cat:
                counter += 1
    return counter

def punc_counter(code_list):
    counter = 0
    for code in code_list:
        if code in rsrc.punctuation:
            counter += 1
    return counter

def gram_counter(code_list):
    counter = 0
    for code in code_list:
        if code in rsrc.grammar:
            counter += 1
    return counter

def spell_counter(code_list):
    counter = 0
    for code in code_list:
        if code in rsrc.spelling:
            counter += 1
    return counter

def wordchoice_counter(code_list):
    counter = 0
    for code in code_list:
        if code in rsrc.word_choice:
            counter += 1
    return counter

def sent_counter(code_list):
    counter = 0
    for code in code_list:
        if code in rsrc.sentence_structure:
            counter += 1
    return counter

def string_to_dict(dict_string):
    try:
        return ast.literal_eval(dict_string)
    except (ValueError, SyntaxError):
        raise ValueError("Invalid dictionary string format")

def dict_slicer(dict_string):
    for i in range(len(dict_string)):
        if dict_string[i] == '{':
            start = i
            break
    new_dict_string = dict_string[start:]
    return new_dict_string

def clean_string_dict(dict_string):
    # Remove whitespace around colons
    dict_string = re.sub(r'\s*:\s*', ':', dict_string)
    
    # Remove whitespace around commas
    dict_string = re.sub(r'\s*,\s*', ',', dict_string)
    
    # Remove whitespace around brackets
    dict_string = re.sub(r'\s*{\s*', '{', dict_string)
    dict_string = re.sub(r'\s*}\s*', '}', dict_string)
    
    # Remove whitespace around square brackets (for lists)
    dict_string = re.sub(r'\s*\[\s*', '[', dict_string)
    dict_string = re.sub(r'\s*\]\s*', ']', dict_string)
    
    return dict_string

def csv_to_list_of_dicts(file_path):
    result = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            result.append(row)
    return result

def message_formatter(sentence, example):
    message = rsrc.langfa_el_user.format(sentence=sentence,example=example)
    return message

#test_sentence = 'For examples food , factories use machinery to produce good such as instant noodles .'

def call_Anthropic(user_sentence):
    user_message = message_formatter(user_sentence,rsrc.user_example)
    #print(user_message)
    
    client = anthropic.Anthropic(api_key=rsrc.AIEd_DnD)
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4000,
        #tools=rsrc.FRQ_tools,
        temperature=0.2,
        system = rsrc.langfa_el_system,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text

def call_OpenAI(user_sentence):
    user_message = message_formatter(user_sentence,rsrc.user_example)
    client = OpenAI(api_key=rsrc.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        temperature = 0.2,
        max_tokens = 4000,
        response_format = {"type":"json_object"},
        messages = [{"role": "system", "content": rsrc.langfa_el_system},
                    {"role": "user", "content": user_message}
                    ])
    return response.choices[0].message.content

def output_cleaner(llm_response):
    new_output = llm_response.replace("\n", "")
    cleaned_string = dict_slicer(new_output)
    cooked_string = clean_string_dict(cleaned_string)
    served_dict = string_to_dict(cooked_string)
    return served_dict

#output = call_Anthropic(test_sentence)

#served_dict = output_cleaner(output)

def extract_gold_code_list(single_row_dict):
    string_list = single_row_dict['Errant Codes']
    actual_list = ast.literal_eval(string_list)
    return actual_list

def generate_errant_code_list(output_dict):
    if isinstance(output_dict['results'], dict):
        num_of_code = len(output_dict['results']['answer'])
    elif isinstance(output_dict['results'], list):
        pass

    errant_code_list = []
    if isinstance(output_dict['results'], dict):
        for index in range(num_of_code):
            errant_code_list.append(output_dict['results']['answer'][index]['code'])
    elif isinstance(output_dict['results'], list):
        for query in output_dict['results']:
            query_size = len(query['answer'])
            for index in range(query_size):
                errant_code_list.append(query['answer'][index]['code'])

    return errant_code_list

def results_counter(errant_code_list, gold_code_list):
    data_row = []
    false_positive_list = []
    true_positive_list = []
    false_negative_list = gold_code_list
    #print(false_negative_list)
    #gold_space = len(false_negative_list)
    #print("True Positives + False Negatives = "+str(gold_space))
    #print(errant_code_list)
    total_positive = len(errant_code_list)
    #print("True Positives + False Positives = "+str(total_positive))
    for code in errant_code_list:
        if code not in false_negative_list:
            false_positive_list.append(code)
        elif code in false_negative_list:
            false_negative_list.remove(code)
            true_positive_list.append(code)
    #print(false_positive_list)
    false_positive = len(false_positive_list)
    #print('False positives = '+str(false_positive))
    #print(false_negative_list)
    false_negative = len(false_negative_list)
    #print('False negatives = '+str(false_negative))
    true_positive_fp = total_positive - false_positive
    data_row.append(true_positive_fp)
    data_row.append(false_positive)
    data_row.append(false_negative)
    #print('True positives = '+str(true_positive_fp))
    #true_positive_fn = gold_space - false_negative
    #print('True positives = '+str(true_positive_fn))
    #print(' ')
    #print('These are the punctuation counts:')
    punc_count_TP = punc_counter(true_positive_list)
    punc_count_FP = punc_counter(false_positive_list)
    punc_count_FN = punc_counter(false_negative_list)
    data_row.append(punc_count_TP)
    data_row.append(punc_count_FP)
    data_row.append(punc_count_FN)
    #print(punc_count_TP)
    #print(punc_count_FP)
    #print(punc_count_FN)
    #print(' ')
    #print('These are the grammar counts:')
    gram_count_TP = gram_counter(true_positive_list)
    gram_count_FP = gram_counter(false_positive_list)
    gram_count_FN = gram_counter(false_negative_list)
    data_row.append(gram_count_TP)
    data_row.append(gram_count_FP)
    data_row.append(gram_count_FN)
    #print(gram_count_TP)
    #print(gram_count_FP)
    #print(gram_count_FN)
    #print(' ')
    #print('These are the spelling counts:')
    spell_count_TP = spell_counter(true_positive_list)
    spell_count_FP = spell_counter(false_positive_list)
    spell_count_FN = spell_counter(false_negative_list)
    data_row.append(spell_count_TP)
    data_row.append(spell_count_FP)
    data_row.append(spell_count_FN)
    #print(spell_count_TP)
    #print(spell_count_FP)
    #print(spell_count_FN)
    #print(' ')
    #print('These are the word choice counts:')
    wordchoice_count_TP = wordchoice_counter(true_positive_list)
    wordchoice_count_FP = wordchoice_counter(false_positive_list)
    wordchoice_count_FN = wordchoice_counter(false_negative_list)
    data_row.append(wordchoice_count_TP)
    data_row.append(wordchoice_count_FP)
    data_row.append(wordchoice_count_FN)
    #print(wordchoice_count_TP)
    #print(wordchoice_count_FP)
    #print(wordchoice_count_FN)
    #print(' ')
    #print('These are the sentence structure counts:')
    sent_count_TP = sent_counter(true_positive_list)
    sent_count_FP = sent_counter(false_positive_list)
    sent_count_FN = sent_counter(false_negative_list)
    data_row.append(sent_count_TP)
    data_row.append(sent_count_FP)
    data_row.append(sent_count_FN)
    #print(sent_count_TP)
    #print(sent_count_FP)
    #print(sent_count_FN)
    #print(' ')
    #print('These are the total errant code counts:')
    #total_count_TP = punc_counter(true_positive_list)
    #total_count_FP = punc_counter(false_positive_list)
    #total_count_FN = punc_counter(false_negative_list)
    #print(total_count_TP)
    #print(total_count_FP)
    #print(total_count_FN)
    return data_row

def results_printer(errant_code_list, gold_code_list):
    false_positive_list = []
    true_positive_list = []
    false_negative_list = gold_code_list
    total_positive = len(errant_code_list)
    for code in errant_code_list:
        if code not in false_negative_list:
            false_positive_list.append(code)
        elif code in false_negative_list:
            false_negative_list.remove(code)
            true_positive_list.append(code)
    print('True Positive List: '+str(true_positive_list))
    print('False Positive List: '+str(false_positive_list))
    print('False Negative List: '+str(false_negative_list))
    false_positive = len(false_positive_list)
    print('Total False positives = '+str(false_positive))
    false_negative = len(false_negative_list)
    print('Total False negatives = '+str(false_negative))
    true_positive_fp = total_positive - false_positive
    print('Total True positives = '+str(true_positive_fp))
    print(' ')
    print('These are the punctuation counts:')
    punc_count_TP = punc_counter(true_positive_list)
    punc_count_FP = punc_counter(false_positive_list)
    punc_count_FN = punc_counter(false_negative_list)
    print(punc_count_TP)
    print(punc_count_FP)
    print(punc_count_FN)
    print(' ')
    print('These are the grammar counts:')
    gram_count_TP = gram_counter(true_positive_list)
    gram_count_FP = gram_counter(false_positive_list)
    gram_count_FN = gram_counter(false_negative_list)
    print(gram_count_TP)
    print(gram_count_FP)
    print(gram_count_FN)
    print(' ')
    print('These are the spelling counts:')
    spell_count_TP = spell_counter(true_positive_list)
    spell_count_FP = spell_counter(false_positive_list)
    spell_count_FN = spell_counter(false_negative_list)
    print(spell_count_TP)
    print(spell_count_FP)
    print(spell_count_FN)
    print(' ')
    print('These are the word choice counts:')
    wordchoice_count_TP = wordchoice_counter(true_positive_list)
    wordchoice_count_FP = wordchoice_counter(false_positive_list)
    wordchoice_count_FN = wordchoice_counter(false_negative_list)
    print(wordchoice_count_TP)
    print(wordchoice_count_FP)
    print(wordchoice_count_FN)
    print(' ')
    print('These are the sentence structure counts:')
    sent_count_TP = sent_counter(true_positive_list)
    sent_count_FP = sent_counter(false_positive_list)
    sent_count_FN = sent_counter(false_negative_list)
    print(sent_count_TP)
    print(sent_count_FP)
    print(sent_count_FN)
    print(' ')
    