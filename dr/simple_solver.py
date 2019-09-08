import logging

from .model import Relation


logger = logging.getLogger(__name__)


class UserData:
    def __init__(self):
        self.strength = 0
        self.contradictions = {}
        self.next_strength = 1


class ThesisData:
    def __init__(self):
        self.strength = 0
        self.supporting_relations = []
        self.taken = False


class RelationData:
    def __init__(self):
        self.strength = 0


class Contradiction:
    def __init__(self, contradiction_relation, path1=None, path2=None):
        self.contradiction_relation = contradiction_relation
        self.path1 = path1
        self.path2 = path2


class Path:
    def __init__(self, *support_relations):
        self.path = support_relations

    @property
    def first_thesis(self):
        self.path[0].thesis1

    @property
    def last_thesis(self):
        self.path[-1].thesis1

    def __contains__(self, thesis):
        for rel in self.path:
            if rel.thesis1 == thesis:
                return True

        return rel.thesis2 == thesis

    def grow(self, relation):
        return Path(*self.path, relation)


class Solver:
    def __init__(self, problem, error_threshold=.1):
        self.problem = problem
        self.error_threshold = error_threshold

        # collect all users and set their strength to default 1

        self.users = {u: UserData()
            for u in [
                u
                for thesis in problem.theses
                for u in thesis.votes
            ] + [
                u
                for relation in problem.relations
                for u in relation.votes
            ]
        }

        self.all_users_strength = len(self.users)

        # for each thesis we need a bunch of data

        self.theses_data = {
            thesis: ThesisData()
            for thesis in problem.theses
        }

        self.inverse_theses_order = None
        self.max_theses_strength = 0

        self.relations = {
            relation: RelationData()
            for relation in problem.relations
        }

        self.contradictions = []

        self._analyze_theses_graph()

        self._find_users_contradictions()

        # stats

        self.iteration = 0

    def solve(self):
        """
        Calculate theses strengths and return the one with greater strength that is also a solution.
        """

        while True:
            self._iterate()

            if self._converged():
                break

            self.iteration += 1

        return self._find_stronger_solution()

    def _analyze_theses_graph(self):
        # collect all supporting theses

        paths = []

        for relation in self.relations:
            if relation.type is Relation.SUPPORT:
                self.theses_data[relation.thesis2].supporting_relations.add(relation)

                paths.add([relation.thesis2, relation.thesis1])

        # find cycles

        cycles = []

        while paths:
            new_paths = []

            for path in paths:
                thesis = path[-1]
                thesis_data = self.theses_data[thesis]

                for relation in thesis_data.supporting_relations:
                    new_path = path + [relation.thesis1]

                    if thesis in path:
                        cycles.append(new_path)
                    else:
                        new_paths.append(new_path)

            paths = new_paths

        # remove supporting_relations that form cycles

        for cycle in cycles:
            for relation in cycle:
                thesis = relation.thesis2
                thesis_data = self.thesis_data[thesis]

                thesis_data.supporting_relations.remove(relation)

        # calc theses order

        self.inverse_theses_order = []

        theses_count = len(self.theses_data)

        while theses_count > len(self.inverse_theses_order):
            for thesis, thesis_data in self.theses_data.items():
                if thesis_data.taken:
                    continue

                if not thesis_data.supporting_relations:
                    thesis_data.taken = True
                    self.inverse_theses_order.append(thesis)
                    continue

                collectable = True

                for relation in thesis_data.supporting_relations:
                    supporting_thesis_data = self.theses_data[relation.thesis1]

                    if not supporting_thesis_data.taken:
                        collectable = False
                        break

                if collectable:
                    thesis_data.taken = True
                    self.inverse_theses_order.append(thesis)

    def _iterate(self):
        self._calc_all_users_strength();
        self._calc_relations_strength()
        self._calc_theses_strength()
        self._calc_contradictions_strength()
        self._calc_users_strength()

    def _calc_all_users_strength(self):
        self.all_users_strength = 0

        for user_data in self.users.values():
            user_data.strength = user_data.next_strength

            self.all_users_strength += user_data.strength

    def _calc_relations_strength(self):
        for relation, relation_data in self.relations.items():
            relation_data.strength = self._direct_votes_strength(relation)

    def _direct_votes_strength(self, voted_object):
        upvotes = 0
        downvotes = 0

        for user, vote in voted_object.votes.items():
            if vote == -1:
                downvotes += user.strength
            else:
                upvotes += user.strength

        if upvotes > downvotes:
            return upvotes / self.all_users_strength
        else:
            return 0

    def _calc_theses_strength(self):
        for thesis in reversed(self.inverse_theses_order):
            thesis_data = self.theses_data[thesis]

            thesis_data.strength = self._direct_votes_strength(thesis)

            if thesis_data.strength > 0:
                for relation in thesis_data.supporting_relations:
                    relation_data = self.relations[relation]
                    supporting_thesis_data = self.theses_data[relation.thesis1]

                    thesis_data.strength += relation_data.strength * supporting_thesis_data.strength

        self.max_theses_strength = max([thesis.strength for thesis in self.theses])

    def _new_contradiction(self, contradiction_relation, path1, path2):
        r = Contradiction(contradiction_relation, path1, path2)

        self.contradictions.append(r)

        return r

    def _build_and_assign_contradiction(self, users, relation, path1=None, path2=None):
        if not users:
            return

        contradiction = self._new_contradiction(relation, path1, path2)

        for user in users:
            user_data = self.users[user]

            user_data.contradictions.setdefault(relation, []).append(contradiction)

    def _find_users_contradictions(self):
        # method 3: collect all inconsistencies, starting from contradiciton relation
        # and following support path, then assign them to voting users
        self.contradictions = []

        for user_data in self.users.values():
            user_data.contradictions = {}

        for relation in filter(lambda r: r.type is self.CONTRADICTION, self.relations):
            self._build_and_assign_contradiction(
                relation.thesis1.votes.keys() & relation.thesis2.votes.keys(),
                relation
            )

            # consider every non repeating path consisting of support relation
            # ending either in relation.thesis1 or relation.thesis2
            # such paths are contradictions
            # i have to take, for each user, just one contradiction for each
            # relation, the one with max strength

            all_paths = {}

            for ending_point in [relation.thesis1, relation.thesis2]:
                paths_to_examine = [
                        Path(supp_rel)
                        for supp_rel in filter(
                            lambda r: r.type is Relation.SUPPORT and r.thesis2 is ending_point,
                            ending_point.relations
                        )
                    ]

                while paths_to_examine:
                    path = paths_to_examine.pop()

                    all_paths.setdefault(ending_point, []).append(path)

                    thesis = path.last_thesis

                    self._build_and_assign_contradiction(
                        ending_point.votes.keys() & thesis.votes.keys(),
                        relation, path
                    )

                    for supporting_relation in filter(
                        lambda r: r.type is self.SUPPORT and r.thesis2 is thesis,
                        thesis.relations
                    ):
                        new_thesis = supporting_relation.thesis1

                        if new_thesis in path:
                            continue

                        paths_to_examine.add(path.grow(relation))

            for path1 in all_paths.get(relation.thesis1, []):
                for path2 in all_paths.get(relation.thesis2, []):
                    thesis1 = path1.last_thesis
                    thesis2 = path2.last_thesis

                    self._build_and_assign_contradiction(
                        thesis1.votes.keys() & thesis2.votes.keys(),
                        relation, path1, path2)

    def _normalized_thesis_strength(self, thesis):
        return self.theses_data[thesis].strength / self.max_theses_strength

    def _calc_contradictions_strength(self):
        for contradiction in self.contradictions:
            contradiction_relation = contradiction.relation
            thesis1_strength = self._normalized_thesis_strength(contradiction_relation.thesis1)
            thesis2_strength = self._normalized_thesis_strength(contradiction_relation.thesis2)

            strength = self.relation[contradiction_relation].strength * thesis1_strength * thesis2_strength

            for path in [contradiction.path1, contradiction.path2]:
                if path is None:
                    continue

                for relation in path.path:
                    relation_strength = self.relations[relation].strength
                    thesis1_strength = self._normalized_thesis_strength(relation.thesis1)

                    strength *= relation_strength * thesis1_strength

            contradiction.strength = 1 - strength

    def _calc_users_strength(self):
        for user, user_data in self.users.items():
            strength = 1

            for relation, contradictions in user_data.contradictions:
                strength *= max(map(lambda x: x.strength, contradictions))

            user_data.next_strength = strength

    def _converged(self):
        for user_data in self.users.values():
            error = (user_data.next_strength - user_data.strength) ** 2

            if error > self.error_threshold:
                return False


'''
        # method 2: for each thesis couple, find if they contradict each other
        # then consider these theses votes

        # find inconsistencies
        # ie. user vote Ta and Tb and there is a path [T1, ... Tn] where
        # Ta -x- T1 <- T2 ... <- Tn <- Tb
        # or Ta -x- Tb if such path does not exist
        # f(I) = 1 - |f(Ta)| * |f(T1)| * f(S12) * ... * f(n-1n) * |f(Tn)| * f(Snb) * |f(Tb)|
        for thesis_a in self.theses:
            for thesis_b in self.theses:
                if thesis_a is thesis_b:
                    continue

            contradiction = self._contradiction_between(thesis_a, thesis_b)

            if contradiction is None:
                continue

            for user in thesis_a.votes:
                if user in thesis_b.votes:
                    user.contradictions.append(contradiction)

'''