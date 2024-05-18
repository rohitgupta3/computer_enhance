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

def test_decode_executable_bin(filename):
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

def test_decode_executable_asm(original_executable_filename, asm_ground_truth_filename):
    lines = parser.decode_executable(original_executable_filename, num_lines=68)
    logging.info(f'Disassembled {original_executable_filename}: {lines}')

    # with open(f'{original_executable_filename}.asm', mode='r') as original_asm_file:
    with open(f'{asm_ground_truth_filename}', mode='r') as original_asm_file:
        original_asm = original_asm_file.read()

    original_asm = original_asm.split('\n')
    for idx, (original_line, disassembled_line) in enumerate(zip(original_asm, lines)):
        # breakpoint()
        # `idx` list below captures ones where 226 == -30, `bp` == `bp+0`, and such
        # if idx not in [22, 29]:
        if original_line.replace(' ', '') != disassembled_line.replace(' ', ''):
            logging.warning(f'line {idx} not equal')
            logging.warning(f'original_line: {original_line}')
            logging.warning(f'disassembled_line: {disassembled_line}')
            logging.warning('')



if __name__ == '__main__':
#     # FILENAME = 'listing_0037_single_register_mov'
#     # FILENAME = 'listing_0038_many_register_mov'
#     # FILENAME = 'listing_0039_more_movs'
#     FILENAME = sys.argv[1]
#     lines = decode_executable(FILENAME)
#     for line in lines:
#         logging.info(line)
    # test_decode_executable_bin('listing_0037_single_register_mov')
    # test_decode_executable_bin('listing_0038_many_register_mov')
    # test_decode_executable_bin('listing_0039_more_movs')
    # test_decode_executable_bin('listing_0041_add_sub_cmp_jnz')
    test_decode_executable_asm(
        'listing_0041_add_sub_cmp_jnz',
        'listing_0041_add_sub_cmp_jnz_testing.asm'
    )
