import streamlit as st
import pandas as pd


def app():
    # Page Title
    st.title("⚙️ Teacher: Settings")

    st.subheader("🔖 Upload Error Tags")  # Title for the section

    # Column for CSV Upload without a label
    uploaded_file = st.file_uploader("Download the template csv file to fill in your error tags or choose from the prepared files. Reuploading will replace the existing tags.", type="csv")  # Empty string for no label

    if uploaded_file is not None:
        uploaded_data = pd.read_csv(uploaded_file)

        # Check for correct columns in uploaded CSV
        if set(uploaded_data.columns) == {"Error tag", "Description"}:
            # Create errors_dict from the uploaded data
            errors_dict = {row["Error tag"]: {"description": row["Description"]} for _, row in uploaded_data.iterrows()}

            # Store errors_dict in session state
            st.session_state.errors_dict = errors_dict

            # Display the uploaded data
            st.success("Data uploaded successfully!")
        else:
            st.error("The CSV file must contain 'Error tag' and 'Description' columns.")

    # Display current errors_dict from session state as a DataFrame if it exists
    if 'errors_dict' in st.session_state:
        st.markdown("### Current Error Tags")

        # Convert errors_dict to DataFrame
        errors_df = pd.DataFrame({
            "Error Tag": st.session_state.errors_dict.keys(),
            "Description": [value["description"] for value in st.session_state.errors_dict.values()]
        })

        # Display the DataFrame
        st.dataframe(errors_df, use_container_width=True)

    # Create an expandable accordion for the error tags download section
    with st.expander("📥 Try Our Error Tags", expanded=False):
        # Example file data for download
        # Replace with your actual data as needed
        specific_errors = {
            "template.csv": {
                "Error tag": [
                    "Error tag 1",
                    "Error tag 2",
                    "Error tag 3"
                ],
                "Description": [
                    "Description of error tag 1",
                    "Description of error tag 2",
                    "Description of error tag 3",
                ]
            },
            "argumentative_errors.csv": {
                "Error tag": [
                    "Did not address concerns",
                    "Illogical summary",
                    "Incoherent summary",
                    "Irrelevant evidence",
                    "Irrelevant topic",
                    "Lack of logical connectors",
                    "Lack of elaboration",
                    "Lack of evidence",
                    "Unfocused summary",
                    "Unfocused thesis",
                    "Overly narrow topic",
                    "Lack of commitment",
                    "No counterarguments",
                    "No reiteration of stand",
                    "No summary",
                    "Outdated topic",
                    "Weak audience connection",
                    "Weak counterargument",
                    "Poor introduction",
                    "Unclear thesis/stand"
                ],
                "Description": [
                    "Failed to anticipate or respond to potential reader questions, misunderstandings, or misinterpretations regarding the argument or content.",
                    "Presented a summary that does not logically follow from the argument or evidence discussed, showing errors in reasoning.",
                    "Presented a summary that lacks clarity, making it difficult to understand the main points or flow of the argument.",
                    "Provided examples or evidence that do not directly support or relate to the main argument or thesis.",
                    "Developed a thesis or argument that is off-topic or unrelated to the prompt or main subject of discussion.",
                    "Did not use appropriate transition words or phrases to show logical connections between different points or arguments.",
                    "Did not provide enough detail or explanation to fully develop the main idea or support the argument.",
                    "Did not provide examples, facts, or research to support the main argument or thesis.",
                    "The summary of the argument is scattered or unfocused, making it unclear what the main point is.",
                    "The thesis statement is too broad or vague, making it difficult to determine the specific point being argued.",
                    "The thesis or argument is too limited in scope, restricting the discussion or analysis.",
                    "Used weak or indecisive language that does not clearly express a strong position or stand on the issue being discussed.",
                    "Did not include or address opposing viewpoints, failing to present a balanced or comprehensive argument.",
                    "Did not restate the writer’s position or thesis at the conclusion, weakening the closing argument.",
                    "Did not provide a concluding summary of the key points discussed in the argument.",
                    "Discussed a topic that is no longer relevant or appropriate given the current context or prompt.",
                    "Did not engage the reader by using language or strategies to connect with the audience's concerns, values, or expectations.",
                    "Presented a counterargument that lacks strength or clarity, failing to challenge the opposing viewpoint effectively.",
                    "Did not provide sufficient context or an introduction to clearly set up the topic or argument being discussed.",
                    "The main argument or thesis is not clearly expressed, making it difficult to understand the writer’s position or focus."
                ]
            },
            "biology_errors.csv": {
                "Error tag": [
                    "Misconception of Process",
                    "Incomplete Explanation",
                    "Incorrect Sequence",
                    "Lack of Specificity",
                    "Wrong Function",
                    "Overgeneralization",
                    "Confusion Between Terms",
                    "Mislabeling",
                    "Wrong Unit of Measurement",
                    "Misinterpretation of Graphs",
                    "Incorrect Calculation",
                    "Incorrect Cause-Effect",
                    "Failure to Link Concepts",
                    "Misunderstanding of Scale",
                    "Overcomplication",
                    "Misidentification",
                    "Irrelevant Information",
                    "Incomplete Comparison",
                    "Misuse of Terminology"
                ],
                "Description": [
                    "Fundamental misunderstanding of the biological process (e.g., thinking photosynthesis occurs at night).",
                    "Provides an incomplete or partial elaboration of a biological concept.",
                    "Describes a biological process in the wrong order (e.g., incorrect stages of mitosis or meiosis).",
                    "Uses vague language or fails to specify key details (e.g., not mentioning ‘active transport’ when describing how ions move through membranes).",
                    "Assigns the wrong function to an organ, structure, or cell component (e.g., stating that the liver filters blood like the kidneys).",
                    "Applies a concept too broadly (e.g., assuming all organisms undergo respiration the same way).",
                    "Confuses two related but distinct biological terms (e.g., meiosis vs. mitosis, genotype vs. phenotype).",
                    "Mislabels a diagram, graph, or biological structure (e.g., labeling an artery as a vein in a circulatory system diagram).",
                    "Uses the wrong unit to express a biological quantity (e.g., using kilograms instead of grams for body mass).",
                    "Misreads or misinterprets data from a biological graph or chart (e.g., mixing up dependent and independent variables in experimental results).",
                    "Makes an error in a biological calculation (e.g., calculating magnification incorrectly in microscopy).",
                    "Incorrectly explains the cause and effect in biological processes (e.g., stating that heart rate slows during exercise instead of increasing).",
                    "Fails to connect related concepts (e.g., not linking the role of enzymes to digestion in the stomach).",
                    "Misunderstands biological scales (e.g., confusing cell sizes with organism sizes or misrepresenting the scale of ecosystems).",
                    "Provides an overly complex explanation where a simpler, more direct one is correct.",
                    "Identifies the wrong species, tissue, or cell type in a question (e.g., confusing plant cells for animal cells in a diagram).",
                    "Includes irrelevant information that does not answer the question or address the biological concept.",
                    "Makes an incomplete comparison between biological concepts (e.g., not fully explaining differences between aerobic and anaerobic respiration).",
                    "Uses biological terminology incorrectly (e.g., using ‘diffusion’ instead of ‘osmosis’ in the context of water movement)."
                ]
            }
        }

        for filename, data in specific_errors.items():
            # Convert specific error data to DataFrame
            specific_df = pd.DataFrame(data)

            # Create a download button for each specific CSV file
            specific_csv = specific_df.to_csv(index=False).encode('utf-8')  # Ensure UTF-8 encoding
            st.download_button(
                label=f"Download {filename}",
                data=specific_csv,
                file_name=filename,
                mime='text/csv'  # Correct MIME type for CSV
            )

    # Section for Suggested Answer
    st.subheader("💡 Add Suggested Answer")
    suggested_answer = st.text_area("Enter a suggested answer here:")

    # Save button for Suggested Answer
    if st.button("Save"):
        st.session_state.suggested_answer = suggested_answer  # Save the suggested answer in session state
        st.session_state.suggested_answer_saved = True  # Indicate that the answer has been saved
    if 'suggested_answer_saved' in st.session_state and st.session_state.suggested_answer_saved:
        st.success("Suggested Answer Saved Successfully!")
