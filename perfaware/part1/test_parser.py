import logging

logging.basicConfig(
        level=logging.WARN,
        format="%(asctime)s %(levelname)1.1s %(module)s:%(lineno)d - %(message)s",
)

import parser
import tempfile
import subprocess
import os
import mock

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


test_decode_executable('listing_0037_single_register_mov')
test_decode_executable('listing_0038_many_register_mov')
test_decode_executable('listing_0039_more_movs')

def test_decode_regmem_tofrom_reg():
    pass


# There will be some code like this
# if bytes_start_with('100010')
#     or bytes_start_with('000000')
#     or bytes_start_with('001010')
#     or bytes_start_with('001110'):
#     asm_after_operator = parse_regmem_regmem(some_bytes)
@mock.patch('parser.parse_regmem_regmem')
def test_grouped_correctly(mock_parse_regmem_regmem):
    # Example bits (replace this with your actual bit sequence)
    bit_sequence = "0100100001100101011011000110110001101111"
    byte_values = [int(bit_sequence[i:i+8], 2) for i in range(0, len(bit_sequence), 8)]
    machine_code = bytes(byte_values)
    parser.parse_machine_code(machine_code)
    mock_parse_regmem_regmem.assert_called_once()
