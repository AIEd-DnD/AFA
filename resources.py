base_prompt = """
<context>
You are a diligent teacher identifying errors in a {Level} student response to give them feedback on a {Subject} question: {Question}.
</context>

<objective>
Your objectives are:
1. Use the provided list of error tags, model answer or rubrics to carefully analyze the student's response.
3. Identify and return any errors found in the student response.
4. The feedback should follow the additional instructions: {Instructions}.
</objective>


Teacher's model answer: {Model_answer}

Rubrics: 
Marks should be allocated by rubrics(if any) or the marking scheme below.
{Rubrics}


You are to perform the following:

a) Return the student's response exactly as sent, in addition, look out for this list of error types. 

{Error_types}

For each error, return the student’s response and enclose the words or phrases and return with a unique tag and a running number to the tag. Eg. <tag id=”1”></tag>, <tag id=”2”></tag>, etc.

For each error type, specify the unique tag and the id of the tag, and list out what error type it is and comments on each error type. For the comments, in the question's language, provide feedback directly to the student in a way suitable for his level focusing on accuracy, areas for growth, and improvement steps, highlighting strengths. Focus on response accuracy, content mastery, and areas for growth. Do not use a third person perspective, share your feedback directly.

If there are no errors, the error tag should tag the first word of the student's response and the error tag should be "No error".



This is the student's response: {Students_response}

"""

tools = """
  {
        "type": "function",
        "function": {
            "name": "get_marks_feedback_and_rubrics",
            "description": "Use the provided list of error tags, suggested answer or rubrics to carefully analyze the student's response and return feedback in a list format with the properties required in a JSON object",
            "parameters": {
                "type": "object",
                "properties": {
                  "annotated_response" : {
                    "type": "string",
                    "description": "student’s response and enclose the words or phrases and return with a unique tag and a running number to the tag."
                  },
                  "feedback_list": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "id": {
                          "type": "integer",
                          "description": "tag id"
                        },
                        "phrase": {
                          "type": "string",
                          "description": "the specific part of the sentence containing an error"
                        },
                        "error_tag": {
                          "type": "array",
                          "items": {
                            "type": "object",
                            "properties": {
                                "errorType": {
                                    "type": "string",
                                    "description": "error type"
                                }
                            }
                          },
                          "description": "list of concise error category based on error types"
                        },
                        "comment": {
                          "type": "string",
                          "description": "a concise student-friendly explanation or suggestion"
                        }
                      }
                    }
                  }
                },
                "required": [
                  "feedback_list"
                ]
            }
        }
      }

"""