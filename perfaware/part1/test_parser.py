import parser
import tempfile
import subprocess

def test_listing_0037():
    MACHINE_CODE_FILENAME = 'listing_0037_single_register_mov'

    lines = parser.decode_executable(MACHINE_CODE_FILENAME)
    print(f'Disassembled 0037: {lines}')

    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp:
        tmp.write("\n".join(lines))
        asm_path = tmp.name
    print(f'Wrote 0037 asm to {asm_path}')

    executable_path = tempfile.mktemp()
    nasm_cmd = [
        'nasm',
        asm_path,
        '>',
        executable_path
    ]
    subprocess.run(nasm_cmd, check=True)
    print(f'Assembled disassembled 0037 asm to {executable_path}')

    with open(executable_path, mode='r+b') as reconstructed_executable, \
        open(MACHINE_CODE_FILENAME, mode='r+b') as original_executable:
        reconstructed_contents = reconstructed_executable.read()
        original_contents = original_executable.read()
        assert reconstructed_contents == original_contents

def test_listing_0038():
    lines = parser.decode_executable('listing_0038_many_register_mov')
    print(lines)

test_listing_0037()

