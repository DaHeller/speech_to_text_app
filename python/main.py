# img_viewer.py

import PySimpleGUI as sg
import os.path
from deepgram import Deepgram
import asyncio
import json
import os
import sys

# First the window layout in 2 columns


# def get_api_key():
#     with open('apikey.txt', 'r') as file:
#         api_key = file.read().strip()
#     # print(api_key)
#     return api_key

def get_api_key():
    try:
        base_path = os.path.dirname(sys.executable) if getattr(
            sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        # print(f"Base path: {base_path}")  # add this line
        with open(os.path.join(base_path, 'apikey.txt'), 'r') as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        sg.popup('Something wrong with apikey',
                 'Ensure the file apikey.txt is in the same directory as the application.')
        raise SystemExit
    return api_key


def transcribe_file(filename, apikey, directory, window):
    dg_key = apikey
    dg = Deepgram(dg_key)

    MIMETYPE = filename.split('.')[-1]
    # DIRECTORY = directory

    options = {
        "punctuate": True,
        "model": 'general',
        "tier": 'enhanced'
    }
    just_file_name = filename.split('/')[-1].split('.')[0]

    # Update the status
    window['-STATUS-'].update('Transcription in progress...')

    with open(filename, "rb") as f:
        source = {'buffer': f, 'mimetype': 'audio/'+MIMETYPE}
        res = dg.transcription.sync_prerecorded(source, options)
        transcript = res.get("results", {}).get("channels", [{}])[0].get(
            "alternatives", [{}])[0].get("transcript", "")
        with open(f"{directory}/{just_file_name}.txt", "w") as f:
            f.write(transcript)
        # with open(f"{directory}/{just_file_name}.json", "w") as transcript:
        #     json.dump(res, transcript)

    # Update the status
    window['-STATUS-'].update('Transcription completed!')


file_list_column = [
    [
        sg.Text("Select the folder."),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
        )
    ],
]

# Add this block to your layout to allow choosing an output directory
output_dir_column = [
    [
        sg.Text("Choose output directory:"),
        sg.In(size=(25, 1), enable_events=True, key="-OUTDIR-"),
        sg.FolderBrowse(),
    ],
]

image_viewer_column = [
    [sg.Text("Choose an audio file from list on left:")],
    [sg.Text(size=(100, 1), key="-TOUT-")],
    [sg.Button('Transcribe', key="-TRANSCRIBE-")],
    [sg.Button('Transcribe All in Folder', key="-TRANSCRIBE_ALL-")],
    [sg.Text(size=(100, 1), key="-STATUS-")]
]

# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(output_dir_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]
]

window = sg.Window("Audio To Text", layout)
transcribe_files_lst = []
all_files_in_folder = []
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            os.path.join(folder, f)
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith((".mp3", ".mp4", ".mp2", ".aac", '.wav', '.flac', '.pcm', '.m4a', '.ogg', '.opus', '.webm'))
        ]
        # print(fnames)
        all_files_in_folder = fnames
        fnames_display = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith((".mp3", ".mp4", ".mp2", ".aac", '.wav', '.flac', '.pcm', '.m4a', '.ogg', '.opus', '.webm'))
        ]

        window["-FILE LIST-"].update(fnames_display)
    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            # Update the value of "-TOUT-" in the values dictionary
            values["-TOUT-"] = filename
            transcribe_files_lst.append(filename)
            window["-TOUT-"].update(filename)
        except Exception as e:
            print(e)
    elif event == "-TRANSCRIBE-":
        # ilename = values["-TOUT-"]
        if transcribe_files_lst:
            filename = transcribe_files_lst[-1]
        else:
            sg.popup(
                'Choose a file', title='Error')
            continue
        # print(filename)
        api_key = get_api_key()
        # print(api_key)
        output_dir = values["-OUTDIR-"]
        try:
            transcribe_file(filename, api_key, output_dir, window)
        except Exception as e:
            sg.popup(
                'Something wrong with apikey or directorys not selected', title='Error')
            print(e)
    elif event == "-TRANSCRIBE_ALL-":
        if all_files_in_folder:
            pass
        else:
            sg.popup(
                'Choose a directory', title='Error')
            continue
        # print(filename)
        print(all_files_in_folder)
        api_key = get_api_key()
        # print(api_key)
        output_dir = values["-OUTDIR-"]
        for filename in all_files_in_folder:
            try:
                transcribe_file(filename, api_key, output_dir, window)
            except Exception as e:
                sg.popup(
                    'Something wrong with apikey or directorys not selected', title='Error')
                print(e)

    # window.close()
