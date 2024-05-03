import parser
import tempfile
import subprocess
import os

TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_artifacts')

def test():
    # MACHINE_CODE_FILENAME = 'listing_0037_single_register_mov'
    MACHINE_CODE_FILENAME = 'listing_0038_many_register_mov'

    lines = parser.decode_executable(MACHINE_CODE_FILENAME)
    print(f'Disassembled 0037: {lines}')

    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.asm', dir=TEST_DIR) as tmp:
        tmp.write("\n".join(lines))
        asm_path = tmp.name
    print(f'Wrote 0037 asm to {asm_path}')

    executable_path = tempfile.mktemp(dir=TEST_DIR)
    nasm_cmd = [
        'nasm',
        asm_path,
        '-o',
        executable_path
    ]
    subprocess.run(nasm_cmd, check=True)
    print(f'Assembled disassembled 0037 asm to {executable_path}')

    with open(executable_path, mode='r+b') as reconstructed_executable, \
        open(MACHINE_CODE_FILENAME, mode='r+b') as original_executable:
        reconstructed_contents = reconstructed_executable.read()
        original_contents = original_executable.read()
        assert reconstructed_contents != original_contents

test()
