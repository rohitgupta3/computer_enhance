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

# Note: check out https://edge.edx.org/c4x/BITSPilani/EEE231/asset/8086_family_Users_Manual_1_.pdf
# p160 or so of the PDF, where it says "Machine Instruction Encoding and Decoding"


def parse_two_bytes(two_bytes):
    # TODO: is it pairs of bytes?
    # TODO: will need to iterate thru, not just do this hardcoded bit
    first_instruction = two_bytes[0:2]
    first_byte = first_instruction[0]
    first_bits = bin(first_byte)[2:]

    opcode = first_bits[0:6]
    # TODO: check this
    if opcode == '100010':
        logging.info('this is a MOV')
    destination_bit = first_bits[6]
    logging.info(f'destination_bit: {destination_bit}')
    width_bit = first_bits[7]
    logging.info(f'width_bit: {width_bit}')

    second_byte = first_instruction[1]
    second_bits = bin(second_byte)[2:]
    logging.info(f'second_bits: {second_bits}')
    mod = second_bits[:2]
    reg = second_bits[2:5]
    r_slash_m = second_bits[5:]
    logging.info(f'mod: {mod}')
    logging.info(f'reg: {reg}')
    logging.info(f'r_slash_m: {r_slash_m}')

    if opcode == '100010' and mod == '11':
        logging.info('this is a register-to-register MOV')
        asm = decode_reg_to_reg_mov(destination_bit, width_bit, reg, r_slash_m)
        logging.info(asm)

    return asm

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
        asm = parse_two_bytes(two_bytes)
        lines.append(asm)

    print(f'; {FILENAME} disassembly:')
    print('bits 16')
    for line in lines:
        print(line)
