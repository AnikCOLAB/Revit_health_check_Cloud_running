import streamlit as st
import numpy as np
import re
import pandas as pd
import plotly.express as px

# ---------------- Helpers ---------------- #
unit_re = re.compile(r'^\s*([\d,.]+)\s*(KB|MB|GB)\s*$', re.I)
def to_mb(val):
    """
    Convert '7,416 KB' / '2.3 MB' / '1.5 GB' → float MB.
    Values lacking a KB/MB/GB unit become NaN.
    """
    if pd.isna(val):
        return np.nan

    m = unit_re.match(str(val))
    if not m:                     # no unit → NaN
        return np.nan

    num = float(m.group(1).replace(',', ''))
    unit = m.group(2).upper()

    if unit == 'KB':
        return num / 1000
    if unit == 'MB':
        return num
    if unit == 'GB':
        return num * 1000
    return np.nan


YEAR_RANGE = range(2022, 3000)          # 2022-2026 inclusive

def _safe_lookup(df, key, col_key=2, col_val=8):
    """
    Return the value in column `col_val` whose row in `col_key`
    matches `key`. If not found, replace the year and try 2022-2026.
    """
    # direct match first
    series = df.loc[df[col_key] == key, col_val]
    if not series.empty:
        return series.iloc[0]

    # strip any year and try the range
    base = re.sub(r'20\d{2}', '{yr}', key)          # e.g. "Total Model Elements Revit {yr}"
    for yr in YEAR_RANGE:
        alt_key = base.format(yr=yr)
        series = df.loc[df[col_key] == alt_key, col_val]
        if not series.empty:
            return series.iloc[0]

    # still nothing → NaN
    return np.nan

def custom_metric(title, value, delta_value=False, background_color="#FCFCFC", value_color="#000000", delta_color="#FF0000", arrow="&#x25B2;"):
    if delta_value:
        st.markdown(f"""
            <div class="metric-container", style="background:{background_color};">
                <div>
                    <div class="metric-title">{title}</div>
                    <div class="metric-value" style="color:{value_color};">{value}</div>
                    <div class="metric-delta" style="color:{delta_color};">{delta_value} <span style="color: gray;">{arrow}</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="metric-container", style="background:{background_color};">
                <div>
                    <div class="metric-title">{title}</div>
                    <div class="metric-value" style="color:{value_color};">{value}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True)
        

def mark_metric(df, standard_dict, list_item, title_item, variable=False, value_color= "#2E3D5E"):
    if not variable:
        raw_val = _safe_lookup(df, list_item)
        variable = np.nan if pd.isna(raw_val) else int(str(raw_val).replace(",", ""))
    consider_check = standard_dict[title_item].get("Consider", False)
    standard = standard_dict[title_item].get("Value", None)

    title = title_item
    value = variable
    delta_value = f"Goal: {standard}"


    if consider_check and (variable != int(standard)):
        if int(variable) > int(standard):
            background_color = "#FFEEEE"
            value_color = "#FF0000"

            custom_metric(title, value, delta_value, background_color, value_color)

        else:
            background_color = "#DCF1E8"
            value_color = "#005F33"
            delta_color = "#007740"

            custom_metric(title, value, delta_value, background_color=background_color, value_color=value_color, delta_color=delta_color, arrow="&#x25BC;")

    else:
        custom_metric(title, value, value_color= value_color)



def visulaization_mode(df, df_elements, standards):
    st.markdown("""
                <style>
                .metric-container {
                    margin:5px;
                    background-color: #f9f9f9; 
                    padding: 15px; 
                    border: 1px solid #CACACA;
                    border-radius: 10px; 
                    display: inline-block; 
                    text-align: center;
                    font-family: 'Arial', sans-serif;
                    display: flex;
                    flex-direction: row;
                    justify-content: center;
                    align-items: center;
                    gap: 50px;
                }
                .metric-title {
                    font-size: 15px; 
                    color: black;
                }
                .metric-value {
                    font-size: 28px; 
                    font-weight: bold; 
                    color: black;
                }
                .metric-delta {
                    font-size: 12px; 
                    color: red;
                }
                </style>
                """,
                unsafe_allow_html=True)
    
    genreral_statistic, performance_impacts, building_systems, family_size_breakthrough = st.columns([1,1,1.2,1.5])

    with genreral_statistic:
        with st.container(border=True):
            st.markdown('<h4 align = "center">General Statistics</h4>', unsafe_allow_html=True)

            genreral_statistic_title = ["Total Element Count", "Model Elements", "Annotative Elements", "Imported Raster Images",  "Linked DWGs", "Model Groups", "Detail Groups", "Design Options", "Number of Levels", "Number of Grid Lines"]
            genreral_statistic_list = ["Total Model Elements Revit 2024", "Elements Per Phase", "Total Annotative Elements Revit 2024", "Raster Images", "Linked CAD Files", "Model Groups", "Detail Groups", "Design Options", "Levels", "Grids"]
            
            size_cell = df.loc[df[2] == "File Size", 6].iloc[0] 
            mark_metric(df, standards["General Statistics"], None, "File Size", variable=size_cell)

            for count in range(len(genreral_statistic_list)):
                try:
                    if (count == 1) or (count == 5):
                        col1A, col2A = st.columns([1,1], gap="small")
                        with col1A:
                            mark_metric(df, standards["General Statistics"], genreral_statistic_list[count], genreral_statistic_title[count])
                        with col2A:
                            mark_metric(df, standards["General Statistics"], genreral_statistic_list[count+1], genreral_statistic_title[count+1])
                    
                    elif (count == 2) or (count == 6):
                        continue
                    
                    else:
                        mark_metric(df, standards["General Statistics"], genreral_statistic_list[count], genreral_statistic_title[count])
                except:
                    pass

            
    with performance_impacts:
        with st.container(border=True):
            st.markdown('<h4 align = "center">Performance Impacts</h4>', unsafe_allow_html=True)

            performance_impacts_title = ["Errors & Warnings", "Imported DWG & SKP", "Purgeable Elements", "Redundant and Unenclosed Rooms", "Unplaced Rooms", "Duplicate Modeled Elements", "Views Not On Sheets"]
            performance_impacts_list = ["Warnings", "Imported CAD files", "Purgeable Elements", "Redundant and Unenclosed Rooms", "Unplaced Rooms", "Duplicate Modeled Elements", "Views Not On Sheets"]
           

            for count in range(len(performance_impacts_list)):
                try:
                    mark_metric(df, standards["Performance Impacts"], performance_impacts_list[count], performance_impacts_title[count])
                except:
                    pass

    with building_systems:
        with st.container(border=True):
            st.markdown('<h4 align = "center">Elements Per workset</h4>', unsafe_allow_html=True)

            df_cat = (df_elements.groupby('Category', as_index=False)['Count'].sum().rename(columns={'Count': 'TotalCount'}).sort_values('TotalCount', ascending=False).head(12))
            st.dataframe(df_cat, hide_index=True)

        with st.container(border=True):
            st.markdown('<h4 align = "center">Building Systems</h4>', unsafe_allow_html=True)
            building_system_title = ["Unconnected Ducts", "Unconnected Pipe", "Unconnected Electrical", "Non-native Object Styles", "Mirrored Elements"]
            building_system_list = ["Duct Systems That Are Not Connected", "Piping Systems That Are Not Connected", "Electrical Systems That Are Not Connected", "Non built-in Object Styles", "Mirrored Elements"]

            for count in range(len(building_system_list)):
                try:
                    if (count == 0) or (count == 2):
                        col1A, col2A = st.columns([1,1], gap="small")
                        with col1A:
                            mark_metric(df, standards["Building Systems"], building_system_list[count], building_system_title[count])
                        with col2A:
                            mark_metric(df, standards["Building Systems"], building_system_list[count + 1], building_system_title[count + 1])
                    elif (count == 1) or (count == 3):
                        continue
                    
                    else:
                        mark_metric(df, standards["Building Systems"], building_system_list[count], building_system_title[count])
                except:
                    pass


    with family_size_breakthrough:
        genreral_statistic_color = "#129b00"
        with st.container(border=True):
            st.markdown('<h4 align = "center">File Size Breakthrough</h4>', unsafe_allow_html=True)

            # Process the dataframe
            df_elements['Value_MB'] = df_elements['Value'].apply(to_mb)
            df_elements['Count'] = pd.to_numeric(df_elements['Count'], errors='coerce')

            # FamilySize = Value_MB * Count  (leave NaN if either is NaN)
            df_elements['FamilySize'] = df_elements['Value_MB'] * df_elements['Count']

            # Total size across all families
            total_mb = df_elements['FamilySize'].sum()
            count_gt5 = (df_elements['FamilySize'] > 5).sum()
            count_2_5 = ((df_elements['FamilySize'] > 2) & (df_elements['FamilySize'] <= 5)).sum()
            count_1_2 = ((df_elements['FamilySize'] > 1) & (df_elements['FamilySize'] <= 2)).sum()
            count_lt1 = (df_elements['FamilySize'] <= 1).sum()

            with st.container(border=True, height=300):
                st.markdown('<h5 align = "center">Family Count by Size</h5>', unsafe_allow_html=True)
                # Pie chart
                sizes = [count_gt5, count_2_5, count_1_2, count_lt1]
                labels = ['> 5 MB', '2-5 MB', '1-2 MB', '< 1 MB']
                fig = px.pie(df, values=sizes, names=labels, hole=.3)
                fig.update_layout(height=300)
                st.plotly_chart(fig)


            family_size_title = ["Families over 5 MB", "In-Place Families", "Total MB of Families","Total Family Count", ]
            family_size_list = [count_gt5, "In-Place Families", total_mb, "Loadable Families"]

  
            for count in range(len(family_size_list)):
                try:
                    if (count == 0) or (count == 2):
                        col1A, col2A = st.columns([1,1], gap="small")
                        with col1A:
                            mark_metric(df, standards["File Size Breakthrough"], family_size_list[count], family_size_title[count], variable=family_size_list[count])
                        with col2A:
                            mark_metric(df, standards["File Size Breakthrough"], family_size_list[count + 1], family_size_title[count + 1])
                    elif (count == 1) or (count == 3):
                        continue
                except:
                    pass


            with st.container(border=True):
                family_count = standards["File Size Breakthrough"]["Largest Families"]["Value"]
                st.markdown(f'<h5 align = "center">{family_count} Largest Families</h5>', unsafe_allow_html=True)
                # ---------------- Sort & top‑12 ---------------- #
                df_sorted = df_elements.sort_values('FamilySize', ascending=False)
                df_top12 = df_sorted[['Name', 'FamilySize']].head(family_count)
                st.dataframe(df_top12, hide_index=True)
            

