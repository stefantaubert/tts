import os
from logging import getLogger
from shutil import copytree
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

  mel_name = mel_info["name"]
  mel_root_dir = mel_info["root_dir"]
  wav_name = wav_info["name"]
  wav_root_dir = wav_info["root_dir"]

  merge_name = f"{mel_name}+{wav_name}"
  if custom_name is not None:
    merge_name = f"{custom_name}=={merge_name}"
  merge_dir = os.path.join(base_dir, merge_name)
  if os.path.isdir(merge_dir):
    print("Already created.")
  else:
    os.makedirs(merge_dir, exist_ok=False)
    mel_dest_dir = os.path.join(merge_dir, f"mel_{mel_name}")
    wav_dest_dir = os.path.join(merge_dir, f"wav_{wav_name}")
    copytree(mel_root_dir, mel_dest_dir)
    copytree(wav_root_dir, wav_dest_dir)
    print("Done.")
    print(f"Output: {merge_dir}")
