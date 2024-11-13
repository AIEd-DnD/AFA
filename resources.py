base_prompt = """
<context>
You are a diligent teacher identifying errors in a {Level} student response to give them feedback on a {Subject} question: {Question}.
</context>

<objective>
Your objectives are:
1. Use the provided list of error tags, model answer or rubrics to carefully analyze the student's response.
3. Identify and return any errors found in the student response.
4. The feedback should follow the additional instructions: <Instructions>{Instructions}</Instructions>.
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

recipes = {"Default":"recipe 1 content",
           "recipe 2":"recipe 2 content",
           "recipe 3":"recipe 3 content",
           "recipe 4":"recipe 4 content",
           "recipe 5":"recipe 5 content",
           "recipe 6":"recipe 6 content",
           "recipe 7":"recipe 7 content",
           "recipe 8":"recipe 8 content",
           "recipe 9":"recipe 9 content"
           }

tools = [
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
]

biology_errors = """
Misconception of Process - Fundamental misunderstanding of the biological process (e.g., thinking photosynthesis occurs at night),  
Incomplete Explanation - Provides an incomplete or partial elaboration of a biological concept,  
Incorrect Sequence - Describes a biological process in the wrong order (e.g., incorrect stages of mitosis or meiosis),  
Lack of Specificity - Uses vague language or fails to specify key details (e.g., not mentioning ‘active transport’ when describing how ions move through membranes),  
Wrong Function - Assigns the wrong function to an organ, structure, or cell component (e.g., stating that the liver filters blood like the kidneys),  
Overgeneralization - Applies a concept too broadly (e.g., assuming all organisms undergo respiration the same way),  
Confusion Between Terms - Confuses two related but distinct biological terms (e.g., meiosis vs. mitosis, genotype vs. phenotype),  
Mislabeling - Mislabels a diagram, graph, or biological structure (e.g., labeling an artery as a vein in a circulatory system diagram),  
Wrong Unit of Measurement - Uses the wrong unit to express a biological quantity (e.g., using kilograms instead of grams for body mass),  
Misinterpretation of Graphs - Misreads or misinterprets data from a biological graph or chart (e.g., mixing up dependent and independent variables in experimental results),  
Incorrect Calculation - Makes an error in a biological calculation (e.g., calculating magnification incorrectly in microscopy),  
Incorrect Cause-Effect - Incorrectly explains the cause and effect in biological processes (e.g., stating that heart rate slows during exercise instead of increasing),  
Failure to Link Concepts - Fails to connect related concepts (e.g., not linking the role of enzymes to digestion in the stomach),  
Misunderstanding of Scale - Misunderstands biological scales (e.g., confusing cell sizes with organism sizes or misrepresenting the scale of ecosystems),  
Overcomplication - Provides an overly complex explanation where a simpler, more direct one is correct,  
Misidentification - Identifies the wrong species, tissue, or cell type in a question (e.g., confusing plant cells for animal cells in a diagram),  
Irrelevant Information - Includes irrelevant information that does not answer the question or address the biological concept,  
Incomplete Comparison - Makes an incomplete comparison between biological concepts (e.g., not fully explaining differences between aerobic and anaerobic respiration),  
Misuse of Terminology - Uses biological terminology incorrectly (e.g., using ‘diffusion’ instead of ‘osmosis’ in the context of water movement)
"""