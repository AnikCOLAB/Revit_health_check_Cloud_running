import os
import streamlit as st
from visualize import visulaization_mode
import pandas as pd
import io
import json
#Sets the name of the site

excel_file_name = "bestpractices-2024 Results 2025_05_08.xlsx"

st.set_page_config(page_title="Revit Health Check", layout="wide", initial_sidebar_state="collapsed")

if 'standards' not in st.session_state:
    with open("Standards.json", "r", encoding="utf-8") as f:
        standard_dict = json.load(f)
    st.session_state.standards = standard_dict

@st.cache_data(show_spinner=False)
def load_record(buf_or_path):
    my_bar = st.progress(0, text="Loading, Please wait!")
    # buf_or_path can be the ExcelBytes IO buffer or a file path
    dfs = {
        "files":    pd.read_excel(buf_or_path, "Files",    header=None),
        "checks":   pd.read_excel(buf_or_path, "Checks",   header=None),
        "elements": pd.read_excel(buf_or_path, "Elements"),
    }
    my_bar.progress(25, text="Reading 'Files' from the Record.")
    my_bar.progress(75, text="Reading 'Checks' from the Record.")
    my_bar.progress(100, text="Reading 'Elements' from the Record.")
    my_bar.empty()
    return dfs


def _clear_cache():
    st.cache_data.clear()


@st.dialog("Configure Standards", width="large")
def configure_standards():

    with st.expander("General Statistics", expanded=False):
        gs_df_standard = pd.DataFrame.from_dict(st.session_state.standards["General Statistics"], orient='index')
        gs_edited_df = st.data_editor(gs_df_standard, use_container_width=True)

    with st.expander("Performance Impacts", expanded=False):
        ps_df_standard = pd.DataFrame.from_dict(st.session_state.standards["Performance Impacts"], orient='index')
        ps_edited_df = st.data_editor(ps_df_standard, use_container_width=True)

    with st.expander("Building Systems", expanded=False):
        bs_df_standard = pd.DataFrame.from_dict(st.session_state.standards["Building Systems"], orient='index')
        bs_edited_df = st.data_editor(bs_df_standard, use_container_width=True)

    with st.expander("File Size Breakthrough", expanded=False):
        fs_df_standard = pd.DataFrame.from_dict(st.session_state.standards["File Size Breakthrough"], orient='index')
        fs_edited_df = st.data_editor(fs_df_standard, use_container_width=True)
      
    column_s1, column_S2 = st.columns([1,1])
    with column_s1:
        if st.button("Close & refresh", use_container_width=True):
            # update the session state standards
            st.session_state.standards["General Statistics"] = gs_edited_df.to_dict(orient='index')
            st.session_state.standards["Performance Impacts"] = ps_edited_df.to_dict(orient='index')
            st.session_state.standards["Building Systems"] = bs_edited_df.to_dict(orient='index')
            st.session_state.standards["File Size Breakthrough"] = fs_edited_df.to_dict(orient='index')
            st.rerun()
            
    with column_S2:
        st.download_button(use_container_width=True,
            label="Download Standards",
            data=json.dumps(st.session_state.standards, ensure_ascii=False, indent=2),
            file_name="Standards.json")
    uploaded_standard = st.file_uploader("Upload Standards", type=["json"], accept_multiple_files=False)
    if uploaded_standard is not None:
        try:
            standard_dict = json.load(uploaded_standard)
            st.session_state.standards = standard_dict
            st.success("Standards successfully loaded!")
            st.rerun()
        except Exception as e:
            st.error(f"Error loading Standards: {e}")

if "current_record" not in st.session_state:
    # default record on first load
    st.session_state.current_record = load_record(excel_file_name)

column_C1, column_C2= st.columns([6,1])
with column_C2:
    #change this one to your company logo
    st.image("images/mithun_logo.png")



with st.sidebar:
    st.header("Revit Health Check")

    temp_excel_sheet = st.file_uploader("Upload Temporary Report to check:")
    if temp_excel_sheet is not None:
        try:
            xls = pd.ExcelFile(temp_excel_sheet)
        except ValueError:
            st.error("Uploaded file isn't a readable Excel workbook.")

        buf = io.BytesIO(temp_excel_sheet.getvalue())
        st.session_state.current_record = load_record(buf)
        project_name = None
    else:
        st.session_state.current_record = load_record(excel_file_name)
        project_name = "Sample Project"

    if st.button("Configure Standards", use_container_width=True):
        configure_standards()
    st.text("Hit refresh to see changes")
    if st.button("Refresh", use_container_width=True):
        st.rerun()

    st.button("🧹  Clear cache",on_click=_clear_cache, help="Flush all cached reads and rerun the dashboard", use_container_width=True)


with column_C1:
    #sets the title of the page
    df_files = st.session_state.current_record["files"]
    if project_name is None:
        raw_project = df_files.iloc[1,1]
        s = str(raw_project).strip()
        base = os.path.basename(s)
        project_name = os.path.splitext(base)[0]

    st.header(project_name)
    report_date = df_files.iloc[1,0]
    st.text(f"Report date: {report_date}")




df_checks = st.session_state.current_record["checks"]

df_elements = st.session_state.current_record["elements"]

    
visulaization_mode(df_checks, df_elements, st.session_state.standards)

