


def dashboard():
    """
    If df_growth then init page with selected from Search page data
    else init the whole page.
    """

    import streamlit as st
    st.set_page_config(page_title="Visualization Dashboard", layout='wide')


    print("session state in dashboard:",st.session_state)


    import pandas as pd
    import altair as alt
    import plotly.express as px
    from streamlit_extras.app_logo import add_logo
    import streamlit.components.v1 as components
    import sys
    import os
    from scripts.filter_df import filter_dict_states

    current_dir = os.path.dirname(os.path.realpath(__file__))[:-9]
    relative_path_to_src = os.path.join(current_dir, 'src')

    sys.path.append(relative_path_to_src)
    from db_functions import getExperiments
    from parse_raw_data import save_data_to_csv
    

    add_logo("figs/logo_sidebar2.png", height=100)
    with open("style.css") as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

    df_growth = pd.DataFrame()
    df_reads = pd.DataFrame()

    conn = st.connection("BacterialGrowth", type="sql")

    st.title("Visualizing Study Data")


    # temporar
    if "to_dashboard" in st.session_state and st.session_state["to_dashboard"] != "":
        studyID_to_visualize = str(st.session_state["to_dashboard"])
    else:
        studyID_to_visualize = None

    if  "df_growth" not in st.session_state:
        st.session_state['df_growth'] = None

    if  "df_reads" not in st.session_state:
        st.session_state['df_reads'] = None

    data = None
    col1, col2 = st.columns([0.94, 0.06])

    if studyID_to_visualize is None:

        with col1:
            no_button = True
            studyID_to_visualize = st.text_input(
                label = "Study ID",
                placeholder="Enter the Study ID you want to visualize its data",
                help="Enter only numerical values"
                )
            if studyID_to_visualize != None:
                no_button = False


        with col2:
            st.write("")
            st.write("")
            go_button = st.button("Go!",type = "primary",disabled=no_button)


    if studyID_to_visualize != None or go_button:

        print(studyID_to_visualize)
        print(type(studyID_to_visualize))
        print("===================")
        path = relative_path_to_src + f"/Data/Growth/{studyID_to_visualize}"
        growth_file = path + f"/Growth_Metabolites.csv"
        reads_file = path + f"/Sequencing_Reads.csv"


        try:
            df_growth = pd.read_csv(growth_file)
            subset_columns = df_growth.columns.drop('Position')
            # Drop rows where all values are NaN
            df_growth = df_growth.dropna(subset=subset_columns, how='all')
            st.session_state['df_growth'] = 0
        except FileNotFoundError:
            df_growth = pd.DataFrame()

        try:
            df_reads = pd.read_csv(reads_file)
            st.session_state['df_reads'] = 0
        except FileNotFoundError:
            df_reads = pd.DataFrame()


    return df_growth, df_reads, studyID_to_visualize, conn

def content(df_growth, df_reads, studyID_to_visualize, conn):
    import streamlit as st
    import pandas as pd
    import altair as alt
    import plotly.express as px
    from streamlit_extras.app_logo import add_logo
    import streamlit.components.v1 as components
    import sys
    import os
    from scripts.filter_df import filter_dict_states

    current_dir = os.path.dirname(os.path.realpath(__file__))[:-9]
    relative_path_to_src = os.path.join(current_dir, 'src')

    sys.path.append(relative_path_to_src)
    from db_functions import getExperiments

    print("session state in dashboard:",st.session_state)

    checkbox_states = {}

    #col1, col2, col3 = st.columns([0.25, 0.70, 0.5])
    #with col2:
    #    if not df_growth.empty :
    #        st.dataframe(df_growth)
    #    if not df_reads.empty:
    #        st.dataframe(df_growth)
    with col1:
        st.subheader("Experiments")

    if not df_growth.empty or not df_reads.empty:
        with col1:
            if not df_growth.empty:
                df_experiments = getExperiments(studyID_to_visualize, conn)
                for i, j, k in zip(df_experiments["experimentId"], df_experiments["experimentDescription"],  df_experiments["bioreplicateIds"]):
                    with st.expander(f"{i}"):
                        st.write(f"{j}")
                        biorep_list = k.split(",")
                        for rep in biorep_list:
                            checkbox_key = f"checkbox{i}:biologicalreplicate:{rep}"
                            checkbox_states[checkbox_key] = st.checkbox(f"{rep}", key=checkbox_key, value=checkbox_states.get(checkbox_key, False))
            else:
                st.warning("Study does not contain growth data")

            
        experiment_with_bioreps = filter_dict_states(st.session_state)
        return df_growth,experiment_with_bioreps
    
def tabs_plots(df_growth,experiment_with_bioreps):
    import streamlit as st
    import pandas as pd
    import altair as alt
    import plotly.express as px
    from streamlit_extras.app_logo import add_logo
    import streamlit.components.v1 as components
    from scripts.filter_df import filter_df
    import sys
    import os
    import numpy as np
    from scripts.filter_df import filter_dict_states

    current_dir = os.path.dirname(os.path.realpath(__file__))[:-9]
    relative_path_to_src = os.path.join(current_dir, 'src')

    sys.path.append(relative_path_to_src)
    from db_functions import getExperiments

    with col2:
        result_growth_df_dict, result_reads_df_dict = filter_df(experiment_with_bioreps,df_growth,df_reads)
        #print(result_growth_df_dict)
        #print(result_reads_df_dict)
        tab1, tab2, tab3, tab4, tab5,tab6 = st.tabs(["OD", "Plate Counts","pH","FC Counts","Reads 16S rRNA Seq","Metabolites"])
        css = '''
        <style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size:1.5rem;
            font-weight: bold;
            }
        </style>
        '''
        st.markdown(css, unsafe_allow_html=True)

        with tab1:
            for exp, growth_df in result_growth_df_dict.items():
                if 'OD' in growth_df.columns:
                    with st.expander(f"**OD Data for Experiment: {exp}**"):
                        st.dataframe(growth_df[["Biological_Replicate_id","Time","OD"]])
                    fig = px.line(growth_df, x='Time', y='OD',color='Biological_Replicate_id' ,title=f'OD Plot for Experiment: {exp} per Biological replicates',
                                  labels={
                                        'Time': 'Hours',
                                    },
                                    markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("The Biological Replicate ID selected do not contain OD data")
        with tab2:
            for exp, growth_df in result_growth_df_dict.items():
                if 'Plate_counts' in growth_df.columns:
                    with st.expander(f"**Plate Counts: {exp}**"):
                        st.dataframe(growth_df[["Biological_Replicate_id","Time","Plate_counts"]])
                    fig = px.line(growth_df, x='Time', y='Plate_counts',color='Biological_Replicate_id' ,title=f'Plate Counts for Experiment: {exp} per Biological replicates')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("The Biological Replicate IDs selected do not contain Plate Counts data")
        with tab3:
            for exp, growth_df in result_growth_df_dict.items():
                if 'pH' in growth_df.columns:
                    with st.expander(f"**pH: {exp}**"):
                        st.dataframe(growth_df[["Biological_Replicate_id","Time","pH"]])
                    fig = px.line(growth_df, x='Time', y='pH',color='Biological_Replicate_id' ,title=f'pH for Experiment: {exp} per Biological replicates')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("The Biological Replicate IDs selected do not contain pH data")
        with tab4:
            for exp, growth_df in result_growth_df_dict.items():
                if 'FC' in growth_df.columns:
                    with st.expander(f"**FC: {exp}**"):
                        st.dataframe(growth_df[["Biological_Replicate_id","Time","FC"]])
                    
                    fig = px.line(growth_df, x='Time', y='FC',color='Biological_Replicate_id' ,title=f'FC counts for Experiment: {exp} per Biological replicates',
                                  labels={
                                        'Time': 'Hours',
                                        'FC': 'Cells/mL',
                                    },
                                    markers=True)
                    st.plotly_chart(fig, use_container_width=True)

            for exp, reads_df in result_reads_df_dict.items():
                counts_col = [col for col in reads_df.columns if not col.endswith('_reads')]
                if counts_col:
                    with st.expander(f"**FC counts per Species: {exp}**"):
                        st.dataframe(reads_df)
                    unique_biorep_ids = reads_df['Biological_Replicate_id'].unique()
                    for biorepID in unique_biorep_ids:
                        filtered_per_biorep_df = reads_df[reads_df['Biological_Replicate_id'] == biorepID]
                        #non_nan_columns = filtered_per_biorep_df.columns[filtered_per_biorep_df.notna().any()].tolist()
                        filtered_per_biorep_df = filtered_per_biorep_df.dropna(axis=1,how='all')
                        species_columns = filtered_per_biorep_df.filter(like='_counts').columns

                        melted_df = filtered_per_biorep_df.melt(id_vars=['Time', 'Biological_Replicate_id'],
                                    value_vars=species_columns,
                                    var_name='Species', value_name='Cells/mL')
                        melted_df['Log_Cells/mL'] = np.log10(melted_df['Cells/mL'])
                        on = st.toggle("Apply Log", key=f"toogle_FC_{biorepID}")
                        if on:
                            fig = px.line(melted_df, x='Time', y='Log_Cells/mL',color='Species' ,title=f'FC Counts: {biorepID} per Microbial Strain',
                                            labels={
                                            'Time': 'Hours',
                                        },
                                        markers=True)
                        else:
                            fig = px.line(melted_df, x='Time', y='Cells/mL',color='Species' ,title=f'FC Counts: {biorepID} per Microbial Strain',
                                            labels={
                                            'Time': 'Hours',
                                        },
                                        markers=True)
                        st.plotly_chart(fig, use_container_width=True)

                #else:
                #    st.warning("The Biological Replicate IDs selected do not contain FC data")
                
        with tab5:
            for exp, reads_df in result_reads_df_dict.items():
                reads_col = [col for col in reads_df.columns if not col.endswith('_reads')]
                if reads_col:
                    with st.expander(f"**16S rRNA Sequencing: {exp}**"):
                        st.dataframe(reads_df)
                    unique_biorep_ids = reads_df['Biological_Replicate_id'].unique()
                    for biorepID in unique_biorep_ids:
                        filtered_per_biorep_df = reads_df[reads_df['Biological_Replicate_id'] == biorepID]
                        species_columns = filtered_per_biorep_df.filter(like='_reads').columns
                        melted_df = filtered_per_biorep_df.melt(id_vars=['Time', 'Biological_Replicate_id'],
                                value_vars=species_columns,
                                var_name='Species', value_name='Cells/mL')
                        melted_df['Log_Cells/mL'] = np.log10(melted_df['Cells/mL'])
                        on = st.toggle("Apply Log", key=f"toogle_{biorepID}")
                        if on:
                            fig = px.line(melted_df, x='Time', y='Log_Cells/mL',color='Species' ,title=f'16S rRNA Sequencing Counts: {biorepID} per Microbial Strain',
                                        labels={
                                        'Time': 'Hours',
                                    },
                                    markers=True)
                        else:
                            fig = px.line(melted_df, x='Time', y='Cells/mL',color='Species' ,title=f'16S rRNA Sequencing Counts: {biorepID} per Microbial Strain',
                                          labels={
                                        'Time': 'Hours',
                                    },
                                    markers=True)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("The Biological Replicate IDs selected do not contain 16S rRNA Sequencing data")

        with tab6:
            for exp, growth_df in result_growth_df_dict.items():
                columns_to_keep = [col for col in growth_df.columns if not col.endswith('_std') and col not in ["Biological_Replicate_id", "Time", "FC", "OD","Plate_counts","Position","pH"]]
                if columns_to_keep:
                    with st.expander(f"**Metabolites: {exp}**"):
                        st.dataframe(growth_df)
                    unique_biorep_ids = growth_df['Biological_Replicate_id'].unique()
                    for biorepID in unique_biorep_ids:
                        filtered_per_biorep_df = growth_df[growth_df['Biological_Replicate_id'] == biorepID]
                        #non_nan_columns = filtered_per_biorep_df.columns[filtered_per_biorep_df.notna().any()].tolist()
                        filtered_per_biorep_df = filtered_per_biorep_df.dropna(axis=1, how='all')
                        metabolites_columns = filtered_per_biorep_df.filter(columns_to_keep).columns
                        melted_df = filtered_per_biorep_df.melt(id_vars=['Time', 'Biological_Replicate_id'],
                                value_vars=metabolites_columns,
                                var_name='Metabolites', value_name='mM')
                        print(melted_df.head())
                        fig = px.line(melted_df, x='Time', y='mM',color='Metabolites',title=f'Metabolites Concentrations: {biorepID} per Metabolite',
                                      labels={
                                        'Time': 'Hours',
                                    },
                                    markers=True)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("The Biological Replicate IDs selected do not contain Metabolite data")











if __name__ == "__main__":
    import streamlit as st
    df_growth, df_reads, studyID_to_visualize, conn = dashboard()
    col1, col2 = st.columns([0.35, 0.65])
    df_growth,experiment_with_bioreps=content(df_growth, df_reads, studyID_to_visualize, conn)
    print(experiment_with_bioreps)
    tabs_plots(df_growth,experiment_with_bioreps)
    #content(df_growth, df_reads, studyID_to_visualize, conn)
