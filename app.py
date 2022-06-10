from flask import Flask, render_template, redirect, url_for, g, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import pandas as pd
import os
from flask_environments import Environments
from google.cloud import bigquery

def df_import(csv_file):
    poke_df = pd.read_csv(csv_file, index_col="english_name")
    return poke_df

poke_df = df_import('pokemon.csv')

def df_drop_add(dataframe):
    """
    ## df_drop_add(dataframe)
    removes a specific list of columns & adds a 'wins' and 'losses' column

    *dataframe:
    - takes a pandas dataframe
    """
    # Columns to drop from dataframe
    dataframe.drop(columns=[
        'japanese_name',
        'percent_male',
        'percent_female',
        'capture_rate',
        'base_egg_steps',
        'evochain_0',
        'evochain_1',
        'evochain_2',
        'evochain_3',
        'evochain_4',
        'evochain_5',
        'evochain_6',
        'gigantamax',
        'mega_evolution',
        'mega_evolution_alt',
    ],   
        axis=1,
        inplace=True,
    )
    # Columns to add to dataframe
    col_list=['wins','losses','times_chosen']
    for col in col_list:
        if col not in dataframe.columns:
            dataframe['wins']=0
            dataframe['losses']=0
            dataframe['times_chosen']=0
        else:
            pass
    return dataframe

poke_df = df_drop_add(poke_df)   

class Pokemon():
    def __init__(self, id, name, hp, attack, defense, speed):
        self.id = id
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        g.name = name
        g.hp = hp
        g.attack = attack
        g.defense = defense
        g.speed = speed
    pass

### BATTLE LOGIC ###
def p1_attacking(pokemon1, pokemon2):
    """
    ### Pokemon1 attacks Pokemon2 for p1_dmg

    - p1_dmg: Takes pokemon1's attack and minuses pokemon2's defense having the total equal the damage.
    """
    # Calculate damage for poke2 to take
    p1_dmg = (pokemon1.attack - pokemon2.defense)
    # Can only attack with positive health total
    if pokemon1.hp > 0:
        # Has to have a positive number for damage to deal damage
        if p1_dmg > 0:
            print(f'{pokemon1.name} is attacking {pokemon2.name} for {p1_dmg} damage!')
            # Set poke2's new hp to be health minus damage
            pokemon2.hp = (pokemon2.hp - p1_dmg)
            print(f'Leaving {pokemon2.name} with {pokemon2.hp} hp')
            return pokemon2.hp
        else:
        # Catches if they do not have a damage of above 0
            print(f"{pokemon1.name}'s {p1_dmg} damage is not enough to damage {pokemon2.name}")
            return pokemon2.hp
    else:
    # allows the other pokemon to attack in poke_battle function
        pass

def p2_attacking(pokemon1, pokemon2):
    """
    ### Pokemon2 attacks Pokemon1 for p2_dmg

    - p2_dmg: Takes pokemon2's attack and minuses pokemon1's defense having the total equal the damage.
    """
    # Calculate damage for poke1 to take
    p2_dmg = (pokemon2.attack - pokemon1.defense)
    # Can only attack with positive health total
    if pokemon2.hp > 0:
        # Has to have a positive number for damage to deal damage
        if p2_dmg > 0:
            print(f'{pokemon2.name} is attacking {pokemon1.name} for {p2_dmg} damage!')
            # Set poke2's new hp to be health minus damage
            pokemon1.hp = (pokemon1.hp - p2_dmg)
            print(f'Leaving {pokemon1.name} with {pokemon1.hp} hp')
            return pokemon1.hp
        # Catches if they do not have a damage of above 0    
        else:
            print(f"{pokemon2.name}'s {p2_dmg} damage is not enough to damage {pokemon1.name}")
            return pokemon1.hp
    # allows the other pokemon to attack in poke_battle function
    else:
        pass

def poke_battle(pokemon1, pokemon2):
    """
    Pits two pokemon against each other, calling p1_attacking() & p2_attacking()
    """
    # Checks to make sure both pokemon have positive damage before while loop
    if (pokemon2.attack - pokemon1.defense) > 0 or (pokemon1.attack - pokemon2.defense) > 0:
        # Runs while both pokemon have positive health.
        while pokemon1.hp > 0 and pokemon2.hp > 0:
            # Determining which poke goes first by comparing speed
            if pokemon1.speed > pokemon2.speed:
                # If pokemon has positive health, it attacks
                if pokemon1.hp > 0:
                    p1_attacking(pokemon1, pokemon2)
                else:
                    # If pokemon has negative health, break loop and return fainted string.
                    return f'{pokemon1.name} has fainted.'
                # If pokemon is still alive after being attacked, it then attacks
                if pokemon2.hp > 0:
                    p2_attacking(pokemon1, pokemon2)
                else:
                    # If pokemon has negative health, break loop and return fainted string.
                    return f'{pokemon2.name} has fainted.'
            else:
                pass
            # This functions the same way as the other speed check, if they have the same speed pokemon2 goes first.
            # This just flips the turn order for which poke is attacking.
            if pokemon2.speed >= pokemon1.speed:
                if pokemon2.hp > 0:
                    p2_attacking(pokemon1, pokemon2)
                else:
                    return f'{pokemon2.name} has fainted.'
                if pokemon1.hp > 0:
                    p1_attacking(pokemon1, pokemon2)
                else:
                    return f'{pokemon1.name} has fainted.'
        if pokemon1.hp < 0:
            return f'{pokemon1.name} has fainted.'
        elif pokemon2.hp < 0:
            return f'{pokemon2.name} has fainted.'
        else:
            pass
    # If both poke's have negative damage, compare the attacks and the one with the most wins.
    else:
        if pokemon1.attack > pokemon2.attack:
            return f'{pokemon2.name} has fainted.'
        elif pokemon2.attack > pokemon1.attack:
            return f'{pokemon1.name} has fainted.'
        # If both poke's have the same attack, compare speed.
        else:
            if pokemon1.speed > pokemon2.speed:
                return f'{pokemon2.name} has fainted.'
            elif pokemon2.speed > pokemon1.speed:
                return f'{pokemon1.name} has fainted.'
            # This defaults if ALL the other conditionals have failed. We could have more conditionals to fall into, but eventually someone has to win.
            else:
                return f'{pokemon2.name} has fainted.'
                # R.I.P.

def updater(data_in, pokemon1, pokemon2, str_message):
    """
    Interprets return of poke_battler() and updates pandas df with win and loss data, as well as times chosen
    """
    if pokemon1.name in str_message:
        data_in.at[pokemon2.id, "wins"] += 1
        data_in.at[pokemon1.id, "times_chosen"] += 1
        data_in.at[pokemon2.id, "times_chosen"] += 1
    elif pokemon2.name in str_message:
        data_in.at[pokemon1.id, "wins"] += 1
        data_in.at[pokemon1.id, "times_chosen"] += 1
        data_in.at[pokemon2.id, "times_chosen"] += 1
    else:
        pass

def bq_pull(poke_1, poke_2):
    """
    BigQuery function to pull pokemon from our dataset and return pandas df
    """
    bqclient = bigquery.Client()
    query_string = f"""
    SELECT *
        FROM deb-01-346001.pokemon.poke_battler_data
        WHERE name LIKE '{poke_1}' OR name LIKE '{poke_2}'
    """
    dataframe = (
        bqclient.query(query_string)
        .result()
        .to_dataframe()
    )
    dataframe.set_index("national_number", inplace=True)
    return dataframe

def insert(df, table):
    """
    BigQuery function to insert updated df into a temp table
    """
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        schema=[
        bigquery.SchemaField("national_number", bigquery.enums.SqlTypeNames.INTEGER)],
        create_disposition='CREATE_IF_NEEDED',
        autodetect=True
    )
    job = client.load_table_from_dataframe(df, table, job_config=job_config)
    job.result()

def update_tablebq(main_table, temp_table):
    """
    BigQuery function that merges the temp table onto the main table
    """
    bqclient = bigquery.Client()
    update = f"""
        UPDATE {main_table} as i
        SET wins = i.wins + n.wins,
        losses = i.losses + n.losses,
        times_chosen = i.times_chosen + n.times_chosen
        FROM {temp_table} as n
        WHERE i.name = n.name
"""
    job = bqclient.query(update)
    job.result()


def drop_tablebq(temp_table):
    """
    BigQuery function to drop temp_table after merge
    """
    bqclient = bigquery.Client()
    drop = f"DROP TABLE IF EXISTS {temp_table};"
    return bqclient.query(drop)


app = Flask(__name__)
# env = Environments(self.app)

app.config["SECRET_KEY"] = 'TQIcpo6gbADjldiP9o9XirAl0LliqYpw'
# env.from_yaml(os.path.join(os.getcwd(), 'myapp', 'config.yml'))
Bootstrap(app)

#Create a subclass of FlaskForm for our pokemon
class PokemonForm(FlaskForm):
    poke_1 = StringField("Pokemon vs...", validators=[DataRequired()])
    poke_2 = StringField("...Pokemon", validators=[DataRequired()])
    submit = SubmitField('Battle!')

@app.route("/", methods=["GET", "POST"])
def poke_fight():
    """
    Accepts user input, runs it through our battler functions, and updates bigquery.
    """
    global poke_df
    form = PokemonForm()
    #ensures our form has text input
    if form.validate_on_submit() == True:
        poke_1 = form.poke_1.data.title()
        poke_2 = form.poke_2.data.title()
        #pulls pokemon from bigquery into df
        poke_df = bq_pull(poke_1, poke_2)
        #sets index
        poke_1id = poke_df.index[poke_df['name'] == poke_1][0]
        poke_2id = poke_df.index[poke_df['name'] == poke_2][0]
        #creates instances of pokemon class
        pokemon1 = Pokemon(poke_1id, poke_df.at[poke_1id, "name"], poke_df.at[poke_1id, "hp"], poke_df.at[poke_1id, "attack"], poke_df.at[poke_1id, "defense"], poke_df.at[poke_1id, "speed"])
        pokemon2 = Pokemon(poke_2id, poke_df.at[poke_2id, "name"], poke_df.at[poke_2id, "hp"], poke_df.at[poke_2id, "attack"], poke_df.at[poke_2id, "defense"], poke_df.at[poke_2id, "speed"])
        #checks if the same pokemon was entered twice
        if poke_1 == poke_2:
            message = f"{poke_1} won't fight another {poke_2}!"
        #checks to see if entered pokemon are in our database
        elif pokemon1.id in poke_df.index and pokemon2.id in poke_df.index:
            #runs pokemon through our battler
            message = poke_battle(pokemon1, pokemon2)
            #update our dataframe with win/loss/chosen info
            updater(poke_df, pokemon1, pokemon2, message)
            #insert into temp table
            insert(poke_df, 'deb-01-346001.pokemon.temp_table')
            #merge temp table with main
            update_tablebq("deb-01-346001.pokemon.poke_battler_data", "deb-01-346001.pokemon.temp_table")
            #drop temp table
            drop_tablebq('deb-01-346001.pokemon.temp_table')
        #checks that valid pokemon were entered
        elif pokemon1.id in poke_df.index and pokemon2.id not in poke_df.index:
            message = f"{poke_2} is not a valid pokemon!"
        elif pokemon1.id not in poke_df.index and pokemon2.id in poke_df.index:
            message = f"{poke_1} is not a valid pokemon!"
        else:
            message = f"{poke_1} and {poke_2} are not valid pokemon!"
    else:
        message = "Choose your Pokemon!"
    #renders and displays html template
    return render_template('index.html', form=form, message=message)





"""create flask app"""
app = Flask(__name__)
# name our secret key something
app.secret_key = 'somesecretkey'


@app.route('/query', methods=['GET', 'POST'])
def query():
    """ create a function to log the user in"""
    if request.method == 'POST':
        poke_name = request.form['name']
        if poke_name in g.poke_df:
            return redirect(url_for('poke-profile'))
        else:
            print('this is not a valid pokemon')

    return render_template('query.html')


"""set route for profile """


@app.route('/poke-profile')
def profile():
    """    sets route for the profile to attach to the template for it"""
    return render_template('poke-profile.html')






if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)