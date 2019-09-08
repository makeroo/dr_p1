from unittest import TestCase

from dr.model import Thesis, Relation, User, Problem


class TestModel (TestCase):
    def test_thesis(self):
        t = Thesis('t', True)

        self.assertEqual(t.content, 't')
        self.assertTrue(t.is_solution)

        self.assertEqual(t, Thesis('t', False))
        self.assertNotEqual(t, Thesis('u', True))

    def test_relation(self):
        t1 = Thesis('t1', False)
        t2 = Thesis('t2', False)

        r = Relation(Relation.SUPPORT, t1, t2)

        self.assertTrue(r.type is Relation.SUPPORT)
        self.assertTrue(r.thesis1 is t1)
        self.assertTrue(r.thesis2 is t2)
        self.assertTrue(type(r.votes) is dict)

    def test_user(self):
        u = User('x')

        self.assertEqual(u.name, 'x')

        self.assertEqual(u, User('x'))
        self.assertNotEqual(u, User('y'))

        hash_test = {}
        hash_test[User('x')] = 2

        self.assertEqual(hash_test[User('x')], 2)

        try:
            hash_test[User('y')]
            self.fail('Should raise KeyError')
        except KeyError:
            pass

    def test_problem(self):
        p = Problem('q')

        self.assertEqual(p.question, 'q')
        self.assertTrue(hasattr(p, 'theses') and type(p.theses) is set)
        self.assertTrue(hasattr(p, 'relations') and type(p.relations) is set)

        self.assertTrue(len(p.theses) == 0)
        self.assertTrue(len(p.relations) == 0)

        t1 = Thesis('t1', False)
        t2 = Thesis('t2', False)

        p.add_thesis(t1)

        self.assertEqual(p.theses, {t1})

        r = Relation(Relation.SUPPORT, t1, t2)

        try:
            p.add_relation(r)
            self.fail('Should raise AssertionError')
        except AssertionError:
            pass
