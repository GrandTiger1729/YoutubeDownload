from __future__ import unicode_literals
import yt_dlp, urllib.error

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os, json
import threading

real_path = os.path.realpath(__file__)
dir_path = os.path.dirname(real_path)
os.chdir(dir_path)

with open('config.json', 'r') as f:
    config = json.load(f)

if not config.get('output_path'):
    config['output_path'] = dir_path
if not config.get('cookiefile'):
    config['cookiefile'] = dir_path+r'\youtube.com_cookies.txt'

def hook(d):
    if d['status'] == 'downloading':
        download_progressbar['value'] = round(d['downloaded_bytes']/d['total_bytes']*100, 1)
        text = f"[download] {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']} ETA {d['_eta_str']}"
        download_progress_var.set(d['_percent_str'])
        terminal.insert('end', text+'\n')
        print(d.keys())

ydl_opts = {
    'format': 'best', # test
    'outtmpl': '%(extractor_key)s\%(title)s.%(ext)s',
    'default_search': 'auto',
    'cookiefile': 'youtube.com_cookies.txt', # <- this can download age-restricted video
    'progress_hooks': [hook]
}

formats = ('best', 'worst', 'bestaudio', 'worstaudio')

def start_thread(func):
    # download()
    new_threading = threading.Thread(target=func)
    new_threading.start()

def download():
    ydl_opts['format'] = format_opt.get()
    outtmpl = ydl_opts['outtmpl']
    ydl_opts['outtmpl'] = path_entry.get() + '\\' + ydl_opts['outtmpl']
    config['cookiefile'] = cookiefile_entry.get(); ydl_opts['cookiefile'] = config['cookiefile']
    downloadframe.pack()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url.get()])
        except yt_dlp.utils.DownloadError as DownloadError:
            if type(DownloadError.exc_info[1]) == urllib.error.URLError:
                print('Unknown Url')
            elif type(DownloadError.exc_info[1]) == yt_dlp.utils.ExtractorError:
                print('Join this channel to get access to members-only content like this video, and other exclusive perks.')
        except Exception as ex:
            print('\n', type(ex).__name__)
    downloadframe.pack_forget()
    ydl_opts['outtmpl'] = outtmpl


def lever_controler(lever, frame):
    if lever.get():
        frame.pack()
    else:
        frame.pack_forget()

def path_browse():
    path = filedialog.askdirectory(initialdir="", title="Select a directory")
    path_entry.delete(0, 'end')
    path_entry.insert(0, path)

def cookiefile_browse():
    cookiefile = filedialog.askopenfilename(initialdir="", title="Select a cookiefile")
    cookiefile_entry.delete(0, 'end')
    cookiefile_entry.insert(0, cookiefile)

window = tk.Tk()
window.title('YoutubeDownloader')
window.resizable(False, False)
window.geometry('650x400')

ttk.Label(window, text='this is a youtube video downloader').pack(side='top')

optionframe = ttk.Frame(window)
optionframe.pack()

ttk.Label(optionframe, text='url: (please enter some url that you want to download)').pack(anchor='w')
url = ttk.Entry(optionframe, width=130)
url.focus(); url.pack()
ttk.Label(optionframe, text='format: (please select a option you want)').pack(anchor='w')
format_opt = ttk.Combobox(optionframe, width=130, values=formats)
format_opt.insert(0, 'best'); format_opt.pack()

advanced_lever = tk.IntVar(optionframe)

advanced_checkbutton = ttk.Checkbutton(optionframe, text='Advanced setting', variable=advanced_lever, command=lambda: lever_controler(advanced_lever, advanced_options))
advanced_checkbutton.pack(anchor='w')

advanced_options = tk.LabelFrame(optionframe, text='')
ttk.Label(advanced_options, text='path: ').grid(row=0, column=0, sticky='w')
path_entry = ttk.Entry(advanced_options, width=80)
path_entry.insert(0, config['output_path']); path_entry.grid(row=0, column=1)
path_browse_button = ttk.Button(advanced_options, text='Browse', command=path_browse)
path_browse_button.grid(row=0, column=2)

ttk.Label(advanced_options, text='cookiefile: ').grid(row=1, column=0, sticky='w')
cookiefile_entry = ttk.Entry(advanced_options, width=80)
cookiefile_entry.insert(0, config['cookiefile']); cookiefile_entry.grid(row=1, column=1)
cookiefile_browse_button = ttk.Button(advanced_options, text='Browse', command=cookiefile_browse)
cookiefile_browse_button.grid(row=1, column=2)

downloadframe = ttk.Frame(optionframe)
download_progress_frame = ttk.Frame(downloadframe)
download_progress_frame.pack()
download_progressbar = ttk.Progressbar(download_progress_frame, orient='horizontal', mode='determinate', length=600)
download_progressbar.grid(row=0, column=0)
download_progress_var = tk.StringVar(downloadframe, value='0 %')
ttk.Label(download_progress_frame, textvariable=download_progress_var).grid(row=0, column=1)
download_moreinfo = ttk.Frame(downloadframe)

download_moreinfo_lever = tk.IntVar(downloadframe)

download_moreinfo_checkbutton = ttk.Checkbutton(downloadframe, text='More Info', variable=download_moreinfo_lever, command=lambda: lever_controler(download_moreinfo_lever, download_moreinfo))
download_moreinfo_checkbutton.pack(anchor='w')
clean_terminal_button = ttk.Button(download_moreinfo, text='clean', command=lambda: terminal.delete(0.0, 'end'))
clean_terminal_button.pack(side='bottom', anchor='e')
terminal = scrolledtext.ScrolledText(download_moreinfo, background='black', foreground='white', width=90, height=10)
terminal.pack(side='bottom')

startbutton = ttk.Button(window, text='download', command=lambda: start_thread(download))
startbutton.pack(side='bottom')

window.mainloop()

with open('config.json', 'w') as f:
    json.dump(config, f, indent=4, separators=(',', ': '))