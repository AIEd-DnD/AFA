import AFA_eval_functions as AFA
#import testbed_AFA_functions as AFA
#import resources as rsrc

data = list()
#test_name = input("Please enter the name of the test: ")               #uncomment this to unlock user input for test name
#file_path = input("Please enter the file path of the test data: ")     #uncomment this to unlock user input for file path
evaluation_record = AFA.start_new_record("4o_Joes_enhanced_prompts")
print("The refinement record has been created.")
response_list = AFA.csv_to_list_of_dicts("Dataset/AFA_BulkTagCheck_Complete.csv")
print("The response list has been created.")

for scenario_dict in response_list:
    new_row = list()
    subject, level, question, students_response, recipe, suggested_answer, rubrics, error_tags = AFA.extract_parameters_refinement(scenario_dict)
    #subject, level, question, students_response, recipe, error_tags = AFA.extract_parameters_refinement_Error_tags(scenario_dict)
    #subject, level, question, students_response, recipe, rubrics = AFA.extract_parameters_refinement_Rubrics(scenario_dict)
    #subject, level, question, students_response, recipe, suggested_answer = AFA.extract_parameters_refinement_SA(scenario_dict)

    new_row.append(subject)
    new_row.append(level)
    new_row.append(recipe)
    new_row.append(error_tags)
    new_row.append(suggested_answer)
    new_row.append(rubrics)
    new_row.append(question)
    new_row.append(students_response)
    
    print('Trying response '+str(response_list.index(scenario_dict)+1))
    
    #message = AFA.assemble_prompt(subject, level, question, students_response, recipe, suggested_answer, rubrics, error_tags)
    system_message = AFA.assemble_system_prompt(subject, level, question, recipe, suggested_answer, rubrics, error_tags)
    user_message = AFA.assemble_user_prompt(students_response)
    #message = AFA.assemble_prompt_Error_tags(subject, level, question, students_response, recipe, error_tags)
    #message = AFA.assemble_prompt_Rubrics(subject, level, question, students_response, recipe, rubrics)
    #message = AFA.assemble_prompt_SA(subject, level, question, students_response, recipe, suggested_answer)

    try:
        #full_LLM_response = AFA.get_annotations(message)
        full_LLM_response = AFA.get_annotations_system_user(system_message, user_message)
    except Exception as exp:
        new_row.append(user_message)
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
        new_row.append(LLM_annotated_response)
        new_row.append(LLM_cards)

        cleaned_text = AFA.strip_tags(LLM_annotated_response)
        if cleaned_text == students_response:
            Unmodified_Response = True
        else:
            Unmodified_Response = False

        number_of_cards = len(LLM_cards)

        open_tag_count = LLM_annotated_response.count('<tag id="')
        close_tag_count = LLM_annotated_response.count('</tag>')
        if open_tag_count == close_tag_count:
            tag_count_match = True
        else:
            tag_count_match = False

        if number_of_cards == close_tag_count:
            card_tag_match_status = True
        else:
            card_tag_match_status = False
        
        if '</tag>' in LLM_annotated_response:
            tagging_status = True
        else:
            tagging_status = False

        #if tagging_status is True and Unmodified_Response is True:
        new_row.append(tagging_status)
        new_row.append(Unmodified_Response)
        new_row.append(number_of_cards)
        new_row.append(open_tag_count)
        new_row.append(close_tag_count)
        new_row.append(tag_count_match)
        new_row.append(card_tag_match_status)

        for column in range(9):
            new_row.append(" ")
            
        if Unmodified_Response is True and card_tag_match_status is True and tag_count_match is True and number_of_cards != 0:
            display_status = "FULL"
        elif Unmodified_Response is True and card_tag_match_status is False and number_of_cards != 0 and open_tag_count != 0 and close_tag_count != 0:
            display_status = "PARTIAL"
        elif Unmodified_Response is False or number_of_cards == 0 or open_tag_count == 0 or close_tag_count == 0:
            display_status = "NIL"

        new_row.append(display_status)

        #elif tagging_status is False or Unmodified_Response is False:
            #print("No tags found or response has been modified. Pass through to second prompt")
            #new_row.append(tagging_status)
            #new_row.append(Unmodified_Response)
            #new_row.append(number_of_cards)
            #new_row.append(open_tag_count)
            #new_row.append(close_tag_count)
            #new_row.append(tag_count_match)
            #new_row.append(card_tag_match_status)

            #correction_prompt = AFA.assemble_AFA_JSON_evaluation_prompt(students_response, full_LLM_response)
            #correction_prompt = AFA.assemble_AFA_JSON_correction_prompt(full_LLM_response)
            
            #corrected_response = AFA.get_annotations(correction_prompt)
            #corrected_LLM_dict = AFA.string_to_dict(corrected_response)
            
            #corrected_LLM_annotated_response, corrected_LLM_cards = AFA.extract_annotation_details_refinement(corrected_LLM_dict)
            #if "</tag>" in corrected_LLM_annotated_response:
                #final_tagging_status = True
            #else:
                #final_tagging_status = False
            #new_row.append(corrected_LLM_annotated_response)
            #new_row.append(corrected_LLM_cards)
            #new_row.append(final_tagging_status)

            #corrected_cleaned_text = AFA.strip_tags(corrected_LLM_annotated_response)
            #if corrected_cleaned_text == students_response:
                #final_Unmodified_Response = True
            #else:
                #final_Unmodified_Response = False
            
            #final_number_of_cards = len(corrected_LLM_cards)
            #new_row.append(final_Unmodified_Response)
            #new_row.append(final_number_of_cards)

            #final_open_tag_count = corrected_LLM_annotated_response.count('<tag id="')
            #final_close_tag_count = corrected_LLM_annotated_response.count('</tag>')
            #if final_open_tag_count == final_close_tag_count:
                #final_tag_count_match = True
            #else:
                #final_tag_count_match = False

            #if final_number_of_cards == final_close_tag_count:
                #final_card_tag_match_status = True
            #else:
                #final_card_tag_match_status = False

            #new_row.append(final_open_tag_count)
            #new_row.append(final_close_tag_count)
            #new_row.append(final_tag_count_match)
            #new_row.append(final_card_tag_match_status)

            #if final_Unmodified_Response is True and final_card_tag_match_status is True and final_tag_count_match is True and final_number_of_cards != 0:
                #display_status = "FULL"
            #elif final_Unmodified_Response is True and final_card_tag_match_status is False and final_number_of_cards != 0 and final_open_tag_count != 0 and final_close_tag_count != 0:
             #   display_status = "PARTIAL"
            #elif final_Unmodified_Response is False or final_number_of_cards == 0 or final_open_tag_count == 0 or final_close_tag_count == 0:
             #   display_status = "NIL"

            #new_row.append(display_status)
        
    except Exception as exp:
        new_row.append(full_LLM_response)
        print(f"An error occurred while attempting to extract the annotated response and feedback list: {str(exp)}.")
        new_row.append("NIL")
        new_row.append(False)
        new_row.append(0)
        data.append(new_row)
        continue

    data.append(new_row)

AFA.write_into_record_refinement(evaluation_record, data)
#AFA.write_into_record_refinement_Error_tags(evaluation_record, data)
#AFA.write_into_record_refinement_Rubrics(evaluation_record, data)
#AFA.write_into_record_refinement_SA(evaluation_record, data)