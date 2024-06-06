import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title("School File Management System")
col1, col2, col3 = st.columns(3)

df1, df2 = None, None

# Read file section1
with col1:
    with st.expander("Read file"):
        read_file = st.file_uploader("Choose a file (CSV, Excel, or plain text):", type=["csv", "xlsx", "txt"])

        if st.button("Display Data", key="display_data_button"):
            if read_file is not None:
                if read_file.type == "text/plain":
                    text = read_file.read().decode("utf-8")
                    df1 = pd.DataFrame({"Text": [text]})
                elif read_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                    df1 = pd.read_excel(read_file)
                elif read_file.type == "text/csv":
                    df1 = pd.read_csv(read_file)

                with col2:
                    st.write("Read File:")
                    st.write(df1)




# Merge files and read section
with col1:
    with st.expander("Merge Files and Read"):
        uploaded_file1 = st.file_uploader("Choose the first file:", type=["csv", "xlsx", "txt"], key="file1")
        uploaded_file2 = st.file_uploader("Choose the second file:", type=["csv", "xlsx", "txt"], key="file2")

        merge_button_col, display_button_col = st.columns(2)

        if merge_button_col.button("Merge Files"):
            if uploaded_file1 is not None and uploaded_file2 is not None:
                if uploaded_file1.type == "text/plain":
                    text1 = uploaded_file1.read().decode("utf-8")
                    df1 = pd.DataFrame({"Text": [text1]})
                elif uploaded_file1.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                    df1 = pd.read_excel(uploaded_file1)
                elif uploaded_file1.type == "text/csv":
                    df1 = pd.read_csv(uploaded_file1)

                if uploaded_file2.type == "text/plain":
                    text2 = uploaded_file2.read().decode("utf-8")
                    df2 = pd.DataFrame({"Text": [text2]})
                elif uploaded_file2.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                    df2 = pd.read_excel(uploaded_file2)
                elif uploaded_file2.type == "text/csv":
                    df2 = pd.read_csv(uploaded_file2)

                if df1 is not None and df2 is not None:
                    merged_df = pd.concat([df1, df2], ignore_index=True)
                    st.session_state['merged_df'] = merged_df
                else:
                    st.write("Cannot merge the files")
            else:
                st.write("Please upload both files")

        if display_button_col.button("Display Merged Data"):
            st.session_state['display_merged'] = True

if 'merged_df' in st.session_state and st.session_state.get('display_merged', False):
    with col2:
        st.write("Merged and Read File:")
        st.write(st.session_state['merged_df'])

# Calculate average score section
if 'merged_df' in st.session_state:
    with col2:
        with st.expander("Summarize Student Performance"):
            id_input_col, button_col = st.columns([2, 1])
            student_id = id_input_col.text_input("Enter Student ID:")
            if button_col.button("Proceed"):
                merged_df = st.session_state['merged_df']
                if student_id:
                    try:
                        student_data = merged_df[merged_df['Id'] == int(student_id)]
                        if not student_data.empty:

                            student_name = student_data['Name'].iloc[0] if 'Name' in student_data.columns else "Name not found"
                            
                            numeric_cols = student_data.select_dtypes(include='number').columns.tolist()
                            if 'Id' in numeric_cols:
                                numeric_cols.remove('Id')
                            if numeric_cols:
                                average_score = student_data[numeric_cols].mean(axis=1).iloc[0]
                                highest_score = student_data[numeric_cols].max(axis=1).iloc[0]
                                top_course = student_data[numeric_cols].idxmax(axis=1).iloc[0]
                                lowest_score = student_data[numeric_cols].min(axis=1).iloc[0]
                                low_course = student_data[numeric_cols].idxmin(axis=1).iloc[0]
                                
                                with col3:
                                    st.markdown(f"<h3>{student_name}</h3>", unsafe_allow_html=True)
                                    st.write(f"Average Score: {average_score}<br>Top-performing course: {top_course} with score {highest_score}<br>Low-performing course: {low_course} with score {lowest_score}", unsafe_allow_html=True)
                                    
                                    fig, ax = plt.subplots()
                                    scores = student_data[numeric_cols].iloc[0]
                                    scores.plot(kind='bar', ax=ax, color=['red' if score == lowest_score else 'teal' if score == highest_score else 'grey' for score in scores])
                                    ax.set_title(f"Scores for Student ID {student_id}")
                                    ax.set_ylabel("Scores")
                                    st.pyplot(fig)

                                    performance = {}
                                    for course in numeric_cols:
                                        course_scores = merged_df[course].dropna()
                                        student_score = student_data[course].iloc[0]
                                        percentile = (np.sum(course_scores < student_score) / len(course_scores)) * 100
                                        performance[course] = percentile
                                    

                                    performance_lines = [
                                        f"{course}: score {student_data[course].iloc[0]}, better than {percentile:.2f}% of students"
                                        for course, percentile in performance.items()
                                    ]
                                    st.write(" <br>".join(performance_lines),unsafe_allow_html=True)


                                    avg_scores = merged_df.groupby('Id')[numeric_cols].mean().mean(axis=1)
                                    fig, ax = plt.subplots()
                                    ax.scatter(avg_scores.index, avg_scores.values, c='blue', label='Other Student')
                                    ax.scatter(int(student_id), average_score, c='red', label=f'{student_name}')
                                    ax.set_xlabel('Student ID')
                                    ax.set_ylabel('Average Score')
                                    ax.legend()
                                    st.pyplot(fig)
                            else:
                                st.write("No numeric columns found for averaging.")
                        else:
                            st.write("Student ID not found.")
                    except ValueError:
                        st.write("Please enter a valid numeric Student ID.")
                else:
                    st.write("Please enter a Student ID.")


if 'merged_df' in st.session_state:
    with col2:
        with st.expander("Grade Distribution"):
            id_input_col, button_col = st.columns([2, 1])
            course_name = id_input_col.text_input("Enter Course Name:")
            if button_col.button("Proceeed"):
                merged_df = st.session_state['merged_df']
                if course_name:
                    try:
                        course_data = merged_df[course_name]
                        if not course_data.empty:

                            course_data = course_data.dropna()
  
                            grade_ranges = {
                                'A+': (97, 100),
                                'A': (93, 96),
                                'A-': (90, 92),
                                'B+': (87, 89),
                                'B': (83, 86),
                                'B-': (80, 82),
                                'C+': (77, 79),
                                'C': (73, 76),
                                'C-': (70, 72),
                                'D+': (67, 69),
                                'D': (65, 66),
                                'D-': (0, 64)
                            }
                            grades = {grade: 0 for grade in grade_ranges}
                            for score in course_data:
                                for grade, (lower, upper) in grade_ranges.items():
                                    if lower <= score <= upper:
                                        grades[grade] += 1
                                        break

                            fig, ax = plt.subplots()
                            ax.pie(grades.values(), labels=grades.keys(), autopct='%1.1f%%')


                            with col3:
                                st.markdown(f"<h3>{course_name}</h3>", unsafe_allow_html=True)
                                st.pyplot(fig)
                        else:
                            st.write("No data found for the entered course name.")
                    except KeyError:
                        st.write("Course name not found")
                else:
                    st.write("Please enter a course name")
