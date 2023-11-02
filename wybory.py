import re
import lxml.etree as ET
import pandas
import streamlit as st
from numpy import isnan
from streamlit.components.v1 import html
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(layout="wide")

ambit_file_path = Path(__file__).with_name('./Sejm_RP_1.svg').absolute()
results_file_path = Path(__file__).with_name('./wybory.xlsx').absolute()

c1, c2 = st.columns([2, 1])


def load_data(year):
    df = pd.read_excel(results_file_path, decimal=',', sheet_name=year)
    df.columns = [get_party_display_name(col) if 'KOMITET WYBORCZY' in col.upper() else col for col in df.columns]
    return df


def load_general_data(year):
    return pd.read_excel(results_file_path, decimal=',', sheet_name=f'{year}_general')


def print_legend_for_winners(ambit_winners):
    with c2:
        for _ in range(5):
            st.text("")
    unique_winners_names = set([winner['name'] for winner in ambit_winners.values()])
    with c2:
        for name in unique_winners_names:
            st.write(f"<span style='color:{get_color_for_party(name)};'> {chr(int('25A0', 16))}  </span>{name}",
                     unsafe_allow_html=True)


def modify_svg_winners(ambit_winners):
    tree = ET.parse(ambit_file_path)
    results = tree.xpath('//svg:g[@id="layer3"]', namespaces={'svg': 'http://www.w3.org/2000/svg'})
    for element in results[0].iter():
        if element.get('id') == 'layer3':
            continue
        winner = ambit_winners.get(int(element.get('id')))
        color = get_color_for_party(winner['name'])

        style = element.get('style')
        style += f';fill:{color};'
        element.set('style', style)

        new_element = ET.Element("title")
        new_element.text = str(winner['value'])
        new_element.set('style', 'width=10px;background-clor=#ffffff')
        element.append(new_element)

    return ET.tostring(tree)


def print_legend_for_all_parties(df: pandas.DataFrame):
    committee_columns = [name for name in df.columns if 'KOMITET WYBORCZY' in name.upper()]

    with c2:
        selected_party = st.radio(
            "Partie",
            committee_columns
        )

        st.session_state['selected_party'] = selected_party


party_results_colors = {
    '#DAF7A6': {
        'min': 0.0,
        'max': 5.0
    },
    '#DAFF76': {
        'min': 5.0,
        'max': 10.0
    },
    '#47fb56': {
        'min': 10.0,
        'max': 20.0
    },
    '#ff9900': {
        'min': 20.0,
        'max': 30.0
    },
    '#FF5733': {
        'min': 30.0,
        'max': 40.0
    },
    '#C70039': {
        'min': 40.0,
        'max': 50.0
    },
    '#900C3F': {
        'min': 50.0,
        'max': 60.0
    },
    '#581845': {
        'min': 60.0,
        'max': 100.0
    },
}


def get_color_for_single_ambit(support: float):
    if isnan(support) or support == 0.0:
        return '#ffffff'

    for color, values in party_results_colors.items():
        if values['min'] < support <= values['max']:
            return color
    return '#ffffff'


def get_single_ambit_legend():
    legend = ''
    for color, values in party_results_colors.items():
        legend += f"<span style='color:{color};'> {chr(int('25A0', 16))}  </span>{int(values['min'])}% - {int(values['max'])}% |"

    with c1:
        st.write(legend[:-1], unsafe_allow_html=True)


def bar_chart_for_single_party(df: pandas.DataFrame):
    with c2:
        single_party_results = pandas.DataFrame(df[st.session_state['selected_party']])
        single_party_results['Okręg'] = single_party_results.index + 1
        fig = px.bar(single_party_results, y='Okręg', x=st.session_state['selected_party'], orientation='h',
                     range_x=[0, 100], color_discrete_sequence=['green'] * 41)
        st.plotly_chart(fig, use_container_width=True)


def modify_svg_single_part_support(df: pandas.DataFrame):
    if 'selected_party' not in st.session_state or st.session_state['selected_party'] not in df:
        render_svg(ambit_file_path)

    single_party_results = df[st.session_state['selected_party']]

    tree = ET.parse(ambit_file_path)
    results = tree.xpath('//svg:g[@id="layer3"]', namespaces={'svg': 'http://www.w3.org/2000/svg'})
    for element in results[0].iter():
        if element.get('id') == 'layer3':
            continue
        result = single_party_results[int(element.get('id')) - 1]

        color = get_color_for_single_ambit(result)

        style = element.get('style')
        style += f';fill:{color};'
        element.set('style', style)

        new_element = ET.Element("title")
        new_element.text = f'{str(result)}'
        new_element.set('style', 'width=10px;background-clor=#ffffff')
        element.append(new_element)

    return ET.tostring(tree)


attendance_colors = {
    '#87CEEB': {
        'min': 0.0,
        'max': 50.0
    },
    '#4682B4': {
        'min': 50.0,
        'max': 60.0
    },
    '#4169E1': {
        'min': 60.0,
        'max': 70.0
    },
    '#0000CD': {
        'min': 70.0,
        'max': 80.0
    },
    '#000080': {
        'min': 80.0,
        'max': 100.0
    },
}


def get_color_for_attendance(attendance: float):
    if isnan(attendance) or attendance == 0.0:
        return '#ffffff'

    for color, values in attendance_colors.items():
        if values['min'] < attendance <= values['max']:
            return color

    return '#ffffff'


def get_attendance_legend():
    with c2:
        for _ in range(8):
            st.text("")

    for color, values in attendance_colors.items():
        with c2:
            st.write(
                f"<span style='color:{color};'> {chr(int('25A0', 16))}  </span>{int(values['min'])}% - {int(values['max'])}%",
                unsafe_allow_html=True)


def attendance(df: pandas.DataFrame):
    attendance_results = df['Frekwencja']

    tree = ET.parse(ambit_file_path)
    results = tree.xpath('//svg:g[@id="layer3"]', namespaces={'svg': 'http://www.w3.org/2000/svg'})
    for element in results[0].iter():
        if element.get('id') == 'layer3':
            continue
        result = attendance_results[int(element.get('id')) - 1]

        color = get_color_for_attendance(result)

        style = element.get('style')
        style += f';fill:{color};'
        element.set('style', style)

        new_element = ET.Element("title")
        new_element.text = str(result)
        new_element.set('style', 'width=10px;background-clor=#ffffff')
        element.append(new_element)

    render_svg(ET.tostring(tree))


def get_color_for_party(name):
    if 'PRAWO I SPRAWIEDLIWOŚĆ' in name.upper():
        return '#1248D4'
    elif 'KOALICJA OBYWATELSKA' in name.upper():
        return '#D41248'
    elif 'PLATFORMA OBYWATELSKA' in name.upper():
        return '#D41248'


def get_party_display_name(name):
    if 'ZPOW' in name:
        return re.search('(.*)\s+- ZPOW.*', name)[1]
    return name


def get_ambit_winners(df: pandas.DataFrame):
    committee_columns = [name for name in df.columns if 'KOMITET WYBORCZY' in name.upper()]

    max_values = df[committee_columns].max(axis=1)
    max_values_names = df[committee_columns].idxmax(axis=1)

    return {
        row[0] + 1: {
            'value': row[1][0],
            'name': row[1][1],
        } for row in enumerate(zip(max_values, max_values_names))
    }


def show_general_results(df: pandas.DataFrame):
    with st.container():
        fig = px.pie(df,
                     names='Nazwa',
                     values='Procent głosów',
                     title=f'Głosy',
                     height=400, width=400)
        fig.update_layout(margin=dict(l=20, r=20, t=30, b=80), )
        st.plotly_chart(fig, use_container_width=True)

        st.write('')
        filtered_df = df.loc[df['Procent mandatów'] != 0]
        fig = px.pie(filtered_df,
                     names='Nazwa',
                     values='Procent mandatów',
                     title=f'Mandaty',
                     height=400, width=400)
        fig.update_layout(margin=dict(l=20, r=20, t=30, b=80), )
        st.plotly_chart(fig, use_container_width=True)


def render_svg(svg_string):
    with c1:
        style = '''
        <style>
         path {
            width: 100%;
            height: 100%;
            fill: #69c;
            stroke: #069;
            stroke-width: 5px;
            opacity: 0.5
        }
        </style>
        '''
        html(f'''
        {style}        
        <div style='width:300%;'>
        {svg_string}
        </div>
        ''', height=700)


with st.sidebar:
    st.title('Wybory do sejmu')
    year = st.radio(
        "Rok",
        ("2019", '2015')
    )

    df = load_data(year)
    df_general = load_general_data(year)

    view = st.radio(
        "Wyniki",
        ("Wyniki ogólne", "Zwycięzcy w okręgach", "Partie w okręgach", 'Frekwencja')
    )

if view == 'Wyniki ogólne':
    with c1:
        st.title('Wyniki wyborów do sejmu')
    show_general_results(df_general)
if view == 'Zwycięzcy w okręgach':
    with c1:
        st.title('Zwycięzcy w okręgach')
    ambit_winners = get_ambit_winners(df)
    svg = modify_svg_winners(ambit_winners)
    render_svg(svg)
    print_legend_for_winners(ambit_winners)

elif view == 'Partie w okręgach':
    with c1:
        st.title('Procent głosów w okręgach')
    print_legend_for_all_parties(df)
    svg = modify_svg_single_part_support(df)
    render_svg(svg)
    get_single_ambit_legend()
    bar_chart_for_single_party(df)

elif view == 'Frekwencja':
    with c1:
        st.title('Frekwencja w okręgach')
    attendance(df)
    get_attendance_legend()
