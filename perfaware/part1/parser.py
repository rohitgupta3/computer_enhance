# Note: check out https://edge.edx.org/c4x/BITSPilani/EEE231/asset/8086_family_Users_Manual_1_.pdf
# p160 or so of the PDF, where it says "Machine Instruction Encoding and Decoding"
import logging

logging.basicConfig(
        level=logging.WARN,
        format="%(asctime)s %(levelname)1.1s %(module)s:%(lineno)d - %(message)s",
)

import sys


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


def get_more_bytes_needed_100010(two_bytes):
    second_byte = two_bytes[1]
    second_bits = bin(second_byte)[2:]
    logging.info(f'second_bits: {second_bits}')
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


def get_more_bytes_needed(two_bytes):
    first_byte = two_bytes[0]
    first_bits = bin(first_byte)[2:]

    if first_bits[0:6] == '100010':
        logging.info('this is a register-to-register or memory-to-register or register-to-memory mov')
        # TODO: don't love the naming
        return get_more_bytes_needed_100010(two_bytes)
    elif first_bits[0:4] == '1011':
        logging.info('this is an immediate-to-register mov')
        return get_more_bytes_needed_1011(two_bytes)
    else:
        raise ValueError(f'{two_bytes} not supported')


def parse_100010(some_bytes):
    first_byte = some_bytes[0]
    first_bits = bin(first_byte)[2:]
    destination_bit = first_bits[6]
    width_bit = first_bits[7]

    second_byte = some_bytes[1]
    second_bits = bin(second_byte)[2:]
    mod = second_bits[:2]
    reg = second_bits[2:5]
    r_slash_m = second_bits[5:]

    if mod == '11':
        logging.info('this is a register-to-register mov')
        asm = decode_reg_to_reg_mov(destination_bit, width_bit, reg, r_slash_m)
        logging.info(asm)
    elif mod == '10':
        logging.info('this is memory mov with 16-bit displacement')
        asm = decode_memory_mov_16_bit_disp(destination_bit, width_bit, reg, r_slash_m, some_bytes[1:])
    elif mod == '01':
        logging.info('this is memory mov with 8-bit displacement')
        asm = decode_memory_mov_8_bit_disp(destination_bit, width_bit, reg, r_slash_m, some_bytes[1:])
    elif mod == '00':
        logging.info('this is memory mov with no displacement*')
        asm = decode_memory_mov_no_disp(destination_bit, width_bit, reg, r_slash_m, some_bytes[1:])

    return asm


def get_int_string_displacement(displacement_bytes):
    # TODO: using default (big) endianness; confirm
    int_value_i: int = int.from_bytes(displacement_bytes)
    int_value_s: str = str(int_value_i)
    return int_value_s


def get_readable_eff_add(r_slash_m_bits_string, mod, displacement_bytes):
    int_string_displacement = get_int_string_displacement(displacement_bytes)
    if mod == '10' and r_slash_m_bits_string == '000':
        return f'[bx + si + {int_string_displacement}]'
    if mod == '10' and r_slash_m_bits_string == '001':
        return f'[bx + di + {int_string_displacement}]'
    if mod == '10' and r_slash_m_bits_string == '010':
        return f'[bp + si + {int_string_displacement}]'
    if mod == '10' and r_slash_m_bits_string == '011':
        return f'[bp + di + {int_string_displacement}]'
    if mod == '10' and r_slash_m_bits_string == '100':
        return f'[si + {int_string_displacement}]'
    if mod == '10' and r_slash_m_bits_string == '101':
        return f'[di + {int_string_displacement}]'
    if mod == '10' and r_slash_m_bits_string == '110':
        return f'[bp + {int_string_displacement}]'
    if mod == '10' and r_slash_m_bits_string == '111':
        return f'[bx + {int_string_displacement}]'
    # TODO: finish for mod '01' and mod '00'

def decode_memory_mov_16_bit_disp(
    destination_bit,
    width_bit,
    reg_bits_string,
    r_slash_m_bits_string,
    displacement_bytes
):
    reg_decoded = get_readable_reg(reg_bits_string, width_bit)
    r_slash_m_decoded = get_readable_eff_add(r_slash_m_bits_string, mod='10', displacement_bytes)


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


def parse_two_bytes(two_bytes):
    first_byte = two_bytes[0]
    first_bits = bin(first_byte)[2:]

    opcode = first_bits[0:6]
    if opcode == '100010':
        logging.info('this is a register-to-register or memory-to-register or register-to-memory mov')
    destination_bit = first_bits[6]
    logging.info(f'destination_bit: {destination_bit}')
    width_bit = first_bits[7]
    logging.info(f'width_bit: {width_bit}')

    second_byte = two_bytes[1]
    second_bits = bin(second_byte)[2:]
    logging.info(f'second_bits: {second_bits}')
    mod = second_bits[:2]
    reg = second_bits[2:5]
    r_slash_m = second_bits[5:]
    logging.info(f'mod: {mod}')
    logging.info(f'reg: {reg}')
    logging.info(f'r_slash_m: {r_slash_m}')

    if opcode == '100010' and mod == '11':
        logging.info('this is a register-to-register mov')
        asm = decode_reg_to_reg_mov(destination_bit, width_bit, reg, r_slash_m)
        logging.info(asm)

    return asm


def parse_1011(some_bytes):
    pass


# TODO: could DRY with `get_more_bytes_needed` / re-architect generally
def parse_next_group(some_bytes):
    first_byte = two_bytes[0]
    first_bits = bin(first_byte)[2:]

    if first_bits[0:6] == '100010':
        logging.info('this is a register-to-register or memory-to-register or register-to-memory mov')
        # TODO: don't love the naming
        return parse_100010(some_bytes)
    elif first_bits[0:4] == '1011':
        logging.info('this is an immediate-to-register mov')
        return parse_1011(some_bytes)
    else:
        raise ValueError(f'{two_bytes} not supported')

    pass


if __name__ == '__main__':
    # FILENAME = 'listing_0037_single_register_mov'
    # FILENAME = 'listing_0038_many_register_mov'
    FILENAME = sys.argv[1]
    # TODO: relative path
    with open(f'/Users/rgmbp/projects/computer_enhance/perfaware/part1/{FILENAME}', mode='r+b') as fd:
        file_contents = fd.read()

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
        # asm = parse_two_bytes(two_bytes)
        lines.append(asm)

    print(f'; {FILENAME} disassembly:')
    print('bits 16')
    for line in lines:
        print(line)
