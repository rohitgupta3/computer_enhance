# Note: check out https://edge.edx.org/c4x/BITSPilani/EEE231/asset/8086_family_Users_Manual_1_.pdf
# p160 or so of the PDF, where it says "Machine Instruction Encoding and Decoding"
import logging

logging.basicConfig(
        level=logging.WARN,
        format="%(asctime)s %(levelname)1.1s %(module)s:%(lineno)d - %(message)s",
)

import sys

def byte_to_bitstring(some_int):
    """ e.g.
    some_int = some_bytes[0]
    eight_bits = byte_to_bitstring(some_int)
    """
    return format(some_int, '08b')

def get_readable_reg(reg, width_bit):
    if reg == '000' and width_bit == '0':
        return 'al'
    elif reg == '000' and width_bit == '1':
        return 'ax'
    elif reg == '001' and width_bit == '0':
        return 'cl'
    elif reg == '001' and width_bit == '1':
        return 'cx'
    elif reg == '010' and width_bit == '0':
        return 'dl'
    elif reg == '010' and width_bit == '1':
        return 'dx'
    elif reg == '011' and width_bit == '0':
        return 'bl'
    elif reg == '011' and width_bit == '1':
        return 'bx'
    elif reg == '100' and width_bit == '0':
        return 'ah'
    elif reg == '100' and width_bit == '1':
        return 'sp'
    elif reg == '101' and width_bit == '0':
        return 'ch'
    elif reg == '101' and width_bit == '1':
        return 'bp'
    elif reg == '110' and width_bit == '0':
        return 'dh'
    elif reg == '110' and width_bit == '1':
        return 'si'
    elif reg == '111' and width_bit == '0':
        return 'bh'
    elif reg == '111' and width_bit == '1':
        return 'di'


###########
# opcode starts with 100010
###########

def get_more_bytes_needed_100010(two_bytes):
    second_byte = two_bytes[1]
    # second_bits = bin(second_byte)[2:]
    second_bits = byte_to_bitstring(second_byte)
    logging.debug(f'second_bits: {second_bits}')
    mod = second_bits[:2]
    if mod == '11':
        return 0
    elif mod == '10':
        return 2
    elif mod == '01':
        return 1
    elif mod == '00':
        r_slash_m = second_bits[5:]
        if r_slash_m == '110':
            return 2
        else:
            return 0


def parse_100010(some_bytes):
    first_byte = some_bytes[0]
    first_bits = byte_to_bitstring(first_byte)
    destination_bit = first_bits[6]
    width_bit = first_bits[7]

    second_byte = some_bytes[1]
    second_bits = byte_to_bitstring(second_byte)
    mod = second_bits[:2]
    reg = second_bits[2:5]
    r_slash_m = second_bits[5:]

    if mod == '11':
        logging.debug('this is a register-to-register mov')
        asm = decode_reg_to_reg_mov(destination_bit, width_bit, reg, r_slash_m)
        logging.debug(asm)
    else:
        logging.debug('this is memory mov')
        asm = decode_memory_mov(destination_bit, width_bit, reg, r_slash_m, mod, some_bytes[2:])

    return asm

# First in each group
MOV_REGMEM_REGMEM_PREFIX = '100010'
ADD_REGMEM_REGMEM_PREFIX = '000000'
SUB_REGMEM_REGMEM_PREFIX = '001010'
CMP_REGMEM_REG_PREFIX    = '001110'
def get_more_bytes_needed(two_bytes):
    first_byte = two_bytes[0]
    first_bits = byte_to_bitstring(first_byte)

    # if first_bits[0:6] == '100010':
    if first_bits[0:6] in [
        MOV_REGMEM_REGMEM_PREFIX,
        ADD_REGMEM_REGMEM_PREFIX,
        SUB_REGMEM_REGMEM_PREFIX,
        CMP_REGMEM_REG_PREFIX
    ]:
        logging.debug('this is register-to-register or memory-to-register or register-to-memory')
        # TODO: don't love the naming
        return get_more_bytes_needed_100010(two_bytes)
    elif first_bits[0:4] == '1011':
        logging.debug('this is an immediate-to-register mov')
        return get_more_bytes_needed_1011(two_bytes)
    else:
        raise ValueError(f'{two_bytes} not supported')


def get_int_string_from_bytes(displacement_bytes):
    int_value_i: int = int.from_bytes(displacement_bytes, byteorder='little')
    int_value_s: str = str(int_value_i)
    return int_value_s


def get_readable_eff_add(r_slash_m_bits_string, mod, displacement_bytes):
    if r_slash_m_bits_string == '000':
        core_string = 'bx + si'
    if r_slash_m_bits_string == '001':
        core_string = 'bx + di'
    if r_slash_m_bits_string == '010':
        core_string = 'bp + si'
    if r_slash_m_bits_string == '011':
        core_string = 'bp + di'
    if r_slash_m_bits_string == '100':
        core_string = 'si'
    if r_slash_m_bits_string == '101':
        core_string = 'di'
    if r_slash_m_bits_string == '110' and mod != '00':
        core_string = 'bp'
    if r_slash_m_bits_string == '111':
        core_string = 'bx'

    if mod == '00':
        return f'[{core_string}]'

    int_string_displacement = get_int_string_from_bytes(displacement_bytes)

    if r_slash_m_bits_string == '110' and mod == '00':
        return f'[{int_string_displacement}]'

    if int_string_displacement == '0':
        return f'[{core_string}]'
    else:
        return f'[{core_string} + {int_string_displacement}]'


def decode_memory_mov(
    destination_bit,
    width_bit,
    reg_bits_string,
    r_slash_m_bits_string,
    mod,
    displacement_bytes
):
    reg_decoded = get_readable_reg(reg_bits_string, width_bit)
    r_slash_m_decoded = get_readable_eff_add(
            r_slash_m_bits_string,
            mod,
            displacement_bytes
    )
    # TODO: DRY with `decode_reg_to_reg_mov`?
    if destination_bit == '1':
        first_token = reg_decoded
        second_token = r_slash_m_decoded
    elif destination_bit == '0':
        first_token = r_slash_m_decoded
        second_token = reg_decoded
    asm_string = f'mov {first_token}, {second_token}'
    return asm_string


def decode_reg_to_reg_mov(destination_bit, width_bit, reg_bits_string, r_slash_m_bits_string):
    reg_decoded = get_readable_reg(reg_bits_string, width_bit)
    r_slash_m_decoded = get_readable_reg(r_slash_m_bits_string, width_bit)
    if destination_bit == '1':
        first_token = reg_decoded
        second_token = r_slash_m_decoded
    elif destination_bit == '0':
        first_token = r_slash_m_decoded
        second_token = reg_decoded
    asm_string = f'mov {first_token}, {second_token}'
    return asm_string


def get_more_bytes_needed_1011(two_bytes):
    first_byte = two_bytes[0]
    first_bits = byte_to_bitstring(first_byte)
    logging.debug(f'first_bits: {first_bits}')
    width_bit = first_bits[4]
    # reg = first_bits[5:]
    # reg_decoded = get_readable_reg(reg, width_bit)
    # register_size_bytes = get_size_of_reg_in_bytes(reg_decoded)
    # return register_size_bytes
    return 1 if width_bit == '1' else 0

# TODO: could DRY with `get_more_bytes_needed_1011`
def parse_1011(some_bytes):
    first_byte = some_bytes[0]
    first_bits = byte_to_bitstring(first_byte)
    logging.debug(f'first_bits: {first_bits}')
    width_bit = first_bits[4]
    reg = first_bits[5:]
    reg_decoded = get_readable_reg(reg, width_bit)
    immediate_s = get_int_string_from_bytes(some_bytes[1:])
    return f'mov {reg_decoded}, {immediate_s}'


# TODO: could DRY with `get_more_bytes_needed` / re-architect generally
def parse_next_group(some_bytes):
    first_byte = some_bytes[0]
    first_bits = byte_to_bitstring(first_byte)

    if first_bits[0:6] == '100010':
        logging.debug('this is a register-to-register or memory-to-register or register-to-memory mov')
        # TODO: don't love the naming
        return parse_100010(some_bytes)
    elif first_bits[0:4] == '1011':
        logging.debug('this is an immediate-to-register mov')
        return parse_1011(some_bytes)
    else:
        raise ValueError(f'{two_bytes} not supported')


def decode_machine_code(file_contents):
    lines = []
    while True:
        if len(file_contents) == 0:
            break
        two_bytes = file_contents[:2]
        file_contents = file_contents[2:]
        more_bytes_needed = get_more_bytes_needed(two_bytes)
        remaining_bytes = file_contents[:more_bytes_needed]
        file_contents = file_contents[more_bytes_needed:]
        asm = parse_next_group(two_bytes + remaining_bytes)
        logging.info(f'asm: {asm}')
        lines.append(asm)

    return lines

def decode_executable(filename):
    # TODO: relative path
    with open(f'/Users/rgmbp/projects/computer_enhance/perfaware/part1/{filename}', mode='r+b') as fd:
        file_contents = fd.read()

    lines = decode_machine_code(file_contents)
    lines = [
        f'; {filename} disassembly:',
        'bits 16',
        *lines
    ]
    return lines

# def parse_regmem_regmem():
#     pass
# 
# def parse_machine_code(machine_code):
#     parse_regmem_regmem()

if __name__ == '__main__':
    # FILENAME = 'listing_0037_single_register_mov'
    # FILENAME = 'listing_0038_many_register_mov'
    # FILENAME = 'listing_0039_more_movs'
    FILENAME = sys.argv[1]
    lines = decode_executable(FILENAME)
    for line in lines:
        logging.info(line)
