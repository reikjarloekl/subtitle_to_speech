#!/usr/bin/python
from gtts import gTTS
from subprocess import call
import os
import typer
import random
import string


def convert_string_to_wav(text, outfile_path, lang='en', delay=0, tempo=1.2):
    """
    Convert text into a wav file

    Args:
        :param text: the text to speech in latin encoding if wanter
        :param outfile_path: where to write the outfile
        :param lang: the language, english by default
        :param delay: in seconds
        :param tempo: speed of speech, google defaut is 1 but too slow

    """
    tts = gTTS(text=text, lang=lang, slow=False).save(outfile_path+'.tmp.mp3')
    call(["mpg123", "-w", outfile_path+'.tmp.wav', outfile_path+'.tmp.mp3'])
    call(["sox", outfile_path+'.tmp.wav', outfile_path, "tempo", str(tempo), "delay", str(delay)])
    os.remove(outfile_path+'.tmp.wav')
    os.remove(outfile_path+'.tmp.mp3')
    
def convert_str_to_wav_in_docker_command(srt_file="", outfilename="", lang='', tempo:float = 1.2):
    """
    Convert a subtitle file found in /data into a wav file

    Args:
        :param srt_file: filename of the subtitle file in srt format
        :param outfilename: filename of the outfile
        :param lang: the language, english by default
        :param tempo: speed of speech, google defaut is 1 but too slow

    """
    if srt_file == "":
        filenames = os.listdir('/data/')
    else:
        filenames = [srt_file, ]
    for file_name in filenames:
        if file_name[-4:] == ".srt":
            typer.echo ("language of %s: %s" % (file_name, lang))
            convert_str_to_wav_command(
                srt_file="/data/%s" % file_name,
                outfile_path="/data/%s.wav" % (file_name[:-4] if outfilename == "" else outfilename),
                lang=get_language_from_filename(file_name) if lang == "" else lang,
                tempo=tempo,
            )
    
def get_language_from_filename(file_name):
    try:
        rindex = file_name[:-4].rindex('.')+1
        if rindex == 0:
            raise Exception()
        return file_name[rindex:-4]
    except Exception:
        typer.echo("No language found. To specify it, ends the filename with .fr.srt or .en.srt") 
        return "en"

def convert_str_to_wav_command(srt_file, outfile_path, lang='en', tempo:float = -1.0):
    """
    Convert a subtitle file into a wav file

    Args:
        :param srt_file: path to the subtitle file in srt format
        :param outfile_path: where to write the outfile
        :param lang: the language, english by default
        :param tempo: speed of speech, google defaut is 1 but too slow

    """
    if tempo < 0 :
        if lang == "fr" :
            tempo = 1.35
        else:
            tempo = 1.2
    f = open(srt_file, 'r')
    lines = f.readlines()
    line_id=0
    part_files=[]
    ran_str=lang+''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    tmp_outfile_path="/tmp/%s-out.wav"%ran_str
    while line_id+2<len(lines):
        try:
            name = lines[line_id+0].replace("\r","")[:-1]
            timming = lines[line_id+1].replace("\r","")[:-1]
            text = lines[line_id+2].replace("\r","")[:-1]
            start_time = timming.split(" --> ")[0]
            start_time_parts = start_time.split(":")
            seconds = start_time_parts[2].split(".")[0]
            delay = ((int(start_time_parts[0]) * 60 + int(start_time_parts[1])) * 60 + int(seconds))
            part_files.append("/tmp/%s-%s.wav"%(ran_str,name))
            convert_string_to_wav(
                text=text,
                outfile_path=part_files[-1],
                lang=lang,
                delay=delay,
                tempo=tempo,
            )
            line_id+=4
        except Exception as e:
            typer.echo("Error at line " + str(line_id) + " in " + srt_file)
            raise e
        #if len(part_files) == 2:
        #    call(['sox', '-m'] + part_files + [tmp_outfile_path])
        #elif len(part_files) > 2:
        #    call(['sox', '-m'] + part_files[:-1] + [tmp_outfile_path] + [tmp_outfile_path+'-out.wav'])
        #    call(['mv', tmp_outfile_path+'-out.wav', tmp_outfile_path])
    call(['sox', '-m'] + part_files + [tmp_outfile_path, 'norm'])
    call(['mv', tmp_outfile_path, outfile_path])
    call(["sox", outfile_path, outfile_path[:-3]+'ogg'])
    call(['rm'] + part_files)
    
    
#convert subtitle (.srt) to speech (.wav) using google API
if __name__ == '__main__':
    typer.run(convert_str_to_wav_command)
