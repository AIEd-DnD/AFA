import LLM_helper_f05 as llm
import helper_functions as AFA
import csv
from datetime import datetime

# Get current timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Create filename with timestamp
filename = f"AFA_temp0.1_test_{timestamp}.csv"

header = ['Incorrect sentence','False Negative Codes','Cleaned Output','Generated Errant Code List','All True Positives','All False Positives','All False Negatives','Punctuation TP','Punctuation FP','Punctuation FN','Grammar TP','Grammar FP','Grammar FN','Spelling TP','Spelling FP','Spelling FN','Word Choice TP','Word Choice FP','Word Choice FN','Sentence Structure TP','Sentence Structure FP','Sentence Structure FN']
data = []

sentence_list = llm.csv_to_list_of_dicts("insert file_path for datasets")

for scenario_dict in sentence_list:
    new_row = []
    print('Trying sentence '+str(sentence_list.index(scenario_dict)+1))
    test_sentence = scenario_dict['Incorrect Sentences']
    #print(test_sentence)
    new_row.append(test_sentence)
    gold_code_list = llm.extract_gold_code_list(scenario_dict)
    new_row.append(gold_code_list)
    unclean_output = llm.call_OpenAI(test_sentence)
    try:
        cleaned_output = llm.output_cleaner(unclean_output)
    except Exception as exp:
        print(f"An error occurred with this sentence while cleaning: {str(exp)}. Moving on to next sentence...")
        print(unclean_output)
        data.append(new_row)
        continue
    #print(cleaned_output)
    new_row.append(str(cleaned_output))
    try:
        generated_codes = llm.generate_errant_code_list(cleaned_output)
    except Exception as e:
        print(f"An error occurred with this sentence while generating code list: {str(e)}. Moving on to next sentence...")
        data.append(new_row)
        continue
    new_row.append(generated_codes)
    code_count = llm.results_counter(generated_codes, gold_code_list)
    for count in code_count:
        new_row.append(count)
    data.append(new_row)

with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(data)

print(f"CSV file '{filename}' has been created successfully.")