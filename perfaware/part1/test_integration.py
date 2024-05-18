import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--log_level')
args = parser.parse_args()
log_level = args.log_level.upper() if args.log_level else 'DEBUG'

import logging

logging.basicConfig(
   level=getattr(logging, log_level),
   format="%(asctime)s %(levelname)1.1s %(module)s:%(lineno)d - %(message)s",
)

import parser
import tempfile
import subprocess
import os

TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_artifacts')

def test_decode_executable(filename):
    lines = parser.decode_executable(filename)
    logging.info(f'Disassembled {filename}: {lines}')

    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.asm', dir=TEST_DIR) as tmp:
        tmp.write("\n".join(lines))
        asm_path = tmp.name
    logging.info(f'Wrote {filename} asm to {asm_path}')

    executable_path = tempfile.mktemp(dir=TEST_DIR)
    nasm_cmd = [
        'nasm',
        asm_path,
        '-o',
        executable_path
    ]
    subprocess.run(nasm_cmd, check=True)
    logging.info(f'Assembled disassembled {filename} asm to {executable_path}')

    with open(executable_path, mode='r+b') as reconstructed_executable, \
        open(filename, mode='r+b') as original_executable:
        reconstructed_contents = reconstructed_executable.read()
        original_contents = original_executable.read()
        assert reconstructed_contents == original_contents



if __name__ == '__main__':
#     # FILENAME = 'listing_0037_single_register_mov'
#     # FILENAME = 'listing_0038_many_register_mov'
#     # FILENAME = 'listing_0039_more_movs'
#     FILENAME = sys.argv[1]
#     lines = decode_executable(FILENAME)
#     for line in lines:
#         logging.info(line)
    # test_decode_executable('listing_0037_single_register_mov')
    # test_decode_executable('listing_0038_many_register_mov')
    # test_decode_executable('listing_0039_more_movs')
    test_decode_executable('listing_0041_add_sub_cmp_jnz')