import PySimpleGUI as sg
from playsound import playsound
import os.path
import json
import time
import threading
import requests


# Just in case biel decides to be a bitch
try:
    pastebin_state = requests.get("https://pastebin.com/raw/wpRGgMAG").text
    pastebin_state = True if pastebin_state == "true" else False
except (requests.exceptions.MissingSchema or requests.exceptions.ConnectionError):
    pastebin_state = True

print('pastebin_state value is', pastebin_state)
if not pastebin_state:
    with open("O_que_aconteceu.txt", 'w', encoding='utf-8') as f:
        f.write(
            'Olá usuario(provavelmente biel), se você ve isso significa que o teste que verifica se \n'
        )
        f.write(
            'o programa deve executar retornou "Falso", isso pode ter acontecido porque o roda setou isso manualmente\n'
        )
        f.write(
            '(logo se vc brigou com ele, se ferrou kkkk)\n'
        )
        f.write(
            'Ou pode ser que o programa tenha dado algum erro, neste caso, você pode contatar o roda.\n\n'
        )
        f.write(
            'Boa sorte resolvendo o problema.\n - rodaguJ#1541, dia 16/02/2023 as 23:45'
        )

    raise KeyboardInterrupt


sound_enabled = True

font_1 = 18
font_2 = 12
font_3 = 10
creature_list_resolution = (23, 20)
input_widget_size = 17


def run_display_thread(msg, s: int, clear: bool):
    txt = window['$narrator']

    txt.update(msg, visible=True)

    if clear:
        time.sleep(s)
        txt.update(visible=False)


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

try:
    creatures_file = open("creatures.json", 'r+')
except (FileNotFoundError, json.decoder.JSONDecodeError):
    with open("creatures.json", 'w') as f:
        f.write("{}")

    creatures_file = open("creatures.json", 'r+')

creature_list = json.load(creatures_file)

if sound_enabled:
    background_sound = threading.Thread(target=background_sound_check, daemon=True)
    background_sound.start()

creature_creator = [
    [sg.Text(text="Lista de Criaturas", font=("Arial", font_1), text_color='#800000', background_color="black")],
    [sg.Listbox(
        values=list(creature_list.keys()), size=creature_list_resolution,
        enable_events=True, key="$creature_list"
    )],
    [sg.Button(
        button_text="Matar Criatura Selecionada", button_color=("#000000", "#FFFFFF"), key="$kill_creature",
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
        button_text="Adicionar Criatura", button_color=("#000000", "#FFFFFF"), key="$add_creature",
        font=("Arial", font_3), enable_events=True
    )]
]

creature_manager = [
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
        button_text="Atacar Criatura", button_color=("#000000", "#FFFFFF"), key="$dmg_creature",
        enable_events=True, font=("Arial", font_3)
    )],

    [sg.Text(text="O Narrador diz:", font=("Arial", font_1), text_color="#800000", background_color="black")],
    [sg.Text(
        text="", font=("Arial", font_3), text_color="#001CBF", background_color="black", visible=False,
        key="$narrator"
    )]
]

layout = [
    [
        sg.Column(creature_creator, background_color="black"),
        sg.VSeperator(),
        sg.Image(source=f'{os.path.join(os.getcwd(), "background_image.png")}'),
        sg.VSeperator(),
        sg.Column(creature_manager, background_color="black", vertical_alignment='t')
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

    # Quick Reminder: getting a value from a textbox or input, you can use values[ValueKey], but getting values from
    # window elements, like TextBoxes, you can use window[ElemKey]

    print(event, values)
    print('-----------------')
    print(creature_list)
    print()

window.close()
creatures_file.close()

'''
Programa Deve incluir:
- Usuario poder adicionar uma criatura nova facilmente (Vida, Defesa)
- Usuario poder dar dano em certa criatura (inserindo Ataque e Dano)

- DO NOT FORGET TO PRINT THAT BOOK FROM MY BROTHER
- use the Pillow library to resize the image [Just learn how to use it, no need to actually do anything with it]

https://www.geeksforgeeks.org/user-input-in-pysimplegui/
https://www.pysimplegui.org/en/latest/call%20reference/#window-the-window-object
https://pyinstaller.org/en/stable/usage.html

'''
