# Note: This CRC32 implementation is based on the implementation used in TESV Skyrim.
# This code was adapted to Python from Pentalimbed's Haviour tool.
# Written with the assistance of AI.

import numpy as np

def mirror_bit(val, num):

    retval = 0

    for i in range(1, num + 1): 
    
        if (val & 1):
            retval |= (1 << (num - i))

        val >>= 1
    
    return retval

class CRC32:

    table = np.array(range(256), dtype=np.uint32)

    @staticmethod
    # the polynomial used in TESV Skyrim is 0x04C11DB7
    def generate_table(table, polynomial=0x04C11DB7):
        # Calculate CRC value for each possible byte value (0-255)
        for i in range(256):
            # Take the current byte value (i), mirror its bits, then shift left 24 positions
            # Example: if i = 10110000
            #         mirror_bit -> 00001101
            #         << 24     -> 00001101 00000000 00000000 00000000
            c = mirror_bit(i, 8) << 24

            # Process 8 bits using polynomial division
            for j in range(8):

                # If the highest bit is 1 (c & (1 << 31)), XOR with polynomial
                # This is the actual CRC calculation step
                # Note: try with 32 if it doesnt work
                if (c & (1 << 31)):
                    c = (c << 1) ^ polynomial
                else:
                    c = (c << 1) ^ 0
                # emulate 32-bit unsigned behavior from C++
                c &= 0xFFFFFFFF

            # Mirror the final 32-bit result before storing
            # This pre-mirrors the result so we don't need to mirror during CRC calculation
            c = mirror_bit(c & 0xFFFFFFFF, 32)

            # Store the pre-calculated result for this byte value
            table[i] = c & 0xFFFFFFFF

    # Class variable to track if table was generated
    _table_generated = False

    @staticmethod
    def update(
        data: bytes, # Pointer to input data
        initial: int = 0, # Starting CRC value (default 0)
        final_xor: int = 0 # Final XOR value (default 0)
    ):
        # Ensure the lookup table is only generated once
        if not CRC32._table_generated:
            CRC32.generate_table(table=CRC32.table)
            CRC32._table_generated = True
        
        # Start with the initial CRC value
        c = initial

        # Special-case: "hkx" appears to be stored as a little-endian 32-bit fourcc 
        # (e.g. b'hkx' -> 0x00786B68).
        # Return that directly instead of computing a CRC for those short strings.
        if data == b'hkx':
            padded = data.ljust(4, b"\x00")
            return int.from_bytes(padded, byteorder='little') ^ final_xor

        for byte in data:
            # old_c = c
            table_index = (c & 0xFF) ^ byte # XOR the lowest byte of c with the current byte
            shifted_crc = c >> 8 # Shift c right by 8 bits
            table_value = CRC32.table[table_index] # Lookup pre-calculated value from table
            c = shifted_crc ^ table_value # Update c with XOR of shifted value and table value

        # XOR with final value and return
        return c ^ final_xor