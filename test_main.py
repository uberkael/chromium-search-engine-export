import utils
import locations


def test_browser_names():
    browsers = ["chrome", "chromium", "brave", "edge", "vivaldi", "opera", "helium"]

    for k in locations.LOCATIONS.keys():
        assert k in browsers


def test_padding():
    lista = ['a', 'b', 'c']
    assert utils.add_spaces(lista) == ['a     ', 'b     ', 'c     ']
