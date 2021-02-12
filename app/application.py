# This data dashboard is designed for AWS under the address: http://ec2-18-159-45-234.eu-central-1.compute.amazonaws.com:8050/

# Importing the required libraries
from io import BytesIO
from zipfile import ZipFile
import pandas as pd # print(pd.__version__) = 1.1.5
import requests     # print(requests.__version__) = 2.22.0
import pandas as pd
import plotly.graph_objects as go # plotly 4.14.1
from plotly.subplots import make_subplots
import dash  # print(dash.__version__) (version 1.18.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc # version 0.11.1

#----------------------------------------------
# Importing Google Mobility data
#----------------------------------------------
url = "https://www.gstatic.com/covid19/mobility/Region_Mobility_Report_CSVs.zip"
filename = requests.get(url).content
zf = ZipFile( BytesIO(filename), 'r' )
df = pd.read_csv(zf.open('2020_DE_Region_Mobility_Report.csv'), 
                 usecols=['sub_region_1', 'date','retail_and_recreation_percent_change_from_baseline', 
                          'grocery_and_pharmacy_percent_change_from_baseline',
                          'parks_percent_change_from_baseline','transit_stations_percent_change_from_baseline',
                          'workplaces_percent_change_from_baseline','residential_percent_change_from_baseline'])

# Modifying the name of the columns
df.rename(columns={"sub_region_1": "state", "retail_and_recreation_percent_change_from_baseline": "retil_creat",                   "grocery_and_pharmacy_percent_change_from_baseline":"groce_pharma",                  "parks_percent_change_from_baseline":"parks",                   "transit_stations_percent_change_from_baseline":"transit",                  "workplaces_percent_change_from_baseline":"work",                  "residential_percent_change_from_baseline":"resid"}, inplace=True)

# Converting the date from pandas object (python strin) to pandas date time
df['date']=pd.to_datetime(df['date']).dt.date

# There are data for Germany in total and also the data for each state, separately. All of the data start as of 15.02.2020
#let's fill up the 'state' column that is only for the entire Germany with 'all'
df['state'].fillna('all', inplace=True)

#---------------------------------------------------------
# Importing Covid Data from Robert Koch Institute's page
#---------------------------------------------------------
covid=pd.read_csv('https://www.arcgis.com/sharing/rest/content/items/f10774f1c63e40168479a1feb6c7ca74/data',
                    usecols=['Bundesland', 'AnzahlFall','NeuerFall', 'Meldedatum'])

# Renaming Columns
covid.rename(columns={"Bundesland": "state", "AnzahlFall": "cases", "NeuerFall":"new",  "Meldedatum":"date"}, inplace=True)

# Changing the names of the states from German to English
covid.replace({'Bayern': 'Bavaria', 'Rheinland-Pfalz': 'Rhineland-Palatinate',
               'Nordrhein-Westfalen': 'North Rhine-Westphalia','Sachsen': 'Saxony',
               'Sachsen-Anhalt': 'Saxony-Anhalt','Thüringen': 'Thuringia','Niedersachsen': 'Lower Saxony'},
              inplace=True)

# Dropping the rows before 2020/02/15 (this is the date at which the Google traffic data begin)
covid.drop(covid[covid.date < '2020/02/15'].index, inplace=True)

# Converting the date+time to date-only in covid.
covid['date']= pd.to_datetime(covid['date']).dt.date

# To calculate the corona positive cases in each day, in each state, I need to get rid of the cases in which the column 'new' is -1
# Look up the explanations in the webpage of the Robert Koch Institute:
# https://www.arcgis.com/home/item.html?id=f10774f1c63e40168479a1feb6c7ca74
# Let's drop the rows with new=-1
indexNames = covid[ covid['new']== -1 ].index
covid.drop(indexNames , inplace=True)

# The Covid cases for the states
covid=covid.groupby(['state','date'], as_index=False).sum()

# pro 100k capita calculations: 
# Each state's poupulation is taken from the data dashboard of the Robert Koch Institute with the following address:
# https://experience.arcgis.com/experience/478220a4c454480e823b17327b2bf1d4
covid.drop(columns=['new'],inplace=True)
state_popul=pd.DataFrame.from_dict(
                    {'state':[
                    'Schleswig-Holstein','Hamburg','Lower Saxony','Bremen', 'North Rhine-Westphalia',
                    'Hessen','Rhineland-Palatinate','Baden-Württemberg','Bavaria','Saarland','Berlin',
                   'Brandenburg','Mecklenburg-Vorpommern','Saxony','Saxony-Anhalt','Thuringia'],
                  
                   'popul':[
                   2903773, 1847253, 7993608, 681202, 17947221, 6288080, 4093903, 11100394,
                   13124737, 986887, 3669491, 2521893, 1608138, 4071971,2194782, 2133378]
                  })

covid['cases_percap']=covid.set_index('state')['cases'].div (state_popul.set_index('state')['popul'], axis=0).reset_index().loc[:,0]*100000

#Germany's total Covid cases per 100k capita:
germany_popul=83166711
covid_germany=covid.iloc[:,:3].groupby('date',as_index=False).sum()
covid_germany['cases']=covid_germany['cases']/germany_popu*100000
covid_germany.rename(columns={"cases": "cases_percap"}, inplace=True)

# -----Dash App Layout----------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB],
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

#for taking the app on AWS:
application = app.server
app.title='Covid Mobility In Germany'

# Layout
app.layout = dbc.Container([

    dbc.Row(
        dbc.Col(dcc.Markdown(''' ''',
                             className=' font-weight-bold text-left text-muted text-primary mb-sm-5'),
                width={'size': 10, 'offset': 1, 'order': 1}), justify='start'),

    dbc.Row(
        dbc.Col(html.H4("Google Mobility Report in Germany During the Covid-19 Pandemic",
                        className=' font-weight-bold text-center text-muted text-primary mb-sm-5'),
                width=12), justify='center'),

    dbc.Row([
        dbc.Col(dcc.Markdown("""
    ###### The graph at the top shows the trend of the Corona cases (Meldung) in Germany and in the selected state (Bundesland). The data at the bottom graph show how visitors to categorized places (or time spent in categorized places) change compared to baseline days. A baseline day represents a normal value for that day of the week. The baseline day is the median value from the 5‑week period Jan 3 – Feb 6, 2020. For more information, please check [here](https://support.google.com/covid19-mobility/answer/9824897?hl=en&ref_topic=9822927).
    """, className=' breadcrumb mb-4 text-left text-muted text-primary'),
                width=10,  # {'size':10, 'offset':0, 'order':1} ,
                # xs=12, sm=12, md=12, lg=5, xl=5,
                )]
        , justify='center'
    ),

    dbc.Row([

        dbc.Col([
            dcc.Dropdown(id="state_choice",
                         options=[
                             {"label": "Baden-Württemberg", "value": "Baden-Württemberg"},
                             {"label": "Bavaria", "value": "Bavaria"},
                             {"label": "Berlin", "value": "Berlin"},
                             {"label": "Brandenburg", "value": "Brandenburg"},
                             {"label": "Bremen", "value": "Bremen"},
                             {"label": "Hamburg", "value": "Hamburg"},
                             {"label": "Hessen", "value": "Hessen"},
                             {"label": "Lower Saxony", "value": "Lower Saxony"},
                             {"label": "Mecklenburg-Vorpommern", "value": "Mecklenburg-Vorpommern"},
                             {"label": "North Rhine-Westphalia", "value": "North Rhine-Westphalia"},
                             {"label": "Rhineland-Palatinate", "value": "Rhineland-Palatinate"},
                             {"label": "Saarland", "value": "Saarland"},
                             {"label": "Saxony", "value": "Saxony"},
                             {"label": "Saxony-Anhalt", "value": "Saxony-Anhalt"},
                             {"label": "Schleswig-Holstein", "value": "Schleswig-Holstein"},
                             {"label": "Thuringia", "value": "Thuringia"}],
                         multi=False,
                         value="Baden-Württemberg",
                         # style={'width': "40%"}
                         )
        ], width={'size': 5, 'offset': 0, 'order': 1}, xs=12, sm=12, md=12, lg=5, xl=5
        ),
        dbc.Col([

            dcc.Dropdown(id="traffic",
                         options=[
                             {"label": "Retail and Recreation", "value": "retil_creat"},
                             {"label": "Groceries and Pharmacies", "value": "groce_pharma"},
                             {"label": "Parks", "value": "parks"},
                             {"label": "Transit Stations", "value": "transit"},
                             {"label": "Work", "value": "work"},
                             {"label": "Residential", "value": "resid"}],
                         multi=False,
                         value="retil_creat",
                         # style={'width': "40%"}
                         )
        ], width={'size': 5, 'offset': 0, 'order': 2}, xs=12, sm=12, md=12, lg=5, xl=5
        )

    ], justify='center'),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='Germany_Covid_Traffic', config=dict(displaylogo=False), figure={})
        ], width=12,
            # width={'size':12, 'offset':0, 'order':1},
            xs=10, sm=10, md=10, lg=12, xl=12
        )], justify='center'),

    dbc.Row([
        dbc.Col(dcc.Markdown("""
        ###### • Data source: [Robert Koch Institute](https://www.arcgis.com/home/item.html?id=f10774f1c63e40168479a1feb6c7ca74) and [Google](https://www.google.com/covid19/mobility/)  • This page is made by [Payam Payamyar](https://www.linkedin.com/in/payamyar/)
        """, className='text-left text-muted text-primary'
                            #  'bg-white'
                             # ' breadcrumb mb-4 text-center text-muted text-primary'
                             ),
                width={'size': 12, 'offset': 4, 'order': 1},
                #xs=6, sm=6, md=12, lg=5, xl=6,
                )]
        , justify='center'
    ),

  
    dbc.Row(
        dbc.Col(dcc.Markdown(''' ''',
                             className=' font-weight-bold text-left text-muted text-primary mb-sm-5'),
                width={'size': 10, 'offset': 1, 'order': 1}), justify='start'),

], fluid=False)

# ---------App Callback---------
@app.callback(
    Output('Germany_Covid_Traffic', 'figure'),
    Input('traffic', 'value'),
    Input('state_choice', 'value'))
def update_graph(traff, st_ch):

    # Extracting data from the data frames according to the state of choice (st_ch)
    covid_df = covid[covid['state'] == st_ch]
    Germany_googl = df[df['state'] == 'all']
    data_googl = df[df['state'] == st_ch]

    # Preparing the text to be shown in the legend:
    traff_name_dic = {'val': ["retil_creat", "groce_pharma", "parks", "transit", "work", "resid"],
                      'lab': ["Retail and Recreation", "Groceries and Pharmacies", "Parks",
                              "Transit Stations", "Work", "Residential"]}
    traff_df = pd.DataFrame.from_dict(traff_name_dic)
    traff_name = traff_df[traff_df['val'] == traff].iloc[0, 1]

    text1 = st_ch + ': Daily Covid-19 Cases / 100\'000 Inhabitants '
    text2 = 'Germany: Daily Covid-19 Cases / 100\'000 Inhabitants'
    text3 = st_ch + ': % Change in Google Traffic at ' + traff_name + ' Sector'
    text4 = 'Germany:' + ' % Change in Google Traffic at ' + traff_name + ' Sector'
    
    # Defining the figure graph:
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.072)

    # Top graph
    fig.add_trace(go.Scatter(name=text1, x=covid_df['date'], y=covid_df['cases_percap'], mode='lines+markers'
                             ),
                  row=1, col=1)

    fig.add_trace(go.Bar(name=text2, x=covid_germany['date'], y=covid_germany['cases_percap']),
                  row=1, col=1)

    # Bottom graph
    fig.add_trace(go.Scatter(name=text3, x=data_googl['date'], y=data_googl[traff], mode='lines+markers',
                             ),
                  row=2, col=1)

    fig.add_trace(go.Bar(name=text4, x=Germany_googl['date'], y=Germany_googl[traff]),
                  row=2, col=1)

    # --------Update layout properties-------------

    fig.update_layout(
        # title_text="Reference:____",
        # legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=0.7),
        legend=dict(orientation="v", yanchor="top", y=1.17, xanchor="left", x=0.25),
        autosize=True,
        #         width=1600,
        height=750,
    )

    fig.update_yaxes(automargin=True)

    fig.update_xaxes(range=[pd.Series([covid['date'].min(), df['date'].min()]).min(),
                            pd.Series([covid['date'].max(), df['date'].max()]).max()],
                     showgrid=True,
                     ticks="outside",
                     tickson="boundaries",
                     ticklen=10,
                     automargin=True,
                     # title_text="xaxis 2 title",
                     row=1, col=1)
    fig.update_xaxes(range=[pd.Series([covid['date'].min(), df['date'].min()]).min(),
                            pd.Series([covid['date'].max(), df['date'].max()]).max()],
                     showgrid=True,
                     ticks="outside",
                     tickson="boundaries",
                     ticklen=10,
                     automargin=True,
                     # title_text="xaxis 2 title",
                     row=2, col=1)

    fig.show()

    return fig

#-------run the app on AWS------------
if __name__=='__main__':
#    application.run(port=8080)
#    app.run_server(port=8080)
#    app.run_server()
#    application.run(debug=True, port=8080)
    app.run_server(debug=True,port=8050, host="0.0.0.0")
#    app.server.run(debug=True, host='0.0.0.0')
#    app.run_server(debug=True, port=8050, host='0.0.0.0')
#    app.run_server(debug=True, port=7000, host='0.0.0.0')
#    application.run(debug=True, port=8080)
#    app.run_server(debug=True, port=7000)
#    for Jupyter notebook
#    app.server.run(port=3000, host='127.0.0.1')
#    app.server.run(debug=True, port=3000, host='0.0.0.0')