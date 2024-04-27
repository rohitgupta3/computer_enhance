import logging

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)1.1s %(module)s:%(lineno)d - %(message)s",
)

FILENAME = 'listing_0037_single_register_mov'

def get_readable_reg(reg, width_bit):
    if reg == '000' and width_bit == '0':
        return 'AL'
    elif reg == '000' and width_bit == '1':
        return 'AX'
    elif reg == '001' and width_bit == '0':
        return 'CL'
    elif reg == '001' and width_bit == '1':
        return 'CX'
    elif reg == '010' and width_bit == '0':
        return 'DL'
    elif reg == '010' and width_bit == '1':
        return 'DX'
    elif reg == '011' and width_bit == '0':
        return 'BL'
    elif reg == '011' and width_bit == '1':
        return 'BX'
    elif reg == '100' and width_bit == '0':
        return 'AH'
    elif reg == '100' and width_bit == '1':
        return 'SP'
    elif reg == '101' and width_bit == '0':
        return 'CH'
    elif reg == '101' and width_bit == '1':
        return 'BP'
    elif reg == '110' and width_bit == '0':
        return 'DH'
    elif reg == '110' and width_bit == '1':
        return 'SI'
    elif reg == '111' and width_bit == '0':
        return 'BH'
    elif reg == '111' and width_bit == '1':
        return 'DI'



def decode_reg_to_reg_mov(destination_bit, width_bit, reg_bits_string, r_slash_m_bits_string):
    reg_decoded = get_readable_reg(reg_bits_string, width_bit)
    r_slash_m_decoded = get_readable_reg(r_slash_m_bits_string, width_bit)
    if destination_bit == '1':
        first_token = reg_decoded
        second_token = r_slash_m_decoded
    elif destination_bit == '0':
        first_token = r_slash_m_decoded
        second_token = reg_decoded
    asm_string = f'MOV {first_token}, {second_token}'
    return asm_string

# Note: check out https://edge.edx.org/c4x/BITSPilani/EEE231/asset/8086_family_Users_Manual_1_.pdf
# p160 or so of the PDF, where it says "Machine Instruction Encoding and Decoding"

# TODO: relative path
with open(f'/Users/rgmbp/projects/computer_enhance/perfaware/part1/{FILENAME}', mode='r+b') as fd:
    file_contents = fd.read()

logging.info(f'file contents: {file_contents}')

# TODO: is it pairs of bytes?
# TODO: will need to iterate thru, not just do this hardcoded bit
first_instruction = file_contents[0:2]
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
    print(f'; {FILENAME} disassembly:')
    print('bits 16')
    print(asm)
