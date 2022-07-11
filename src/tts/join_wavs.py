import os
from logging import getLogger
from pathlib import Path
from typing import Generator, List, Tuple

import numpy as np
from audio_utils import (concatenate_audios, float_to_wav, get_sample_count,
                         wav_to_float32)
from general_utils import get_all_files_in_all_subfolders


def get_files_sorted_recursive_with_level(directory: Path, files_before_dirs: bool, level: int) -> Generator[Tuple[Path, int], None, None]:
  _, sub_directories, filenames = next(os.walk(directory))
  sub_directories = (directory / x for x in sorted(sub_directories))
  filenames = (directory / x for x in sorted(filenames))
  if files_before_dirs:
    yield from ((x, level) for x in filenames)
    for sub_dir in sub_directories:
      yield from get_files_sorted_recursive_with_level(sub_dir, files_before_dirs, level + 1)
  else:
    for sub_dir in sub_directories:
      yield from get_files_sorted_recursive_with_level(sub_dir, files_before_dirs, level + 1)
    yield from ((x, level) for x in filenames)


def get_files_sorted_recursive(directory: Path, files_before_dirs: bool) -> Generator[Tuple[Path], None, None]:
  _, sub_directories, filenames = next(os.walk(directory))
  sub_directories = (directory / x for x in sorted(sub_directories))
  filenames = (directory / x for x in sorted(filenames))
  if files_before_dirs:
    yield list(filenames)
    for sub_dir in sub_directories:
      yield from get_files_sorted_recursive(sub_dir, files_before_dirs)
  else:
    for sub_dir in sub_directories:
      yield from get_files_sorted_recursive(sub_dir, files_before_dirs)
    yield list(filenames)


def join_audios(base_dir: Path, directory: Path, silence_files: float, silence_directories: float, output_file: Path, dirs_before_files: bool, overwrite: bool) -> bool:
  logger = getLogger(__name__)
  if not directory.is_dir():
    logger.error("Directory was not found!")
    return False

  if output_file.exists() and not overwrite:
    logger.error("File already exists!")
    return False

  all_files = get_files_sorted_recursive(directory, not dirs_before_files)
  all_wav_files = tuple(tuple(file for file in file_chunk if file.suffix.lower() == ".wav")
                        for file_chunk in all_files)

  final_parts = []
  global_sr = None
  for chunk_nr, file_chunk in enumerate(all_wav_files, start=1):
    if len(file_chunk) == 0:
      continue
    is_last_chunk = chunk_nr == len(all_wav_files)
    for file_nr, file in enumerate(file_chunk, start=1):
      is_last_file = file_nr == len(file_chunk)
      wav, wav_sr = wav_to_float32(file)
      if len(wav.shape) != 1:
        logger.error(f"File {file} is not mono. Only mono files are supported! Skipped.")
        continue

      if global_sr is None:
        global_sr = wav_sr
      else:
        if wav_sr != global_sr:
          logger.error(f"File {file} has another sampling rate than the first file. Skipped.")
          continue
      final_parts.append(wav)
      if not is_last_file and silence_files > 0:
        pause_samples = np.zeros((get_sample_count(wav_sr, silence_files),))
        final_parts.append(pause_samples)

    if not is_last_chunk and silence_directories > 0:
      pause_samples = np.zeros((get_sample_count(wav_sr, silence_directories),))
      final_parts.append(pause_samples)

  if len(final_parts) == 0:
    logger.info("Nothing to concatenate!")
    return
  if len(final_parts) == 1:
    result = final_parts[0]
  else:
    logger.debug("Concatenating...")
    result = np.concatenate(tuple(final_parts), axis=-1)

  logger.debug("Saving...")
  output_file.parent.mkdir(parents=True, exist_ok=True)
  float_to_wav(result, output_file, sample_rate=global_sr)
  logger.info(f"Done. Written output to: {output_file.absolute()}")
