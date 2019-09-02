class User:
    def __init__(name):
        assert type(name) is str and len(name) > 0, 'illegal name'

        self.name = name

    def __eq__(self, other):
        return self is other or isinstance(other, User) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Problem:
    def __init__(self, question):
        assert type(question) is str and len(question) > 0, 'illegal question'

        self.question = question

        self.theses = set()
        self.relations = set()

    def add_thesis(self, thesis):
        assert isinstance(thesis, Thesis), 'illegal thesis'

        self.theses.add(thesis)

    def add_relation(self, relation):
        assert isinstance(relation, Relation), 'illegal relation'
        assert relation.thesis1 in self.theses, 'unknown thesis 1'
        assert relation.thesis2 in self.theses, 'unknown thesis 2'

        self.relations.add(relation)


class Thesis:
    def __init__(content, is_solution):
        assert type(content) is str and len(content) > 0, 'illegal content'
        assert type(is_solution) is bool, 'illegal is_solution'

        self.content = content
        self.is_solution = is_solution

        self.votes = dict()  # from users to -1/+1

    def __eq__(self, other):
        return self is other or isinstance(other, Thesis) and self.content == other.content

    def __hash__(self):
        return hash(self.content)

    def upvote(self, user):
        assert isinstance(user, User), 'illegal user'

        self.votes[user] = +1

    def downvote(self, user):
        assert isinstance(user, User), 'illegal user'

        self.votes[user] = -1


class Relation:
    SUPPORT = object()
    CONTRADICTION = object()

    def __init__(self, relation_type, thesis1, thesis2):
        assert relation_type in (Relation.CONTRADICTION, Relation.SUPPORT), 'illegal relation_type'
        assert isinstance(thesis1, Thesis), 'illegal thesis1'
        assert isinstance(thesis2, Thesis), 'illegal thesis2'

        self.type = relation_type
        self.thesis1 = thesis1
        self.thesis2 = thesis2

        self.votes = dict()  # from user to -1/+1

    def __eq__(self, other):
        return self is other or (
            isinstance(other, Relation) and
            self.type is other.type and
            self.thesis1 == other.thesis1 and
            self.thesis2 == other.thesis2
        )

    def __hash__(self):
        return hash(self.type) + hash(self.thesis1) + hash(self.thesis2)

    def upvote(self, user):
        assert isinstance(user, User), 'illegal user'

        self.votes[user] = +1

    def downvote(self, user):
        assert isinstance(user, User), 'illegal user'

        self.votes[user] = -1
