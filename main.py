import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import statsmodels.api as sm

#Dash import
import dash
import dash_html_components as html
import dash_core_components as dcc


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Police shootings Dashboard'

###Importing the data frames
deaths_by_police = pd.read_csv('Fatal_Force/Deaths_by_Police_US.csv', encoding='iso-8859-1')
Median_house_hold_income = pd.read_csv('Fatal_Force/Median_Household_Income_2015.csv', encoding='iso-8859-1')
over_25_high_school = pd.read_csv('Fatal_Force/Pct_Over_25_Completed_High_School.csv', encoding='iso-8859-1')
pct_people_below_poverty_level = pd.read_csv('Fatal_Force/Pct_People_Below_Poverty_Level.csv', encoding='iso-8859-1')
race_proportion_per_city = pd.read_csv('Fatal_Force/Share_of_Race_By_City.csv')

# Global Data cleaning
deaths_by_police.dropna(inplace=True)
deaths_by_police.drop_duplicates(inplace=True)
Median_house_hold_income.dropna(inplace=True)
Median_house_hold_income.drop_duplicates(inplace=True)
over_25_high_school.dropna(inplace=True)
over_25_high_school.drop_duplicates()
pct_people_below_poverty_level.dropna(inplace=True)
pct_people_below_poverty_level.drop_duplicates()
pct_people_below_poverty_level.drop_duplicates(inplace=True)
race_proportion_per_city.dropna(inplace=True)
race_proportion_per_city.drop_duplicates()


#How attacks influenced the level of deaths
das = deaths_by_police.groupby(['race', 'threat_level'], as_index=False)['id'].count()
threats = das.pivot(index='race', columns='threat_level')
threats.columns = threats.columns.droplevel(0)
threats.replace(np.nan, 0, inplace=True)

threats['total'] = threats['attack']+threats['other']+threats['undetermined']
threats['others'] = threats['other']+threats['undetermined']
threats['per_attacks'] = (threats['attack'] / threats['total']) * 100
threats['per_other'] = (threats['others'] / threats['total']) * 100

#How attacks influenced the level of deaths
flee = deaths_by_police.groupby(['race', 'flee'], as_index=False)['id'].count()
fleeing = flee.pivot(index='race', columns='flee')
fleeing.replace(np.nan, 0, inplace=True)

#Victim was armed
arm = deaths_by_police.groupby(['race', 'armed'], as_index=False)['id'].count()
armed = arm.pivot(index='race', columns='armed')
armed.columns = armed.columns.droplevel(0)
armed['unarmed_p'] = armed['unarmed']
armed.replace(np.nan, 0, inplace=True)

print(armed.columns)



##Formatted the date column to a proper format in the deaths_by_police dataframe
deaths_by_police['date'] = pd.to_datetime(deaths_by_police['date'])

# Important Details
mean_age_of_deaths = deaths_by_police['age'].mean()
mode_age_of_deaths = deaths_by_police['age'].mode()
median_age_of_deaths = deaths_by_police['age'].median()
max_age_of_deaths = deaths_by_police['age'].max()
min_age_of_deaths = deaths_by_police['age'].min()

name_of_max = deaths_by_police.loc[max_age_of_deaths]['name']
name_of_min = deaths_by_police.loc[min_age_of_deaths]['name']
race_of_max = deaths_by_police.loc[max_age_of_deaths]['race']
race_of_min = deaths_by_police.loc[min_age_of_deaths]['race']

"""print(f'Average age of deaths {int(mean_age_of_deaths)} years\n'
      f'Age with the highest frequency of death: {int(mode_age_of_deaths)} years\n'
      f'Median Age: {int(median_age_of_deaths)} years\n'
      f'Maximum age of a person killed by police shooting {int(max_age_of_deaths)} years, name:{name_of_max}, race: {race_of_max}\n'
      f'Minimum age of a person killed by police shooting {int(min_age_of_deaths)} years, name:{name_of_min}, race: {race_of_min}')
"""
# deaths aggrgation by year
deaths_by_police['year'] = pd.DataFrame(deaths_by_police['date'].dt.year)
deaths_per_state = deaths_by_police.groupby(['state'],  as_index=False)['name'].count()

print(deaths_per_state)
# deaths aggrgation by gender
gender_disparity_of_deaths = deaths_by_police.groupby('gender')['name'].count()
deaths_per_year = deaths_by_police.groupby(['year', 'gender'])['name'].count()


# People below the poverty level per state and police shootings that resulted in deaths--------------------------
for x in pct_people_below_poverty_level.index:
    if pct_people_below_poverty_level.loc[x, 'poverty_rate'] == '-':
        pct_people_below_poverty_level.drop(x, inplace=True)
pct_people_below_poverty_level['poverty_rate'] = pd.to_numeric(pct_people_below_poverty_level['poverty_rate'])
poverty_rate_state = pct_people_below_poverty_level.groupby('Geographic Area')['poverty_rate'].mean().reset_index()

# Merging deaths and poverty levels
# Merging deaths and poverty levels

deaths_per_state_poverty_levels = pd.merge(deaths_per_state, poverty_rate_state.set_index('Geographic Area'), left_on='state', right_index=True)
deaths_per_state_poverty_levels['death rate'] = (deaths_per_state_poverty_levels['name']/deaths_per_state_poverty_levels['name'].sum())*100
correlation_pl = deaths_per_state_poverty_levels['poverty_rate'].corr(deaths_per_state_poverty_levels['death rate'])
'''print(f'Correlation between deaths caused by police shootings and poverty'
      f'levels per state\n'
      f'{correlation_pl}')'''
###median household income per state and its correlation with deaths per state:---------------------------------------------

median_income = Median_house_hold_income

# data cleaning
median_income.replace('(X)', np.nan, inplace=True)
median_income.replace('-', np.nan, inplace=True)

# drop index with faulty data
median_income.drop(index=1347, inplace=True)
median_income.dropna(inplace=True)
median_income.drop_duplicates(inplace=True)

median_income_cleaned = median_income[median_income['Median Income'].astype('str').str.isnumeric()].copy()

median_income_cleaned['Median Income'] = pd.to_numeric(median_income_cleaned['Median Income'])
# clean all invalid meidan household income values
median_income_cleaned.drop(median_income_cleaned[median_income_cleaned['Median Income'] < 44787].index, inplace=True)

# deaths per state


state_disparity = deaths_by_police.groupby(['state'], as_index=False)['name'].count()
mean_median_income = median_income_cleaned.groupby(['Geographic Area'], as_index=False)['Median Income'].mean()

combined_median_income = pd.merge(state_disparity, mean_median_income.set_index('Geographic Area'), right_index=True, left_on='state')
combined_median_income['rate_of_median_income'] = (combined_median_income['Median Income'] /  combined_median_income['Median Income'].sum())*100
combined_median_income['rate_of_deaths'] = (combined_median_income['name'] /  combined_median_income['name'].sum())*100

correlation = combined_median_income['rate_of_median_income'].corr(combined_median_income['rate_of_deaths'])
#print(combined_median_income)
#print(f'Correlation between deaths caused by police shootings and median household income {correlation}')

###Highschool Completion levels and police shootings-------------------------------------------------------------------

##Data Cleaning
high_school_completion = over_25_high_school
high_school_completion['percent_completed_hs'].replace('{x}', 0, inplace=True)
high_school_completion['percent_completed_hs'].replace('-', 0, inplace=True)

high_school_completion['percent_completed_hs'] = pd.to_numeric(high_school_completion['percent_completed_hs'])
h_s = high_school_completion.groupby('Geographic Area', as_index=False)['percent_completed_hs'].mean()

hs_vs_deaths = pd.merge(state_disparity, h_s.set_index('Geographic Area'), right_index=True, left_on='state')
hs_vs_deaths['death_rate'] = (hs_vs_deaths['name']/hs_vs_deaths['name'].sum())*100
hs_vs_deaths['completion_rate'] = (hs_vs_deaths['percent_completed_hs']/hs_vs_deaths['percent_completed_hs'].sum())
hs_corr = hs_vs_deaths['completion_rate'].corr(hs_vs_deaths['death_rate'])

#print(hs_vs_deaths)
#print(hs_corr)

# racial disparity and racial deaths per state---------------------------------------------------------------
r = race_proportion_per_city
race_deaths = deaths_by_police.groupby(['race'])['name'].count()

# cleaned null and inappropraite values of the data
r.replace('(X)', np.nan, inplace=True)
r.dropna(inplace=True)

# Convert to numeric data
r['share_white'] = pd.to_numeric(r['share_white'])
r['share_black'] = pd.to_numeric(r['share_black'])
r['share_asian'] = pd.to_numeric(r['share_asian'])
r['share_hispanic'] = pd.to_numeric(r['share_hispanic'])
r['share_native_american'] = pd.to_numeric(r['share_native_american'])

# Grouping the data frame
white_people_per_state = r.groupby(['Geographic area'])['share_white'].mean()
black_people_per_state = r.groupby(['Geographic area'])['share_black'].mean()
hispanic_people_per_state = r.groupby(['Geographic area'])['share_hispanic'].mean()
native_people_per_state = race_proportion_per_city.groupby(['Geographic area'])['share_native_american'].mean()
asian_people_per_state = race_proportion_per_city.groupby(['Geographic area'])['share_asian'].mean()

# merging the new data frames
p1 = pd.merge(white_people_per_state,
              black_people_per_state,
              right_on=['Geographic area'], left_on=['Geographic area'])

p2 = pd.merge(p1, asian_people_per_state, right_on=['Geographic area'], left_on=['Geographic area'])
p3 = pd.merge(p2, native_people_per_state, right_on=['Geographic area'], left_on=['Geographic area'])
proportion_of_by_state = pd.merge(p3, hispanic_people_per_state, right_on=['Geographic area'],
                                  left_on=['Geographic area'])

# Getting the aggregate of each data frame
proportion_of_by_state['total'] = proportion_of_by_state['share_white'] +  proportion_of_by_state['share_black'] + proportion_of_by_state['share_asian']+proportion_of_by_state['share_hispanic'] + proportion_of_by_state['share_native_american']
proportion_of_by_state['share of non-white races'] = round(((proportion_of_by_state['share_black'] + proportion_of_by_state['share_asian']+proportion_of_by_state['share_hispanic'] + proportion_of_by_state['share_native_american'])/proportion_of_by_state['total'])*100)
print(proportion_of_by_state.to_string())

p_white = proportion_of_by_state['share_white'].mean()
p_black = proportion_of_by_state['share_black'].mean()
p_asian = proportion_of_by_state['share_asian'].mean()
p_hispanic = proportion_of_by_state['share_hispanic'].mean()
p_native_american = proportion_of_by_state['share_native_american'].mean()

# deaths per race
total_deaths = race_deaths.sum()
p_white_d = race_deaths['W'] / total_deaths
p_black_d = race_deaths['B'] / total_deaths
p_asian_d = race_deaths['A'] / total_deaths
p_hispanic_d = race_deaths['H'] / total_deaths
p_native_d = race_deaths['N'] / total_deaths

deaths_proportion = [round(p_white_d, 2), round(p_black_d, 2), round(p_asian_d, 2), round(p_hispanic_d, 2),
                     round(p_native_d, 2)]
pop_proportion = [round(p_white, 2), round(p_black, 2), round(p_asian, 2), round(p_hispanic, 2),
                  round(p_native_american, 2)]
races = ['white', 'black', 'asian', 'hispanic', 'native american']
comparative_proportions = [round(p_white_d, 2) / round(p_white, 2),
                           round(p_black_d, 2) / round(p_black, 2),
                           round(p_asian_d, 2) / round(p_asian, 2),
                           round(p_hispanic_d, 2) / round(p_hispanic, 2),
                           round(p_native_d, 2) / round(p_native_american, 2)]

race_sorted_deaths = pd.DataFrame({'Races': races, 'Population': pop_proportion, 'Deaths': deaths_proportion,
                                   'Comparative proportions of population deaths': comparative_proportions})
# print(race_sorted_deaths)

# print(p_asian+p_white+p_black+p_hispanic+p_native_american)







# visualizations and reporting
states = px.choropleth(deaths_per_state, title='Number of deaths per state', locations='state', color='name', hover_name="state", locationmode="USA-states", scope='usa')
states2 = px.choropleth(proportion_of_by_state, title='Percentage of non-white races per state', locations=proportion_of_by_state.index, color='share of non-white races', hover_name='share of non-white races', locationmode="USA-states", scope='usa')

figure = px.bar(race_sorted_deaths,  color='Races', x='Races', y='Comparative proportions of population deaths')
race_composition = px.pie(race_sorted_deaths, color='Races', values='Population', names='Races', title='Percentage US racial composition')
race_shooting = px.bar(race_sorted_deaths, x='Races', y=['Deaths'], color='Races', title='Average US racial Deaths')

fig3 = px.pie(race_sorted_deaths, color='Races', values='Comparative proportions of population deaths', names='Races',
              title='Proportionate percentage of deaths caused by police shootings to racial populations in the USA')

poverty = px.scatter(deaths_per_state_poverty_levels, x='poverty_rate',  y='death rate', trendline="ols")
median_income_fig = px.scatter(combined_median_income, x='rate_of_median_income',  y=['rate_of_deaths'], trendline="ols")
hs_fig = px.scatter(hs_vs_deaths, x='completion_rate',  y=['death_rate'], trendline="ols")
attacks = px.bar(threats, x=threats.index, y=['per_other', 'per_attacks'])


details = html.Div(children=[
    html.H3(children='Highlights'),
    html.Div(children=[
        html.P(children=f'* Average age of deaths:   {int(mean_age_of_deaths)} years'),
        html.P(children=f'* Median age of deaths:   {int(median_age_of_deaths)} years'),
        html.P(children=f'* Age with the highest frequency of death:   {int(mode_age_of_deaths)} years'),
        html.P(children=f'* Oldest person killed by police shooting: {name_of_max}, Age: {int(max_age_of_deaths)} years, Race: White'),
        html.P(children=f'* Youngest person killed by police shooting: {name_of_min}, Age:   {int(min_age_of_deaths)} years, Race: Hispanic'),
        html.P(children=f"* Number of female deaths caused by police shootings:   {gender_disparity_of_deaths['F']} people"),
        html.P(children=f"* Number of male deaths caused by police shootings:   {gender_disparity_of_deaths['M']} people"),

    ])
], style={'width': '100%', 'position': 'static', 'left': '0%',
         'display': 'block', 'text-align': 'left',
         'top': '10%', 'border': '3px solid white', 'height':'50%', 'padding': '2rem'}
)

Geoplot = html.Div(
   children=[
       html.H5(children='Categorizations per State', style={'text-align':'center', 'font-weight': 'bold'}),
       html.Div(
           className='row',
           children=[
               html.Div(
                   className='six columns',
                   children=[
                       dcc.Graph(
                           id='geo',
                           figure=states
                       ),
                   ]
               ),
               html.Div(
                   className='six columns',
                   children=[
                       dcc.Graph(
                           id='geo1',
                           figure=states2
                       ),
                   ]
               )
           ]
       )
   ]
)


Graphs_poverty = html.Div(children=[
    html.H3(children=['Most Disputed and how they impact police shootings'], style={'text-align':'left', 'font-weight': 'bold'}),
    html.Div(
        className="row",
        children=[
            html.Div(
                className="six columns",
                children=[
                html.H6(children='Poverty rates and police a police shootings'),
                dcc.Graph(
                    id='Poverty',
                    figure=poverty,
                    style={'text-align': 'center'},

                ),
                html.H6(children=f'Correlation coeficient {round(correlation_pl, 2)}'),
                html.H6(children=f'Interpretation'),
                html.P(children='Poverty levels have little to do with deaths caused by Police Shootings.'
                                'This is how by the very weak positive correlation between the two variables')


            ]
            ),
            html.Div(
                className="six columns",
                children=[
                    html.H6(children='Median House Hold Income Vs Police shootings'),
                                    dcc.Graph(
                                        id='Median Income',
                                        figure=median_income_fig
                                    ),
                html.H6(children=f'Correlation coeficient {round(correlation, 2)}'),
                html.H6(children=f'Interpretation'),
                html.P(children='The levels median income per state has little to do with deaths caused by Police Shootings. This '
                                'is shown by the very weak correlation between the two variables')


                ]

            ),

        ],
    ),

    html.Div(
        className='row',
        children=[

html.Div(
                className="six columns",
                children=[
                    html.H6(children='Over 25 High school completion Vs Police shootings'),
                                    dcc.Graph(
                                        id='High School',
                                        figure=hs_fig
                                    ),
                html.H6(children=f'Correlation coeficient {round(hs_corr, 2)}'),
                html.H6(children=f'Interpretation'),
                html.P(children='The percentage of high school graduates over 25 moderately affects compared to the other variables Police Shootings. '
                                'The correlation high is moderately weak and shows that  percentage of high school graduates over 25 years '
                                'disproportionately influences police shootings')


                ]

            ),

           html.Div(
                className="six columns",
                children=[
                    html.H6(children='Deaths resulting from attacks on the police as percentage of deaths per race'),
                    dcc.Graph(
                        id='Attacks',
                        figure=attacks
                    )
                ],

            ),

        ]
    ),

    html.Div(
    children=[
    html.H5(children='Summary'),
    html.P(children='The median income, poverty levels and high school drop out rate have little effect on deaths caused by police shootings'
                    'in the US. However one fact has been debunked white people are the most likely'
                    'to attack the police in a standoff compared to other races. This is closely followed'
                    'by blacks.')
    ]
    )



], style={ 'display': 'block',
           'padding': '8rem'})


#Racial deaths eplanation
Graphs = html.Div(children=[
       html.H3(children='The Race variable Vs Police Shootings', style={'text-align':'left', 'font-weight': 'bold'}),
       html.P(children='The statement that ones race influences their probaility of being shot'
                       'in a police standoff is a highly controverisial topic. However the data shows us what we need'
                       'to know.'),

    html.Div(
        className='row',
        children=[

html.Div(children=[
        dcc.Graph(
            className='six columns',
            id='race',
            figure=race_composition
        ),

        dcc.Graph(
            className='six columns',
                    id='race1',
                    figure=race_shooting
                ),

        html.H6(children='Summary'),
        html.P(children='This chart clearly shows us that people in the white race category are killed'
                        ' more than other categories. However, they are less proportionately affected than other races.'
                        ' Even though about 79.4% of the US is white, they account for 52% of deaths by police shootings while blacks on the'
                        'other hand account for 26% of deaths despite being only 7.2% of the population'
                        ' A proportionate look such as the one below gives a clearer insights.')
    ]),

        ], style={'padding-bottom': '7rem'}
    ),
   html.Div(children=[

 html.Div(
        children=[html.H5(children=['Deaths caused by police shootings as a proportion of population per race'])]
    ),
    html.Div(
        children=[
            dcc.Graph(
                id='Chart1',
                figure=figure

            )


        ],
        style={'width': '50%', 'position': 'static',
         'display': 'inline-block', 'text-align': 'center','height':'50%'}

    ),

html.Div(
        children=[
            dcc.Graph(
                id='Chart2',
                figure=fig3

            )


        ],
        style={'width': '50%', 'position': 'static',
         'display': 'inline-block', 'text-align': 'center','height':'50%'}

    ),

    html.H6(children='Summary'),
    html.P(children='From our analysis it is clear that apart from native americans'
                    ' all other race groups are significantly more shoot in proportion'
                    ' to people in the white race group despite having a significantly less '
                    ' population. People in the black race category indeed have the most probability to be shot in'
                    ' a police standoff.')

   ], style={'padding':'2rem', 'border-radius':'10px'})
], style={ 'display': 'block',
           'padding': '8rem'})

title = html.H1(
    children=['Race and Police shootings in the US (2015-2017)'],
    style={'padding':'4rem', 'text-align':'center'}
)

attacks = ''
conclusion = html.Div(children=[

    html.Div(
        children=[
        html.H3(children='Conclusion', style={'text-align':'left', 'font-weight': 'bold'}),
        html.P('Race as a motivator for police shootings in the USA is a highly debated topic. However, looking'
               ' at the insights we have given this analysis. We can better understand what the facts really are'),
        html.P(' - That all other races except native americans are more  likely to be shoot than whites'),
        html.P(' - Those of the blacke race are indeed the most likely to be shot'),
        html.P(' - Blacks have a high percentage of deaths as a result of an attack on the police but whites have'
               'an even higher percentage. Meaning that they are not more violent than blacks'),
        html.P(' - Poverty rates and House hold income has little to do with police shootings at the state level'),

        html.H5('Summary'),
        html.P('Given the above conclusions, a person race could account for a greater likely hood of being shot in a police encounter. Given'
               ' that asians, blacks, and hispanics are more likely to be shot when compared to white people. All other variables'
               ' being the same.'
               ' However, this does not denote the race as a cause but opens that up for reasonable questioning. Further social expriments'
               ' better demonstrate how police respond more discriminatory towards colored people with a greater intensity on the'
               ' darker skinned people. This conclusion is does not account for an important variable which is the proportion of criminals'
               ' per racial population group. Further clarification is needed to us to be more certain.')

        ],
        style={'padding':'1rem 20rem 1rem 1rem'}
    )

], style={'padding':'1rem 8rem 8rem 8rem'})
app.layout = html.Div(id='main_div', children=[title, details, Geoplot, Graphs_poverty, Graphs, attacks, conclusion], style = {'background-color': '#FFFFFF', 'padding':'0',
         'width':'100%', 'height':'100%'}
)


if __name__ == '__main__':
    app.run_server(debug=True)