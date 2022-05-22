#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Lucas Vidor Migotto'
__date__ = '$May 22, 2022 08:15:00 AM$'

import logging
import speech_recognition as sr
from os import sys
from os import remove
from time import time
from pytube import YouTube
from pydub import AudioSegment

logging.basicConfig(
    format='[%(asctime)s][%(levelname)s]%(funcName)s(%(lineno)d): %(message)s',
    level='DEBUG')
logging.getLogger('pytube').setLevel('INFO')

VIDEO_LINK = ''
ERROR_MESSGES = {
    '1001': {'code': 1, 'message': 'Audio from video could not be saved'},
    '1002': {'code': 1, 'message': 'Audio could not be converted'},
    '1003': {'code': 1, 'message': 'Audio could not be trancripted'},
    '1004': {'code': 1, 'message': 'Google could not understand the audio'}
}


def exit_error(code, err=None):
    logging.error(f"{ERROR_MESSGES[str(code)]['message']} - {err}")
    sys.exit(ERROR_MESSGES[str(code)][['code']])


def save_youtube_audio_stream(video_link):
    try:
        stream = YouTube(VIDEO_LINK).streams.filter(
            only_audio=True,
            file_extension='mp4').first()

        logging.debug(f"Video audio streams: ${stream}")

        audio_filename = f"{int(time())}.mp4"
        stream.download(filename=audio_filename)

        return audio_filename

    except Exception as err:
        logging.exception(f"Exception: {err}")
        return exit_error(1001, err)


def convert_audio_to_wav(mp4_filename):
    try:
        logging.debug(f"Converting file {mp4_filename}")
        wav_audio = AudioSegment.from_file(mp4_filename, 'mp4')

        wav_filename = f"{int(time())}.wav"
        logging.debug(f"Saving converted audio in {wav_filename}")
        wav_audio.export(wav_filename, format="wav")

        logging.debug(f"Removing mp4 file {mp4_filename}")
        remove(mp4_filename)

        return wav_filename

    except Exception as err:
        logging.exception(f"Exception: {err}")
        return exit_error(1002, err)


def recog_and_transcript_audio(wav_filename):
    try:
        audio = sr.AudioFile(wav_filename)
        recog = sr.Recognizer()
        with audio as source:
            audio_record = recog.record(source)

        transcript = recog.recognize_google(audio_record, language='pt-BR')

        return transcript

    except sr.UnknownValueError:
        return exit_error(1004)
    except Exception as err:
        logging.exception(f"Exception: {err}")
        return exit_error(1003, err)


def main():
    try:
        mp4_file = save_youtube_audio_stream(VIDEO_LINK)

        wav_file = convert_audio_to_wav(mp4_file)

        transcript = recog_and_transcript_audio(wav_file)

        print(transcript)

    except Exception as err:
        print(err)
        sys.exit(1)


if __name__ == '__main__':
    main()
