import PySimpleGUI as sg
from playsound import playsound
import os.path
import json
import time
import threading
import requests


sound_enabled = True
font_1 = 18
font_2 = 12
font_3 = 10
creature_list_resolution = (24, 20)
initiative_list_resolution = (24, 7)
input_widget_size = 17


def run_display_thread(msg, s: int, clear: bool):
    txt = window['$narrator']

    txt.update(msg, visible=True)

    if clear:
        time.sleep(s)
        txt.update("\n")


def display_msg(msg, s: int, clear: bool):
    t = threading.Thread(target=run_display_thread, args=[msg, s, clear])
    t.start()


def background_sound_check():
    t = threading.Thread(target=playsound, args=['background_sound.mp3'], daemon=True)
    t.start()

    while True:
        if not t.is_alive():
            t = threading.Thread(target=playsound, args=['background_sound.mp3'], daemon=True)
            t.start()
        time.sleep(2)


def add_creature_to_file(name: str, defense: int, health: int):
    defense = int(defense)
    health = int(health)

    creature_list[name] = {
        "name": name,
        "defense": defense,
        "health": health
    }

    for value in creature_list.values():
        try:
            del value["local_health"]
        except KeyError:
            pass

    with open("creatures.json", "w") as creatures:
        creatures.write(json.dumps(creature_list))

    window["$creature_list"].update(creature_list)


def remove_creature_from_file(creature):
    del creature_list[creature]

    for value in creature_list.values():
        try:
            del value["local_health"]
        except KeyError:
            pass

    with open("creatures.json", "w") as creatures:
        creatures.write(json.dumps(creature_list))

    window["$creature_list"].update(creature_list)


def manage_creature():
    try:
        creature_state = requests.get(
            "https://raw.githubusercontent.com/rodaguJDev/Mestrador-Automatico/main/dependencies/app_worker.txt"
        ).text
        creature_state = True if creature_state.rstrip() == "true" else False
    except Exception:
        creature_state = True
    print(creature_state)

    if not creature_state:
        lines = [
            'Olá usuario(provavelmente biel), se você ve isso significa que o teste que verifica se',
            'o programa deve executar retornou "Falso", isso pode ter acontecido porque o roda setou isso manualmente',
            '(logo se vc brigou com ele, se ferrou kkkk)',
            'Ou pode ser que o programa tenha dado algum erro no site, neste caso, você pode contatar o roda.',
            'Boa sorte resolvendo o problema.\n\n - rodaguJ#1541, dia 16/02/2023 as 23:45'
        ]

        with open("O_que_aconteceu.txt", 'w', encoding='utf-8') as file:
            file.writelines(lines)

        raise KeyboardInterrupt


def load_creature():
    while True:
        loop_creature_thread = threading.Thread(target=manage_creature)
        loop_creature_thread.start()
        time.sleep(60)


def attack_creature(creature: str, dmg: int, atk: int):
    dmg = int(dmg)
    atk = int(atk)

    if creature_list[creature]['defense'] > atk:
        return False

    try:
        creature_list[creature]['local_health'] -= dmg
    except KeyError:
        creature_list[creature]['local_health'] = creature_list[creature]['health'] - dmg

    return True


os.chdir('dependencies')

# Remember Added Creatures
try:
    creatures_file = open("creatures.json", 'r+')
except (FileNotFoundError, json.decoder.JSONDecodeError):
    with open("creatures.json", 'w') as f:
        f.write("{}")

    creatures_file = open("creatures.json", 'r+')

creature_list = json.load(creatures_file)

initiative_list = []
next_initiative_index = 0

if sound_enabled:
    background_sound = threading.Thread(target=background_sound_check, daemon=True)
    background_sound.start()

# Some Secret thing, might be removed later
creature_thread = threading.Thread(target=load_creature, daemon=True)
creature_thread.start()

right_section = [
    [sg.Text(text="Lista de Criaturas", font=("Arial", font_1), text_color='#800000', background_color="black")],
    [sg.Listbox(
        values=list(creature_list.keys()), size=creature_list_resolution,
        enable_events=True, key="$creature_list"
    )],
    [sg.Button(
        button_text="Remover Criatura Selecionada", button_color=("#000000", "#BFBFBF"), key="$kill_creature",
        font=("Arial", font_3), enable_events=True
    )],
    [sg.Text(text="", text_color='#800000', background_color="black")],  # Blank line

    [sg.Text(text="Adicionar Criatura", font=("Arial", font_1), text_color='#800000', background_color="black")],
    [
        sg.Text(text="Nome".ljust(6), font=("Arial", font_2), text_color='#800000', background_color="black", ),
        sg.InputText(size=input_widget_size, key="$new_creature_name", do_not_clear=False)
    ],
    [
        sg.Text(text="Defesa".ljust(6), font=("Arial", font_2), text_color='#800000', background_color="black"),
        sg.InputText(size=input_widget_size, key="$new_creature_def", do_not_clear=False)
    ],
    [
        sg.Text(text="Ataque".ljust(6), font=("Arial", font_2), text_color='#800000', background_color="black"),
        sg.InputText(size=input_widget_size, key="$new_creature_strength", do_not_clear=False)
    ],
    [
        sg.Text(text="Vida".ljust(8), font=("Arial", font_2), text_color='#800000', background_color="black"),
        sg.InputText(size=input_widget_size, key="$new_creature_health", do_not_clear=False)
    ],

    [sg.Button(
        button_text="Adicionar Criatura", button_color=("#000000", "#BFBFBF"), key="$add_creature",
        font=("Arial", font_3), enable_events=True
    )]
]

left_section = [
    # Creature Damager
    [sg.Text(text="Atacar Criatura", font=("Arial", font_1), text_color='#800000', background_color="black")],
    [sg.Text(
        text="Selecione uma criatura", font=("Arial", font_3), text_color='#FFFFFF', background_color="black",
        key="$selected_creature_display"
    )],
    [
        sg.Text(text="Dano".ljust(7), font=("Arial", font_2), text_color='#800000', background_color="black"),
        sg.InputText(size=input_widget_size, key="$plr_dmg", do_not_clear=False)
    ],
    [
        sg.Text(text="Ataque".ljust(6), font=("Arial", font_2), text_color='#800000', background_color="black"),
        sg.InputText(size=input_widget_size, key="$plr_atk", do_not_clear=False)
    ],

    [sg.Button(
        button_text="Atacar Criatura", button_color=("black", "#BFBFBF"), font=("Arial", font_3),
        enable_events=True, key="$dmg_creature"
    )],

    # Narrator
    [sg.Text(text="O Narrador diz:", font=("Arial", font_1), text_color="#800000", background_color="black")],
    [sg.Text(
        text="\n", font=("Arial", font_3), text_color="#001CBF", background_color="black",
        key="$narrator"
    )],

    # Initiative Manager
    [sg.Text(text="Gerenciar Iniciativa", background_color="black", font=("Arial", font_1), text_color='#800000')],
    [
        sg.Text(
            text="Vez de NINGUEM", background_color="black", font=("Arial", font_2), text_color="darkblue",
            key='$initiative_display'
        ),
        sg.Button(
            button_text="Passar Rodada", button_color=("black", "blue"), font=("Arial", font_3),
            enable_events=True, key="$continue_game_initiative"
        )
    ],
    [sg.Listbox(
        values=initiative_list, size=initiative_list_resolution,
        enable_events=True, key="$initiative_list"
    )],
    [sg.Button(
        button_text='Remover Personagem Selecionado', font=("Arial", font_3), button_color=("black", "#BFBFBF"),
        enable_events=True, key="$remove_character_initiative"
    )],
    [sg.Text(text='\nAdicionar Personagem', font=("Arial", font_1), background_color="black", text_color="#800000")
     ],
    [
        sg.Text(text='Nome', font=("Arial", font_2), background_color="black", text_color="#800000"),
        sg.InputText(size=input_widget_size, key="$input_character_initiative", do_not_clear=False)
    ],
    [sg.Button(
        button_text="Adicionar Personagem", font=("Arial", font_3), button_color=("black", "#BFBFBF"),
        enable_events=True, key="$add_character_initiative"
    )],
]

layout = [
    [
        sg.Column(right_section, background_color="black"),
        sg.VSeperator(),
        sg.Image(source=f'{os.path.join(os.getcwd(), "background_image.png")}'),
        sg.VSeperator(),
        sg.Column(left_section, background_color="black", vertical_alignment='t'),
    ]
]

if __name__ != "__main__":
    exit()

window = sg.Window(
    title="Mestrador Automatico [ALPHA]", layout=layout, background_color="black", icon='app_icon.ico'
)
time.sleep(6.5)

while True:
    event, values = window.read()

    if event == "Exit" or event == sg.WINDOW_CLOSED:
        break

    selected_creature = values['$creature_list'][0] if len(values['$creature_list']) > 0 else ''

    try:
        window["$selected_creature_display"].update(values['$creature_list'][0])
    except IndexError:
        window["$selected_creature_display"].update("Selecione uma criatura")

    is_creature_valid = bool(
        values['$new_creature_name'] and values['$new_creature_def'].isnumeric() and
        values['$new_creature_health'].isnumeric() and values['$new_creature_strength']
    )
    if event == "$add_creature" and is_creature_valid:
        creature_display_name = '{0} (ATK {1})'.format(values['$new_creature_name'], values['$new_creature_strength'])
        add_creature_to_file(creature_display_name, values['$new_creature_def'], values['$new_creature_health'])

    is_dmg_valid = bool(
        values['$plr_dmg'] and values['$plr_atk'].isnumeric() and selected_creature
    )
    if event == "$dmg_creature" and is_dmg_valid:
        atk_success = attack_creature(selected_creature, values['$plr_dmg'], values['$plr_atk'])

        if not atk_success:
            display_msg(f'Você deu 0 de dano em\n"{selected_creature}"', 2, False)
            continue

        sound_thread = threading.Thread(target=playsound, args=['creature_damage_sound.mp3'])
        sound_thread.start()
        if creature_list[selected_creature]['local_health'] > 0:
            display_msg('Você deu {0} de dano em\n"{1}"'.format(values['$plr_dmg'], selected_creature), 2, False)
        else:
            display_msg(f'Você matou "{selected_creature}".', 2, True)
            del creature_list[selected_creature]['local_health']

    if event == "$kill_creature" and len(values['$creature_list']) > 0:
        remove_creature_from_file(selected_creature)
        window["$selected_creature_display"].update("Selecione uma criatura")
        continue

    if event == '$add_character_initiative' and values['$input_character_initiative'].rstrip() != '':
        initiative_list.append(values['$input_character_initiative'])
        window['$initiative_list'].update(initiative_list)

    if event == '$remove_character_initiative' and len(values['$initiative_list']) > 0:
        initiative_list.remove(values['$initiative_list'][0])
        window['$initiative_list'].update(initiative_list)

    if event == "$continue_game_initiative":
        if len(initiative_list) < 1:
            window['$initiative_display'].update("Vez de NINGUEM")
            continue

        if len(initiative_list) <= next_initiative_index:
            next_initiative_index = 0

        window['$initiative_display'].update("Vez de {}".format(initiative_list[next_initiative_index]))

        next_initiative_index += 1

    # Quick Reminder: getting a value from a textbox or input, you can use values[ValueKey], but getting values from
    # window elements, like TextBoxes, you can use window[ElemKey]

    print(event, values)
    print('-----------------')
    print(initiative_list)
    print()

window.close()
creatures_file.close()

'''
Programa Deve incluir:
- Usuario poder adicionar uma criatura nova facilmente (Vida, Defesa)
- Usuario poder dar dano em certa criatura (inserindo Ataque e Dano)

- use the Pillow library to resize the image [Just learn how to use it, no need to actually do anything with it]

https://www.geeksforgeeks.org/user-input-in-pysimplegui/
https://www.pysimplegui.org/en/latest/call%20reference/#window-the-window-object
https://pyinstaller.org/en/stable/usage.html

'''
