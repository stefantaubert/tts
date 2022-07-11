import logging
import os
from argparse import ArgumentParser
from pathlib import Path
import sys

from tts.defaults import DEFAULT_MEL_IN_JSON, DEFAULT_WAV_IN_JSON
from tts.join_wavs import join_audios
from tts.merge_mel_wav_out import merge_mel_and_wav_out

BASE_DIR_VAR = "base_dir"


def init_merge_mel_and_wav_out_parser(parser: ArgumentParser):
  parser.add_argument('--custom_name', type=str, required=False)
  parser.add_argument('--mel_in_json', type=str, default=DEFAULT_MEL_IN_JSON)
  parser.add_argument('--wav_in_json', type=str, default=DEFAULT_WAV_IN_JSON)
  return merge_mel_and_wav_out


def init_join_wavs_parser(parser: ArgumentParser):
  parser.add_argument('directory', type=Path)
  parser.add_argument('output_file', metavar="output-file", type=Path)
  parser.add_argument('-sf', '--silence-files', type=float,
                      help="Silence duration (in s) to insert while joining files in a directory.", default=0.2)
  parser.add_argument('-sd', '--silence-directories', type=float,
                      help="Silence duration (in s) to insert while joining joined files from a directory.", default=1.0)
  parser.add_argument('--dirs-before-files', action="store_true")
  parser.add_argument('-o', '--overwrite', action="store_true")
  return join_audios


def add_base_dir(parser: ArgumentParser):
  assert BASE_DIR_VAR in os.environ.keys()
  base_dir = os.environ[BASE_DIR_VAR]
  parser.set_defaults(base_dir=base_dir)


def _add_parser_to(subparsers, name: str, init_method):
  parser = subparsers.add_parser(name, help=f"{name} help")
  invoke_method = init_method(parser)
  parser.set_defaults(invoke_handler=invoke_method)
  add_base_dir(parser)
  return parser


def _init_parser():
  result = ArgumentParser()
  subparsers = result.add_subparsers(help='sub-command help')

  _add_parser_to(subparsers, "merge", init_merge_mel_and_wav_out_parser)
  _add_parser_to(subparsers, "join-wavs", init_join_wavs_parser)

  return result


def configure_logger() -> None:
  loglevel = logging.DEBUG if __debug__ else logging.INFO
  main_logger = logging.getLogger()
  main_logger.setLevel(loglevel)
  main_logger.manager.disable = logging.NOTSET
  if len(main_logger.handlers) > 0:
    console = main_logger.handlers[0]
  else:
    console = logging.StreamHandler()
    main_logger.addHandler(console)

  logging_formatter = logging.Formatter(
    '[%(asctime)s.%(msecs)03d] (%(levelname)s) %(message)s',
    '%Y/%m/%d %H:%M:%S',
  )
  console.setFormatter(logging_formatter)
  console.setLevel(loglevel)


def _process_args(args):
  params = vars(args)
  invoke_handler = params.pop("invoke_handler")
  invoke_handler(**params)


if __name__ == "__main__":
  configure_logger()
  main_parser = _init_parser()

  received_args = main_parser.parse_args()

  _process_args(received_args)
