# Note: check out https://edge.edx.org/c4x/BITSPilani/EEE231/asset/8086_family_Users_Manual_1_.pdf
# p160 or so of the PDF, where it says "Machine Instruction Encoding and Decoding"
import logging

logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)1.1s %(module)s:%(lineno)d - %(message)s",
)

import sys

# First in each group
MOV_RM_RM_OPCODE = '100010'
ADD_RM_RM_OPCODE = '000000'
SUB_RM_RM_OPCODE = '001010'
CMP_RM_R_OPCODE    = '001110'

# Conditional jump patterns
JNZ_OPCODE = '01110101'
JE_OPCODE = '01110100'
JL_OPCODE = '01111100'
JLE_OPCODE = '01111110'
JB_OPCODE = '01110010'
JBE_OPCODE = '01110110'
JP_OPCODE = '01111010'
JO_OPCODE = '01110000'
JS_OPCODE = '01111000'
JNE_OPCODE = '01110101'
JNL_OPCODE = '01111101'
JG_OPCODE = '01111111'
JNB_OPCODE = '01110011'
JA_OPCODE = '01110111'
JNP_OPCODE = '01111011'
JNO_OPCODE = '01110001'
JNS_OPCODE = '01111001'
LOOP_OPCODE = '11100010'
LOOPZ_OPCODE = '11100001'
LOOPNZ_OPCODE = '11100000'
JCXZ_OPCODE = '11100011'

COND_JUMP_OPCODES = [
    JNZ_OPCODE,
    JE_OPCODE,
    JL_OPCODE,
    JLE_OPCODE,
    JB_OPCODE,
    JBE_OPCODE,
    JP_OPCODE,
    JO_OPCODE,
    JS_OPCODE,
    JNE_OPCODE,
    JNL_OPCODE,
    JG_OPCODE,
    JNB_OPCODE,
    JA_OPCODE,
    JNP_OPCODE,
    JNO_OPCODE,
    JNS_OPCODE,
    LOOP_OPCODE,
    LOOPZ_OPCODE,
    LOOPNZ_OPCODE,
    JCXZ_OPCODE
]

# jnz test_label1
# label:
# je label
# jl label
# jle label
# jb label
# jbe label
# jp label
# jo label
# js label
# jne label
# jnl label
# jg label
# jnb label
# ja label
# jnp label
# jno label
# jns label
# loop label
# loopz label
# loopnz label
# jcxz label


###
# Utility functions / bit & byte wrangling

def bytes_repr(some_bytes):
    return " ".join([format(some_byte, '08b') for some_byte in some_bytes])

def byte_to_bitstring(some_int):
    """ e.g.
    some_int = some_bytes[0]
    eight_bits = byte_to_bitstring(some_int)
    """
    return format(some_int, '08b')

def get_int_string_from_bytes(displacement_bytes):
    int_value_i: int = int.from_bytes(displacement_bytes, byteorder='little')
    int_value_s: str = str(int_value_i)
    return int_value_s

###
# Lookups

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

    # Special case
    if mod == '00' and r_slash_m_bits_string != '110':
        return f'[{core_string}]'

    int_string_displacement = get_int_string_from_bytes(displacement_bytes)

    if r_slash_m_bits_string == '110' and mod == '00':
        return f'[{int_string_displacement}]'

    if int_string_displacement == '0':
        return f'[{core_string}]'
    else:
        return f'[{core_string} + {int_string_displacement}]'



###########
# opcode starts with 100010
###########

def get_more_bytes_needed_rmrm(two_bytes):
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


# def parse_100010(some_bytes):
#     first_byte = some_bytes[0]
#     first_bits = byte_to_bitstring(first_byte)
#     destination_bit = first_bits[6]
#     width_bit = first_bits[7]
# 
#     second_byte = some_bytes[1]
#     second_bits = byte_to_bitstring(second_byte)
#     mod = second_bits[:2]
#     reg = second_bits[2:5]
#     r_slash_m = second_bits[5:]
# 
#     if mod == '11':
#         logging.debug('this is a register-to-register mov')
#         asm = decode_reg_to_reg_mov(destination_bit, width_bit, reg, r_slash_m)
#         logging.debug(asm)
#     else:
#         logging.debug('this is memory mov')
#         asm = decode_memory_mov(destination_bit, width_bit, reg, r_slash_m, mod, some_bytes[2:])
# 
#     return asm

def get_more_bytes_needed(two_bytes):
    first_byte = two_bytes[0]
    first_bits = byte_to_bitstring(first_byte)

    # if first_bits[0:6] == '100010':
    if first_bits[:6] in [
        MOV_RM_RM_OPCODE,
        ADD_RM_RM_OPCODE,
        SUB_RM_RM_OPCODE,
        CMP_RM_R_OPCODE
    ]:
        logging.debug(f'first_bits: {first_bits}, register-to-register / memory-to-register / register-to-memory')
        return get_more_bytes_needed_rmrm(two_bytes)
    # TODO: deal with third row
    elif (first_bits[:4] == '1011' or
          first_bits[:7] == '0000010' or
          first_bits[:7] == '0010110'):
        logging.debug('this is an immediate-to-register mov')
        return get_more_bytes_row3(two_bytes)
    # TODO: handle not only 'add' immed_rm opcode
    elif first_bits[:6] == '100000':
        return get_more_bytes_immed_rm(two_bytes)
    # I think the 8086 manual has a mistake here (this is cmp immediate w/accumulator)
    # It says the data is only one byte but I think it's two if the 'w_bit' is '1'
    elif first_bits[:7] == '0011110':
        w_bit = first_bits[7]
        return 1 if w_bit == '1' else 0
    elif first_bits in COND_JUMP_OPCODES:
        return 0
    else:
        # raise NotImplementedError(f'{two_bytes} not supported. bits: {format(two_bytes[0], "08b") + format(two_bytes[1], "08b")}')
        raise NotImplementedError(f'Bytes not supported: {bytes_repr(two_bytes)}')

def get_more_bytes_immed_rm(two_bytes):
    first_byte = two_bytes[0]
    first_bits = byte_to_bitstring(first_byte)
    logging.debug(f'first_bits: {first_bits}')

    s_bit = first_bits[6]
    w_bit = first_bits[7]

    second_byte = two_bytes[1]
    second_bits = byte_to_bitstring(second_byte)
    logging.debug(f'second_bits: {second_bits}')

    mod = second_bits[:2]
    r_slash_m = second_bits[5:]

    displacement_bytes = 0
    if mod == '11':
        pass # no-op
    elif mod == '10':
        displacement_bytes = 2
    elif mod == '01':
        displacement_bytes = 1
    elif mod == '00' and r_slash_m == '110':
        displacement_bytes = 2
    elif mod == '00' and r_slash_m != '110':
        displacement_bytes = 0
    else:
        raise ValueError('not sure')

    # TODO: don't understand sign / word bytes etc
    data_bytes = 1
    # I think the way this works is if `w_bit` is 1 i.e. you have to put the
    # immediate into 16 bits, then if `s_bit` is 1 that means you get the 16 
    # bits by getting 8 bits of data and sign extending it; otherwise get
    # the full 16 bits from the instruction
    if w_bit == '1' and s_bit == '0':
        data_bytes = 2

    return displacement_bytes + data_bytes

def get_more_bytes_row3(two_bytes):
    first_byte = two_bytes[0]
    first_bits = byte_to_bitstring(first_byte)
    logging.debug(f'first_bits: {first_bits}')
    # mov row 3
    if first_bits[:4] == '1011':
        width_bit = first_bits[4]
    # add row 3, sub row 3
    elif first_bits[:7] == '0000010' or first_bits[:7] == '0010110':
        width_bit = first_bits[7]
    else:
        raise ValueError(f'in `get_more_bytes_row3 with first_bits: {first_bits}')
    return 1 if width_bit == '1' else 0


# def decode_memory_mov(
#     destination_bit,
#     width_bit,
#     reg_bits_string,
#     r_slash_m_bits_string,
#     mod,
#     displacement_bytes
# ):
#     reg_decoded = get_readable_reg(reg_bits_string, width_bit)
#     r_slash_m_decoded = get_readable_eff_add(
#             r_slash_m_bits_string,
#             mod,
#             displacement_bytes
#     )
#     # TODO: DRY with `decode_reg_to_reg_mov`?
#     if destination_bit == '1':
#         first_token = reg_decoded
#         second_token = r_slash_m_decoded
#     elif destination_bit == '0':
#         first_token = r_slash_m_decoded
#         second_token = reg_decoded
#     asm_string = f'mov {first_token}, {second_token}'
#     return asm_string


# def decode_reg_to_reg_mov(destination_bit, width_bit, reg_bits_string, r_slash_m_bits_string):
#     reg_decoded = get_readable_reg(reg_bits_string, width_bit)
#     r_slash_m_decoded = get_readable_reg(r_slash_m_bits_string, width_bit)
#     if destination_bit == '1':
#         first_token = reg_decoded
#         second_token = r_slash_m_decoded
#     elif destination_bit == '0':
#         first_token = r_slash_m_decoded
#         second_token = reg_decoded
#     asm_string = f'mov {first_token}, {second_token}'
#     return asm_string


# TODO: could DRY with `get_more_bytes_needed_row3`
def parse_1011(some_bytes):
    first_byte = some_bytes[0]
    first_bits = byte_to_bitstring(first_byte)
    logging.debug(f'first_bits: {first_bits}')
    width_bit = first_bits[4]
    reg = first_bits[5:]
    reg_decoded = get_readable_reg(reg, width_bit)
    immediate_s = get_int_string_from_bytes(some_bytes[1:])
    return f'mov {reg_decoded}, {immediate_s}'

def parse_rmrm_operands(some_bytes):
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
        logging.debug('this is a register-to-register operation')
        asm = decode_reg_to_reg_operands(destination_bit, width_bit, reg, r_slash_m)
        logging.debug(asm)
    else:
        logging.debug('this is memory operation')
        asm = decode_memory_operands(destination_bit, width_bit, reg, r_slash_m, mod, some_bytes[2:])

    return asm

def decode_reg_to_reg_operands(destination_bit, width_bit, reg_bits_string, r_slash_m_bits_string):
    reg_decoded = get_readable_reg(reg_bits_string, width_bit)
    r_slash_m_decoded = get_readable_reg(r_slash_m_bits_string, width_bit)
    if destination_bit == '1':
        first_token = reg_decoded
        second_token = r_slash_m_decoded
    elif destination_bit == '0':
        first_token = r_slash_m_decoded
        second_token = reg_decoded
    asm_string = f'{first_token}, {second_token}'
    return asm_string

def decode_memory_operands(
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
    # TODO: DRY with `decode_reg_to_reg_operands`?
    if destination_bit == '1':
        first_token = reg_decoded
        second_token = r_slash_m_decoded
    elif destination_bit == '0':
        first_token = r_slash_m_decoded
        second_token = reg_decoded
    asm_string = f'{first_token}, {second_token}'
    return asm_string



# TODO: could DRY with `get_more_bytes_needed` / re-architect generally
def parse_next_group(some_bytes):
    first_byte = some_bytes[0]
    first_bits = byte_to_bitstring(first_byte)

    if first_bits[0:6] == MOV_RM_RM_OPCODE:
        logging.debug('this is a register-to-register or memory-to-register or register-to-memory mov')
        # TODO: don't love the naming
        # return parse_100010(some_bytes)
        return 'mov ' + parse_rmrm_operands(some_bytes)
    elif first_bits[0:6] == ADD_RM_RM_OPCODE:
        logging.debug('this is a reg/memory with register to either add')
        return 'add ' + parse_rmrm_operands(some_bytes)
    elif first_bits[0:6] == SUB_RM_RM_OPCODE:
        logging.debug('this is a reg/memory and register to either sub')
        return 'sub ' + parse_rmrm_operands(some_bytes)
    elif first_bits[0:6] == CMP_RM_R_OPCODE:
        logging.debug('this is a reg/memory and register to either cmp')
        return 'cmp ' + parse_rmrm_operands(some_bytes)
    elif first_bits[0:4] == '1011':
        logging.debug('this is an immediate-to-register mov')
        return parse_1011(some_bytes)
    # TODO: handle not only add immed_rm opcode
    elif first_bits[:6] == '100000':
        second_byte = some_bytes[1]
        second_bits = byte_to_bitstring(second_byte)
        pseudo_reg = second_bits[2:5]
        operand = None
        if pseudo_reg == '000':
            operand = 'add'
        elif pseudo_reg == '101':
            operand = 'sub'
        elif pseudo_reg == '111':
            operand = 'cmp'
        else:
            raise NotImplementedError(f'Bytes not supported: {bytes_repr(some_bytes)}')
        return f'{operand} {parse_immed_rm_operands(some_bytes)}'
    # immediate to accumulator 'add'
    elif first_bits[:7] == '0000010':
        return 'add ' + parse_immed_acc_operands(some_bytes)
    elif first_bits[:7] == '0010110':
        return 'sub ' + parse_immed_acc_operands(some_bytes)
    # Messy, not operating at one level of abstraction here
    # cmp immediate with accumulator
    elif first_bits[:7] == '0011110':
        data_byte = some_bytes[1:]
        immediate_s = get_int_string_from_bytes(data_byte)
        w_bit = first_bits[7]
        accum_reg = 'ax' if w_bit == '1' else 'al'
        return f'cmp {accum_reg}, {immediate_s}'
    elif first_bits in COND_JUMP_OPCODES:
        return parse_conditional_jump(some_bytes)
    else:
        raise NotImplementedError(f'Bytes not supported: {bytes_repr(some_bytes)}')
        # raise NotImplementedError(f'{two_bytes} not supported. bits: {format(two_bytes[0], "08b") + format(two_bytes[1], "08b")}')


def parse_conditional_jump(some_bytes):
    first_byte = some_bytes[0]
    first_bits = byte_to_bitstring(first_byte)

    address = get_int_string_from_bytes(some_bytes[1:])

    jmp_instruction = None
    if first_bits == JNZ_OPCODE:
        jmp_instruction = 'jnz'
    elif first_bits == JE_OPCODE:
        jmp_instruction = 'je'
    elif first_bits == JL_OPCODE:
        jmp_instruction = 'jl'
    elif first_bits == JLE_OPCODE:
        jmp_instruction = 'jle'
    elif first_bits == JB_OPCODE:
        jmp_instruction = 'jb'
    elif first_bits == JBE_OPCODE:
        jmp_instruction = 'jbe'
    elif first_bits == JP_OPCODE:
        jmp_instruction = 'jp'
    elif first_bits == JO_OPCODE:
        jmp_instruction = 'jo'
    elif first_bits == JS_OPCODE:
        jmp_instruction = 'js'
    elif first_bits == JNE_OPCODE:
        jmp_instruction = 'jne'
    elif first_bits == JNL_OPCODE:
        jmp_instruction = 'jnl'
    elif first_bits == JG_OPCODE:
        jmp_instruction = 'jg'
    elif first_bits == JNB_OPCODE:
        jmp_instruction = 'jnb'
    elif first_bits == JA_OPCODE:
        jmp_instruction = 'ja'
    elif first_bits == JNP_OPCODE:
        jmp_instruction = 'jnp'
    elif first_bits == JNO_OPCODE:
        jmp_instruction = 'jno'
    elif first_bits == JNS_OPCODE:
        jmp_instruction = 'jns'
    elif first_bits == LOOP_OPCODE:
        jmp_instruction = 'loop'
    elif first_bits == LOOPZ_OPCODE:
        jmp_instruction = 'loopz'
    elif first_bits == LOOPNZ_OPCODE:
        jmp_instruction = 'loopnz'
    elif first_bits == JCXZ_OPCODE:
        jmp_instruction = 'jcxz'
    else:
        raise ValueError(f'Shouldn\'t be in jmp function, some_bytes: {bytes_repr(some_bytes)}')
    
    return f'{jmp_instruction} {address}'

# TODO: a little confused about accumulator. Thought it's always
# ax, but think if we're moving 8 bits then it's al
def parse_immed_acc_operands(some_bytes):
    first_byte = some_bytes[0]
    first_bits = byte_to_bitstring(first_byte)
    w_bit = first_bits[7]
    accumulator_register = 'ax' if w_bit == '1' else 'al'

    immediate_s = get_int_string_from_bytes(some_bytes[1:])
    return f'{accumulator_register}, {immediate_s}'


def parse_immed_rm_operands(some_bytes):
    first_byte = some_bytes[0]
    first_bits = byte_to_bitstring(first_byte)
    logging.debug(f'first_bits: {first_bits}')

    s_bit = first_bits[6]
    w_bit = first_bits[7]

    second_byte = some_bytes[1]
    second_bits = byte_to_bitstring(second_byte)
    logging.debug(f'second_bits: {second_bits}')

    mod = second_bits[:2]
    # middle_bits = second_bits[2:5] # '000' for add, '101' for sub, '111' for cmp
    r_slash_m = second_bits[5:]

    # Register mode, no displacement
    if mod == '11':
        logging.debug('this is a register operation')
        # data_byte_count = 2 if w_bit == '1' else 1
        # data_bytes = some_bytes[2:]
        register_name = get_readable_reg(r_slash_m, w_bit)
        immediate_s = get_int_string_from_bytes(some_bytes[2:])
        asm = f'{register_name}, {immediate_s}'
        logging.debug(asm)
        return asm
    # Memory mode, no displacement
    elif mod == '00' and r_slash_m != '110':
        # TODO: get destination (memory address)
        data_bytes = some_bytes[2:]
        effective_address = get_readable_eff_add(
            r_slash_m_bits_string=r_slash_m,
            mod=mod,
            displacement_bytes=None
        )
        immediate_s = get_int_string_from_bytes(data_bytes)
        immediate_size = 'word' if w_bit == '1' else 'byte'
        asm = f'{immediate_size} {effective_address}, {immediate_s}'
    # Memory mode, 16-bit displacement
    elif mod == '10':
        displacement_bytes = some_bytes[2:4]
        data_bytes = some_bytes[4:]
        effective_address = get_readable_eff_add(
            r_slash_m_bits_string=r_slash_m,
            mod=mod,
            displacement_bytes=displacement_bytes
        )
        immediate_s = get_int_string_from_bytes(data_bytes)
        immediate_size = 'word' if w_bit == '1' else 'byte'
        asm = f'{immediate_size} {effective_address}, {immediate_s}'
    # Memory mode, 16-bit displacement (special case of mod '00')
    elif mod == '00' and r_slash_m == '110':
        displacement_bytes = some_bytes[2:4]
        data_bytes = some_bytes[4:]
        effective_address = get_readable_eff_add(
            r_slash_m_bits_string=r_slash_m,
            mod=mod,
            displacement_bytes=displacement_bytes
        )
        immediate_s = get_int_string_from_bytes(data_bytes)
        immediate_size = 'word' if w_bit == '1' else 'byte'
        asm = f'{immediate_size} {effective_address}, {immediate_s}'

    # TODO: do others
    else:
        raise NotImplementedError(f'Haven\'t dealt with {bytes_repr(some_bytes)}')
        # asm = decode_memory_operands(destination_bit, width_bit, reg, r_slash_m, mod, some_bytes[2:])

    return asm



def decode_machine_code(file_contents, num_lines=None):
    lines = []
    line_no = 0
    while True:
        logging.info("New line")
        if len(file_contents) == 0:
            break
        if num_lines and len(lines) == num_lines:
            break
        if line_no == 69:
            # breakpoint()
            pass
        two_bytes = file_contents[:2]
        file_contents = file_contents[2:]
        more_bytes_needed = get_more_bytes_needed(two_bytes)
        remaining_bytes = file_contents[:more_bytes_needed]
        file_contents = file_contents[more_bytes_needed:]
        asm = parse_next_group(two_bytes + remaining_bytes)
        print(f'asm, line {line_no}: {asm}')
        lines.append(asm)
        line_no += 1

    return lines

def decode_executable(filename, num_lines=None):
    # TODO: relative path
    with open(f'/Users/rgmbp/projects/computer_enhance/perfaware/part1/{filename}', mode='r+b') as fd:
        file_contents = fd.read()

    lines = decode_machine_code(file_contents, num_lines)
    return lines

def decode_executable_polished(filename, num_lines=None):
    lines = decode_executable(filename, num_lines)
    lines_with_polish = [
        f'; {filename} disassembly:',
        'bits 16',
        *lines
    ]
    return lines_with_polish

