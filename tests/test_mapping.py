from pyverpisor import mapping


def test_mapped_page_is_writable_and_readable():
    page, _ = mapping.map_executable_page(100)

    page[0:5] = b"hello"
    page[5:11] = b" world"

    assert bytes(page[0:11]) == b"hello world"
