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
import unittest

TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_artifacts')


# Do we feel good about not testing this test code?
def bits_to_bytes(bits: str):
    byte_values  = [
        int(bits[i:i+8], 2)
        for i in range(0, len(bits), 8)
    ]
    return bytes(byte_values)

class Listing0040DecodeTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        dest = '0'
        width = '0'
        mod = '00'
        reg = '000'
        r_slash_m = '000'
        # TODO: below not necessarily legal e.g. maybe this should have displacement
        mov_regmem_regmem_bits = (
            f'100010{dest}{width}'
            f'{mod}{reg}{r_slash_m}'
        )
        mov_regmem_regmem_byte_vals = [
            int(mov_regmem_regmem_bits[i:i+8], 2)
            for i in range(0, len(mov_regmem_regmem_bits), 8)
        ]
        self.mov_regmem_regmem_machine_code = bytes(mov_regmem_regmem_byte_vals)

    def test_more_bytes_needed_for_regmem_regmem_mod_01(self):
        """
        mod = '01' => 8-bit disp
        mod = '10' => 16-bit disp
        mod = '11' => no displacement
        """
        dest_bit = '0'
        width_bit = '0'
        reg = '000'
        r_slash_m = '000'

        mov_prefix = '100010'
        make_bytes = lambda prefix, mod: bits_to_bytes(
            f'{prefix}{dest_bit}{width_bit}'
            f'{mod}{reg}{r_slash_m}'
        )
        # mod = '01'
        mov_bytes = make_bytes('100010', '01')
        add_bytes = make_bytes('000000', '01')
        sub_bytes = make_bytes('001010', '01')
        cmp_bytes = make_bytes('001110', '01')
        self.assertEqual(parser.get_more_bytes_needed(mov_bytes), 1)
        self.assertEqual(parser.get_more_bytes_needed(add_bytes), 1)
        self.assertEqual(parser.get_more_bytes_needed(sub_bytes), 1)
        self.assertEqual(parser.get_more_bytes_needed(cmp_bytes), 1)

        # mod = '10'
        mov_bytes = make_bytes('100010', '10')
        add_bytes = make_bytes('000000', '10')
        sub_bytes = make_bytes('001010', '10')
        cmp_bytes = make_bytes('001110', '10')
        self.assertEqual(parser.get_more_bytes_needed(mov_bytes), 2)
        self.assertEqual(parser.get_more_bytes_needed(add_bytes), 2)
        self.assertEqual(parser.get_more_bytes_needed(sub_bytes), 2)
        self.assertEqual(parser.get_more_bytes_needed(cmp_bytes), 2)

        # mod = '11'
        mov_bytes = make_bytes('100010', '11')
        add_bytes = make_bytes('000000', '11')
        sub_bytes = make_bytes('001010', '11')
        cmp_bytes = make_bytes('001110', '11')
        self.assertEqual(parser.get_more_bytes_needed(mov_bytes), 0)
        self.assertEqual(parser.get_more_bytes_needed(add_bytes), 0)
        self.assertEqual(parser.get_more_bytes_needed(sub_bytes), 0)
        self.assertEqual(parser.get_more_bytes_needed(cmp_bytes), 0)

    def test_more_bytes_needed_for_row3(self):
        """
        w = '0' => 8-bit data
        w = '1' => 16-bit data
        """
        data_8bits = '00000000'
        data_16bits = '0000000011111111'
        w0 = '0'
        w1 = '1'

        # w = '0'
        reg = '000'
        mov_bits = f'1011{w0}{reg}{data_8bits}'
        mov_first_two_bytes = bits_to_bytes(mov_bits)
        self.assertEqual(parser.get_more_bytes_needed(mov_first_two_bytes), 0)

        add_bits = f'0000010{w0}{data_8bits}'
        add_first_two_bytes = bits_to_bytes(add_bits)
        self.assertEqual(parser.get_more_bytes_needed(add_first_two_bytes), 0)

        sub_bits = f'0010110{w0}{data_8bits}'
        sub_first_two_bytes = bits_to_bytes(sub_bits)
        self.assertEqual(parser.get_more_bytes_needed(sub_first_two_bytes), 0)

        # w = '1'
        reg = '000'
        mov_bits = f'1011{w1}{reg}{data_16bits}'
        mov_first_two_bytes = bits_to_bytes(mov_bits)
        self.assertEqual(parser.get_more_bytes_needed(mov_first_two_bytes), 1)

        add_bits = f'0000010{w1}{data_16bits}'
        add_first_two_bytes = bits_to_bytes(add_bits)
        self.assertEqual(parser.get_more_bytes_needed(add_first_two_bytes), 1)

        sub_bits = f'0010110{w1}{data_16bits}'
        sub_first_two_bytes = bits_to_bytes(sub_bits)
        self.assertEqual(parser.get_more_bytes_needed(sub_first_two_bytes), 1)

    def test_add_immediate_to_regmem(self):
        """
        Starts with 100000, second byte has '000' in it
        Modeled after the first new instruction pattern in listing 41
        """
        opcode = '100000'
        s_bit = '1'
        w_bit = '1'
        mod = '11' # no displacement
        reg_slash_m = '110' # not the point

        instruction_bits = f'{opcode}{s_bit}{w_bit}{mod}000{reg_slash_m}'
        instruction_bytes = bits_to_bytes(instruction_bits)
        self.assertEqual(parser.get_more_bytes_needed(instruction_bytes), 2)

