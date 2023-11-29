from pyverpisor import mapping
import ctypes
from iced_x86 import *


def test_mapped_page_is_writable_and_readable():
    page, _ = mapping.map_executable_page(100)

    page[0:5] = b"hello"
    page[5:11] = b" world"

    assert bytes(page[0:11]) == b"hello world"


def test_mapped_page_is_executable():
    # Now let's treat the mapped page as a c function returning an int and see
    # if it executes.
    page, ptr = mapping.map_executable_page(100)
    instructions = [
        Instruction.create_reg_i64(Code.MOV_R64_IMM64, Register.RAX, 41),
        Instruction.create_reg_i32(Code.ADD_RM64_IMM8, Register.RAX, 0x1),
        Instruction.create(Code.RETNW)
    ]

    # Assemble and write instructions to page
    encoder = BlockEncoder(bitness=64)
    encoder.add_many(instructions)
    encoded_bytes = encoder.encode(rip=ptr)
    page[0:len(encoded_bytes)] = encoded_bytes

    # Returns int64_t and takes nothing.
    functype = ctypes.CFUNCTYPE(ctypes.c_int64)
    function = functype(ptr)

    result = function()
    assert result == 42
