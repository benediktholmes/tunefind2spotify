from copy import deepcopy

from tunefind2spotify.utils import singleton, MediaType, dict_keep


class TestSingleton:

    def test_singleton(self):
        @singleton
        class Dummy:
            def __init__(self, a: int):
                self.a = a

        obj_1 = Dummy(5)
        assert obj_1.a == 5
        obj_2 = Dummy(10)
        assert obj_2.a == 10
        assert obj_2.a == obj_1.a
        assert obj_1 == obj_2, 'Objects created from a singleton class should be equal. ' \
                               f'Instead got: {obj_1} and {obj_2} .'


class TestMediaType:

    MAP = {
        'show': MediaType.SHOW,
        'SHOW': MediaType.SHOW,
        'shOw': MediaType.SHOW,
        'movie': MediaType.MOVIE,
        'MOVIE': MediaType.MOVIE,
        'mOViE': MediaType.MOVIE,
        'game': MediaType.GAME,
        'GAME': MediaType.GAME,
        'gAmE': MediaType.GAME,
    }

    def test_read_in(self):
        for name, mt in self.MAP.items():
            assert MediaType.read_in(name) is mt, f'Input name \'{name}\' should return {mt} .'

    def test_read_in_random(self):
        r_name = '089wv87wcmxzt4x'
        assert MediaType.read_in(r_name) is None, f'Input name \'{r_name}\' should return None.'

    def test_read_in_not_str(self):
        not_str = 1234
        assert MediaType.read_in(not_str) is None, f'Input \'{not_str}\' should return None.'

    def test_translate(self):
        for name, mt in self.MAP.items():
            assert MediaType.translate(mt) == name.lower()


class TestDictKeep:
    d = {'a': 1, 'b': 2, 'c': 3, 'd': 4}

    def test_no_overlap(self):
        _copy = deepcopy(self.d)
        res = dict_keep(self.d, ['e', 'f', 'g'])
        assert self.d == _copy, 'Original dict must remain unaffected.'
        assert len(res.items()) == 0, f'Dictionary should be empty as all keys were deleted. Instead got: {res}'

    def test_subset(self):
        _copy = deepcopy(self.d)
        res = dict_keep(self.d, ['b', 'd'])
        assert self.d == _copy, 'Original dict must remain unaffected.'
        assert len(res.items()) == 2, 'Only two items should remain in dictionary.'
        assert 'b' in res.keys() and 'd' in res.keys(),\
            f'Keys \'b\' and \'d\' should remain in dictionary. Instead got: {res.keys()} .'
        assert res['b'] == self.d['b'] and res['d'] == self.d['d'],\
            f'Values for remaining keys \'b\' and \'d\' should be unchanged. Instead got: {self.d} vs {res} .'

    def test_half_overlap(self):
        _copy = deepcopy(self.d)
        res = dict_keep(self.d, ['c', 'd', 'e', 'f'])
        assert self.d == _copy, 'Original dict must remain unaffected.'
        assert len(res.items()) == 2, 'Only two items should remain in dictionary.'
        assert 'c' in res.keys() and 'd' in res.keys(), \
            f'Keys \'c\' and \'d\' should remain in dictionary. Instead got: {res.keys()} .'
        assert res['c'] == self.d['c'] and res['d'] == self.d['d'], \
            f'Values for remaining keys \'c\' and \'d\' should be unchanged. Instead got: {self.d} vs {res} .'

    def test_total_overlap(self):
        _copy = deepcopy(self.d)
        res = dict_keep(self.d, ['a', 'b', 'c', 'd', 'e'])
        assert self.d == _copy, 'Original dict must remain unaffected.'
        assert res == self.d, 'Dict content should not have changed.'
