import AFA_eval_functions as AFA

data = list()
#test_name = input("Please enter the name of the test: ")               #uncomment this to unlock user input for test name
#file_path = input("Please enter the file path of the test data: ")     #uncomment this to unlock user input for file path
evaluation_record = AFA.start_new_record("test_run_temp03")
response_list = AFA.csv_to_list_of_dicts("Dataset/AFA_BulkEval_Test1.csv")

for scenario_dict in response_list:
    new_row = list()
    subject, level, question, students_response, recipe, suggested_answer, rubrics, error_tags, full_gold_response = AFA.extract_parameters(scenario_dict)
    
    new_row.append(subject)
    new_row.append(level)
    new_row.append(recipe)
    new_row.append(error_tags)
    new_row.append(suggested_answer)
    new_row.append(rubrics)
    new_row.append(question)
    new_row.append(students_response)
    
    print('Trying response '+str(response_list.index(scenario_dict)+1))
    
    message = AFA.assemble_prompt(subject, level, question, students_response, recipe, suggested_answer, rubrics, error_tags)
    full_LLM_response = AFA.get_annotations(message)
    
    try:
        LLM_dict = AFA.string_to_dict(full_LLM_response)
        gold_dict = AFA.string_to_dict(full_gold_response)
    except Exception as exp:
        print(f"An error occurred while attempting to convert the LLM and gold responses into dictionaries: {str(exp)}.")
        data.append(new_row)
        continue
    
    try:
        LLM_annotated_response, gold_annotated_response, LLM_cards, gold_cards = AFA.extract_annotation_details(LLM_dict, gold_dict)
    except Exception as exp:
        new_row.append(full_LLM_response)
        print(f"An error occurred while attempting to extract the annotated response and feedback list: {str(exp)}.")
        data.append(new_row)
        continue
    
    new_row.append(LLM_annotated_response)
    new_row.append(gold_annotated_response)
    new_row.append(LLM_cards)
    new_row.append(gold_cards)
    
    try:
        LLM_TP_identified_confirmed, gold_common_identified_confirmed, number_of_identified_TP = AFA.identification_checker(LLM_annotated_response, gold_annotated_response, LLM_cards, gold_cards)
    except Exception as exp:
        print(f"An error occurred while attempting to identify the common errors: {str(exp)}.")
        pass
    
    new_row.append(LLM_TP_identified_confirmed)
    new_row.append(gold_common_identified_confirmed)
    
    try:
        categorisation_TP, number_of_categorised_TP = AFA.categorisation_checker(LLM_TP_identified_confirmed, gold_common_identified_confirmed, number_of_identified_TP)
    except Exception as exp:
        print(f"An error occurred while attempting to check the categories of the common errors: {str(exp)}.")
        categorisation_TP = list()
        number_of_identified_TP = len(LLM_TP_identified_confirmed)
        number_of_categorised_TP = len(categorisation_TP)
        pass

    new_row.append(categorisation_TP)
    new_row.append(number_of_identified_TP)
    new_row.append(number_of_categorised_TP)
    
    retrieved = len(LLM_cards)
    relevant = len(gold_cards)
    
    new_row.append(retrieved)
    new_row.append(relevant)
    
    try:
        identification_F05 = AFA.identificationF05Score(number_of_identified_TP, LLM_cards, gold_cards)
        new_row.append(identification_F05)
    except Exception as exp:
        print(f"An error occurred while attempting to calculate the identification F-0.5 score: {str(exp)}.")
        new_row.append("DivsionByZeroError")
        pass

    try:
        categorisation_F05 = AFA.categorisationF05Score(number_of_categorised_TP, LLM_cards, gold_cards)
        new_row.append(categorisation_F05)
    except Exception as exp:
        print(f"An error occurred while attempting to calculate the categorisation F-0.5 score: {str(exp)}.")
        new_row.append("DivsionByZeroError")
        pass
    
    #This is the end of the data extraction and calculation.
    data.append(new_row)

AFA.write_into_record(evaluation_record, data)