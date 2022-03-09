import os
from argparse import ArgumentParser
import sys

from tts.defaults import DEFAULT_MEL_IN_JSON, DEFAULT_WAV_IN_JSON
from tts.merge_mel_wav_out import merge_mel_and_wav_out

BASE_DIR_VAR = "base_dir"


def init_merge_mel_and_wav_out_parser(parser: ArgumentParser):
  parser.add_argument('--custom_name', type=str, required=False)
  parser.add_argument('--mel_in_json', type=str, default=DEFAULT_MEL_IN_JSON)
  parser.add_argument('--wav_in_json', type=str, default=DEFAULT_WAV_IN_JSON)
  return merge_mel_and_wav_out


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

  return result


def _process_args(args):
  params = vars(args)
  invoke_handler = params.pop("invoke_handler")
  invoke_handler(**params)


if __name__ == "__main__":
  main_parser = _init_parser()

  received_args = main_parser.parse_args()

  _process_args(received_args)