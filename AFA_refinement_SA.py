import testbed_AFA_functions as AFA

data = list()
#test_name = input("Please enter the name of the test: ")               #uncomment this to unlock user input for test name
#file_path = input("Please enter the file path of the test data: ")     #uncomment this to unlock user input for file path
evaluation_record = AFA.start_new_record("4o_SA_expanded_v2_system_user")
print("The refinement record has been created.")
response_list = AFA.csv_to_list_of_dicts("Dataset/AFA_Bulk_SA.csv")
print("The response list has been created.")

for scenario_dict in response_list:
    new_row = list()
    subject, level, question, students_response, recipe, suggested_answer = AFA.extract_parameters_refinement_SA(scenario_dict)
    
    new_row.append(subject)
    new_row.append(level)
    new_row.append(recipe)
    new_row.append(suggested_answer)
    new_row.append(question)
    new_row.append(students_response)
    
    print('Trying response '+str(response_list.index(scenario_dict)+1))
    
    #message = AFA.assemble_prompt_SA(subject, level, question, students_response, recipe, suggested_answer)
    system_message = AFA.assemble_SA_system_prompt(subject, level, question, recipe, suggested_answer)
    user_message = AFA.assemble_user_prompt(students_response)
    try:
        #full_LLM_response = AFA.get_annotations(message)
        full_LLM_response = AFA.get_annotations_system_user(system_message, user_message)
    except Exception as exp:
        new_row.append(message)
        print(f"An error occurred while attempting to receive the message from OpenAI: {str(exp)}.")
        new_row.append("NIL")
        new_row.append(False)
        new_row.append(0)
        data.append(new_row)
        continue
    
    try:
        LLM_dict = AFA.string_to_dict(full_LLM_response)
    except Exception as exp:
        new_row.append(full_LLM_response)
        print(f"An error occurred while attempting to convert the LLM response into a dictionary: {str(exp)}.")
        new_row.append("NIL")
        new_row.append(False)
        new_row.append(0)
        data.append(new_row)
        continue

    try:
        LLM_annotated_response, LLM_cards = AFA.extract_annotation_details_refinement(LLM_dict)
        if '</tag>' in LLM_annotated_response:
            status = True
        else:
            status = False
        number_of_cards = len(LLM_cards)
    except Exception as exp:
        new_row.append(full_LLM_response)
        print(f"An error occurred while attempting to extract the annotated response and feedback list: {str(exp)}.")
        new_row.append("NIL")
        new_row.append(False)
        new_row.append(0)
        data.append(new_row)
        continue
    
    new_row.append(LLM_annotated_response)
    new_row.append(LLM_cards)
    new_row.append(status)
    new_row.append(number_of_cards)

    data.append(new_row)

AFA.write_into_record_refinement_SA(evaluation_record, data)