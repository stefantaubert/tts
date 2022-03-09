import datetime
import os
from logging import getLogger
from shutil import copyfile, copytree
from typing import Optional

from tts.defaults import DEFAULT_MEL_IN_JSON, DEFAULT_WAV_IN_JSON
from tts.utils import parse_json


def merge_mel_and_wav_out(base_dir: str, custom_name: Optional[str] = None, mel_in_json: str = DEFAULT_MEL_IN_JSON, wav_in_json: str = DEFAULT_WAV_IN_JSON):
  logger = getLogger()
  if not os.path.isfile(mel_in_json) or not os.path.isfile(wav_in_json):
    logger.error("Input files do not exist!")
    return

  mel_info = parse_json(mel_in_json)
  wav_info = parse_json(wav_in_json)

  #mel_name = mel_info["name"]
  mel_root_dir = mel_info["root_dir"]
  #wav_name = wav_info["name"]
  wav_root_dir = wav_info["root_dir"]

  merge_name = f"{datetime.datetime.now():%d.%m.%Y_%H-%M-%S}"
  if custom_name is not None:
    merge_name = f"{merge_name}_{custom_name}"
  merge_dir = os.path.join(base_dir, merge_name)
  if os.path.isdir(merge_dir):
    print("Already created.")
  else:
    os.makedirs(merge_dir, exist_ok=False)
    mel_dest_dir = os.path.join(merge_dir, f"mel")
    wav_dest_dir = os.path.join(merge_dir, f"wav")
    mel_info_file = os.path.join(merge_dir, "mel_info.json")
    wav_info_file = os.path.join(merge_dir, "wav_info.json")
    copyfile(mel_in_json, mel_info_file)
    copyfile(wav_in_json, wav_info_file)
    copytree(mel_root_dir, mel_dest_dir)
    copytree(wav_root_dir, wav_dest_dir)
    #print("Done. Output:")
    print(f"{merge_dir}")
