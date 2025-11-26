import streamlit as st
import pandas as pd
import plotly.express as px
import ast

# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Global Data Explorer",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ---------------------------------------------------------
# 2. ROBUST NAME MAPPING (THE FIX)
# ---------------------------------------------------------
def get_csv_to_plotly_map():
    """
    Maps common CSV country names to the formal names expected by Plotly's Natural Earth map.
    Format: 'Name in your CSV': 'Name Plotly Wants'
    """
    return {
        'United States': 'United States of America',
        'USA': 'United States of America',
        'US': 'United States of America',
        'Russia': 'Russian Federation',
        'Iran': 'Iran (Islamic Republic of)',
        'South Korea': 'Korea, Republic of',
        'Korea, Rep.': 'Korea, Republic of',
        'North Korea': "Korea, Democratic People's Republic of",
        'Vietnam': 'Viet Nam',
        'Venezuela': 'Venezuela (Bolivarian Republic of)',
        'Bolivia': 'Bolivia (Plurinational State of)',
        'Syria': 'Syrian Arab Republic',
        'Moldova': 'Moldova, Republic of',
        'Tanzania': 'Tanzania, United Republic of',
        'Democratic Republic of the Congo': 'Congo, Democratic Republic of the',
        'Congo, Dem. Rep.': 'Congo, Democratic Republic of the',
        'Republic of the Congo': 'Congo',
        'Congo, Rep.': 'Congo',
        'Laos': "Lao People's Democratic Republic",
        'Lao PDR': "Lao People's Democratic Republic",
        'Brunei': 'Brunei Darussalam',
        'Ivory Coast': "Côte d'Ivoire",
        'Eswatini': 'Eswatini',
        'Czech Republic': 'Czechia',
        'Turkey': 'Türkiye',
        'Palestine': 'Palestine, State of',
        'Taiwan': 'Taiwan, Province of China'
    }


# ---------------------------------------------------------
# 3. DATA PROCESSING
# ---------------------------------------------------------
@st.cache_data
def load_and_process_data():
    file_path = 'row_31_compact_grouped_final.csv'

    try:
        raw_df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return pd.DataFrame()

    # Clean whitespace from column names and country names
    raw_df.columns = raw_df.columns.str.strip()
    if 'country' in raw_df.columns:
        raw_df['country'] = raw_df['country'].astype(str).str.strip()

    processed_rows = []
    # Identify metric columns (exclude non-metrics)
    metric_cols = [c for c in raw_df.columns if c not in ['country', 'year']]

    for _, row in raw_df.iterrows():
        country_csv_name = row['country']

        # Safe parsing of year array
        try:
            years = ast.literal_eval(row['year'])
            if not isinstance(years, list): continue
        except:
            continue

        parsed_metrics = {}
        valid_row = True

        for col in metric_cols:
            try:
                val_list = ast.literal_eval(row[col])
                # Handle single values or lists
                if not isinstance(val_list, list):
                    val_list = [val_list] * len(years)

                # Sync length with years
                if len(val_list) > len(years):
                    val_list = val_list[:len(years)]
                elif len(val_list) < len(years):
                    val_list = val_list + [None] * (len(years) - len(val_list))

                parsed_metrics[col] = val_list
            except:
                # If parsing fails, fill with Nones
                parsed_metrics[col] = [None] * len(years)

        if not valid_row:
            continue

        # Expand to long format
        for i, year in enumerate(years):
            new_record = {'country': country_csv_name, 'year': year}
            for col in metric_cols:
                new_record[col] = parsed_metrics[col][i]
            processed_rows.append(new_record)

    df_clean = pd.DataFrame(processed_rows)

    # --- APPLY NAME MAPPING FOR MAPPING COLUMN ---
    # We create a separate column 'map_location' for Plotly to use,
    # while keeping 'country' as the original CSV name for data lookup.
    name_mapper = get_csv_to_plotly_map()

    # Default to original name, override if in mapper
    df_clean['map_location'] = df_clean['country'].apply(lambda x: name_mapper.get(x, x))

    return df_clean


# Load Data
df = load_and_process_data()

if df.empty:
    st.stop()

# Initialize Session State (Use CSV names here)
if 'selected_countries' not in st.session_state:
    # Try to pick defaults that actually exist in the file
    available = df['country'].unique()
    defaults = []
    if 'United States' in available:
        defaults.append('United States')
    elif 'USA' in available:
        defaults.append('USA')
    if 'China' in available: defaults.append('China')

    st.session_state.selected_countries = defaults if defaults else list(available[:2])


# ---------------------------------------------------------
# 4. INTERACTION LOGIC
# ---------------------------------------------------------
def update_selection(new_selection):
    if not new_selection:
        return

    # The click returns the 'location' we passed to Plotly (The Formal Name)
    clicked_map_name = new_selection[0]['location']

    # We need to find which CSV country this corresponds to
    # 1. Check if it's directly in our dataframe's map_location column
    matched_rows = df[df['map_location'] == clicked_map_name]

    if not matched_rows.empty:
        # Found it! Get the original CSV name
        csv_name = matched_rows.iloc[0]['country']
    else:
        # If not found, it might be a country we don't have data for,
        # or a mismatch we missed. Try reverse mapping just in case.
        csv_to_plotly = get_csv_to_plotly_map()
        plotly_to_csv = {v: k for k, v in csv_to_plotly.items()}
        csv_name = plotly_to_csv.get(clicked_map_name, clicked_map_name)

    # Check if this CSV name actually exists in our data
    if csv_name not in df['country'].unique():
        st.toast(f"No data available for {clicked_map_name}", icon="⚠️")
        return

    # Update State
    current_list = st.session_state.selected_countries
    if csv_name in current_list:
        st.session_state.selected_countries.remove(csv_name)
    else:
        st.session_state.selected_countries.append(csv_name)


def format_metric_name(name):
    return name.replace('_', ' ').title()


# ---------------------------------------------------------
# 5. UI LAYOUT
# ---------------------------------------------------------
st.title("Country Development")

col_map, col_panel = st.columns([1, 1])

# --- LEFT: MAP ---
with col_map:
    available_metrics = [c for c in df.columns if c not in ['country', 'year', 'map_location']]
    default_metric = 'sdg_index_score' if 'sdg_index_score' in available_metrics else available_metrics[0]

    latest_year = df['year'].max()

    # Prepare Map Data
    # We use map_location for the geometry matching
    map_data = df[df['year'] == latest_year].drop_duplicates(subset=['country']).copy()

    map_data['Selection'] = map_data['country'].apply(
        lambda x: x if x in st.session_state.selected_countries else 'Available'
    )
    n_colors = len(map_data.country.unique())
    colorscale = colors = px.colors.sample_colorscale("viridis", [n/(n_colors -1) for n in range(n_colors)])
    colordict = {f:colorscale[i] for i, f in enumerate(map_data.country.unique())}
    colordict.update({'Available': '#E2E2E2'})

    color_map = {'Selected': '#FF4B4B', 'Available': '#E2E2E2'}

    fig_map = px.choropleth(
        map_data,
        locations="map_location",  # VITAL: Use the formal name column
        locationmode="country names",
        color="Selection",
        color_discrete_map=colordict,
        hover_name="country",  # VITAL: Show the familiar CSV name on hover
        hover_data={"Selection": False, "map_location": False, default_metric: True},
        projection="natural earth"
    )

    fig_map.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=450,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#FFFFFF",
            showland=True,
            landcolor="#f4f4f4",
            countrycolor="white",
            bgcolor='rgba(0,0,0,0)'
        ),
        clickmode='event+select',
        showlegend=False
    )

    event = st.plotly_chart(
        fig_map,
        on_select="rerun",
        selection_mode="points",
        use_container_width=True,
        key="map_chart"
    )

    if event and event.get("selection") and event["selection"]["points"]:
        update_selection(event["selection"]["points"])
        st.rerun()

# --- RIGHT: PANEL ---
with col_panel:
    current_selection = st.session_state.selected_countries

    if not current_selection:
        st.info("Click a country on the map.")
    else:
        # Metric Selector
        metric_map = {format_metric_name(c): c for c in available_metrics}


        selected_display = st.multiselect("Metric:", options=list(metric_map.keys()))
        selected_col = [metric for metric in available_metrics if format_metric_name(metric) in selected_display]

        st.divider()

        # Tags
        st.markdown("**Selected:**")
        st.markdown(", ".join([f"`{c}`" for c in current_selection]))

        # Filter
        filtered_df = df[df['country'].isin(current_selection)]
        filtered_df['Selection'] = filtered_df['country'].apply(
            lambda x: x if x in st.session_state.selected_countries else 'Available'
        )

        if filtered_df.empty:
            st.warning("No data for selection.")
        else:
            if(len(selected_col) == 1):
                # Line Chart
                line_chart = px.line(
                    filtered_df,
                    x='year',
                    y=selected_col[0],
                    color='country',
                    color_discrete_map=colordict,
                    markers=True,
                    title=f"{selected_display[0]}",
                    template="plotly_white",
                    range_y=[0,100]
                )

                line_chart.update_layout(
                    legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=50),
                    xaxis_title=None,
                    yaxis_title=None,
                    xaxis = dict(
                        rangeslider=dict(
                            visible=True
                        ),
                        type="date"
                    ),
                    dragmode='select'
                )

                st.plotly_chart(line_chart, use_container_width=True)
            elif(len(selected_col) == 2):
                # Scatter Plot
                scatter_plot = px.scatter(
                    filtered_df,
                    x = selected_col[0],
                    y = selected_col[1],
                    color = "country",
                    color_discrete_map=colordict,
                    title = f"{selected_display[1]} vs. {selected_display[0]}",
                    template="plotly_white",
                    animation_frame = "year",
                    animation_group = "country",
                    hover_name = "country",
                    range_x=[0,100],
                    range_y=[0,100]
                )
                scatter_plot.update_layout(
                    legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=50),
                    xaxis_title=f"{selected_display[0]}",
                    yaxis_title=f"{selected_display[1]}",
                    dragmode='select'
                )
                scatter_plot["layout"].pop("updatemenus")
                st.plotly_chart(scatter_plot, use_container_width=True)
            elif(len(selected_col) < len(available_metrics)):
                smop = px.scatter_matrix(
                    filtered_df, 
                    dimensions=selected_col,
                    color="country",
                    color_discrete_map=colordict,
                    template="plotly_white",
                    hover_name = "country"
                )
                smop.update_traces(
                    showupperhalf=False,
                    diagonal_visible=False
                )
                st.plotly_chart(smop, use_container_width=True)
            elif(len(selected_col) == len(available_metrics)):
                smop = px.scatter_matrix(
                    filtered_df, 
                    dimensions=selected_col,
                    color="country",
                    color_discrete_map=colordict,
                    template="plotly_white",
                    hover_name = "country"
                )
                smop.update_traces(
                    showupperhalf=False,
                    diagonal_visible=False
                )
                st.plotly_chart(smop, use_container_width=True)
    
    if event and event.get("selection") and event["selection"]["points"]:
        update_selection(event["selection"]["points"])
        st.rerun()

            # Table
            # st.subheader(f"Data ({latest_year})")
            # latest_stats = filtered_df[filtered_df['year'] == latest_year][['country', selected_col]]
            # st.dataframe(latest_stats.sort_values(by=selected_col, ascending=False), hide_index=True,
            # use_container_width=True)