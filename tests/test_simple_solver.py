from unittest import TestCase

from dr.model import Thesis, Relation, User, Problem
from dr.simple_solver import Solver

import logging
import sys


# uncomment the following to enable console logging
# logger = logging.getLogger()
# logger.level = logging.DEBUG
# stream_handler = logging.StreamHandler(sys.stdout)
# logger.addHandler(stream_handler)


class TestSimpleSolver (TestCase):
    def test_graph_analysis_1s0c0cy(self):
        """
        t2 -> t1
        """

        u1 = User('u1')
        u2 = User('u2')

        t1 = Thesis('t1', True)
        t2 = Thesis('t2', True)

        r = Relation(Relation.SUPPORT, t2, t1)

        p = Problem('p')

        p.add_thesis(t1)
        p.add_thesis(t2)

        p.add_relation(r)

        t1.upvote(u1)
        t2.upvote(u2)
        r.upvote(u1)

        solver = Solver(p)

        self.assertTrue(solver.problem is p)
        self.assertTrue(type(solver.error_threshold) is float)

        self.assertEqual(len(solver.users), 2)
        self.assertTrue(u1 in solver.users)
        self.assertTrue(u2 in solver.users)
        self.assertEqual(solver.all_users_strength, 2)

        self.assertEqual(len(solver.theses_data), 2)
        self.assertTrue(t1 in solver.theses_data)
        self.assertTrue(t2 in solver.theses_data)
        self.assertEqual(solver.max_theses_strength, 0)

        self.assertEqual(solver.contradictions, [])

        self.assertEqual(solver.theses_order, [
            t2,
            t1,
        ])

    def test_graph_analysis_4s0c1cy(self):
        """
              t4
               |
               v
        t2 -> t1 -> t3
         \-----<----/
        """

        t1 = Thesis('t1', True)
        t2 = Thesis('t2', True)
        t3 = Thesis('t3', True)
        t4 = Thesis('t4', True)

        r21 = Relation(Relation.SUPPORT, t2, t1)
        r13 = Relation(Relation.SUPPORT, t1, t3)
        r32 = Relation(Relation.SUPPORT, t3, t2)
        r41 = Relation(Relation.SUPPORT, t4, t1)

        p = Problem('p')

        p.add_thesis(t1)
        p.add_thesis(t2)
        p.add_thesis(t3)
        p.add_thesis(t4)

        p.add_relation(r21)
        p.add_relation(r13)
        p.add_relation(r32)
        p.add_relation(r41)

        solver = Solver(p)

        self.assertTrue(solver.problem is p)
        self.assertTrue(type(solver.error_threshold) is float)

        self.assertEqual(len(solver.users), 0)
        self.assertEqual(solver.all_users_strength, 0)

        self.assertEqual(len(solver.theses_data), 4)
        self.assertTrue(t1 in solver.theses_data)
        self.assertTrue(t2 in solver.theses_data)
        self.assertTrue(t3 in solver.theses_data)
        self.assertTrue(t4 in solver.theses_data)
        self.assertEqual(solver.max_theses_strength, 0)

        self.assertEqual(solver.contradictions, [])

        self.assertTrue(solver.theses_order.index(t1) >
                        solver.theses_order.index(t4))

    def test_graph_analysis_7s0c3cy(self):
        """
              t4
               |
               v /--->---\
        t2 -> t1 -> t3 <- t5
         \-----<---/ \->--/
        """

        t1 = Thesis('t1', True)
        t2 = Thesis('t2', True)
        t3 = Thesis('t3', True)
        t4 = Thesis('t4', True)
        t5 = Thesis('t5', True)

        r21 = Relation(Relation.SUPPORT, t2, t1)
        r13 = Relation(Relation.SUPPORT, t1, t3)
        r32 = Relation(Relation.SUPPORT, t3, t2)
        r41 = Relation(Relation.SUPPORT, t4, t1)
        r15 = Relation(Relation.SUPPORT, t1, t5)
        r53 = Relation(Relation.SUPPORT, t5, t3)
        r35 = Relation(Relation.SUPPORT, t3, t5)

        p = Problem('p')

        p.add_thesis(t1)
        p.add_thesis(t2)
        p.add_thesis(t3)
        p.add_thesis(t4)
        p.add_thesis(t5)

        p.add_relation(r21)
        p.add_relation(r13)
        p.add_relation(r32)
        p.add_relation(r41)
        p.add_relation(r15)
        p.add_relation(r53)
        p.add_relation(r35)

        solver = Solver(p)

        self.assertTrue(solver.problem is p)
        # self.assertTrue(type(solver.error_threshold) is float)

        self.assertEqual(len(solver.users), 0)
        self.assertEqual(solver.all_users_strength, 0)

        self.assertEqual(len(solver.theses_data), 5)
        self.assertTrue(t1 in solver.theses_data)
        self.assertTrue(t2 in solver.theses_data)
        self.assertTrue(t3 in solver.theses_data)
        self.assertTrue(t4 in solver.theses_data)
        self.assertTrue(t5 in solver.theses_data)
        self.assertEqual(solver.max_theses_strength, 0)

        self.assertEqual(solver.contradictions, [])

        self.assertTrue(solver.theses_order.index(t1) >
                        solver.theses_order.index(t4))

        print([str(t) for t in solver.theses_order])

    def test_iteration_1s0c0cy(self):
        """
        t2 -> t1
        """

        u1 = User('u1')
        u2 = User('u2')

        t1 = Thesis('t1', True)
        t2 = Thesis('t2', True)

        r = Relation(Relation.SUPPORT, t2, t1)

        p = Problem('p')

        p.add_thesis(t1)
        p.add_thesis(t2)

        p.add_relation(r)

        t1.upvote(u1)
        t2.upvote(u2)
        r.upvote(u1)

        solver = Solver(p)

        solution = solver.solve()

        self.assertEqual(solution, t1)

    def test_iteration_0s1c0cy(self):
        """
        t2 -x- t1
        """

        u1 = User('u1')
        u2 = User('u2')

        t1 = Thesis('t1', True)
        t2 = Thesis('t2', True)

        r = Relation(Relation.CONTRADICTION, t2, t1)

        p = Problem('p')

        p.add_thesis(t1)
        p.add_thesis(t2)

        p.add_relation(r)

        t1.upvote(u1)
        t1.upvote(u2)
        t2.upvote(u2)
        r.upvote(u1)

        solver = Solver(p)

        solution = solver.solve()

        self.assertEqual(solution, t1)
