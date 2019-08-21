# Democracy Revisited

This project aims to build a voting system focused on reasoning
and thesis instead of on opinions and people.

## Model

DR model comprises of:

* problem

  A problem, in this phase of the project, is a question
  whose answer can be either yes or no.

* thesis

  A statement in favor of a possible answer.

* support relation between thesis

  It is a directed link between thesis A and
  thesis B meaning that if A is true then B is
  also true.

* contradiction relation

  It is a link between thesis A and B meaning
  that only one thesis can be true.

## User actions

A user can edit the model either adding new
thesis or new relations between them.

Possible actions:

* post a new thesis

* link thesis with a support relation

* link thesis with a contradiction relation

TODO: edit thesis. Thesis cannot be modified if voted, because any change possibly invalidates them. Thesis editing must occur in the form of comments/forum. Or if any change occurs than every vote is invalidated and voting users are requested to express again their opinion.

TODO: remove thesis. Same as above. Removing a thesis have a cascading effect on every relation insisting on it. Plus, every user that expressed an opinion can object.

TODO: remove relations

## The voting system

Users express opinions on both thesis and relations. They can:

* upvote a thesis

  A user upvote a thesis if she/he thinks that
  such thesis is true.

* downvote a thesis

  A user downvote a thesis if she/he thinks that such thesis is false.

* upvote a relation, either of support or contradiction

  A user upvote a relation if she/he thinks that such relation holds.

* downvote a relation, either of support or contradiction

  A user downvote a relation if she/he thinks that such relation does not hold.

## How to determine voting results

An answer has a strength which is the sum of the strength of its thesis. The winning answer
is the one with greater strength.

f(A) = sum f(T) for every T supporting A

f(T) = 0 **if** sum f(Uup) <= sum f(Udown)

f(T) = sum f(Uup) / sum f(U) + sum f(Ts) * f(S) **otherwise**

where:
* Uup is the set of upvoters of thesis T
* Udown is the set of downvoters of thesis T
* U is the set of all users partecipating to the discussion
* Ts is the set of thesis with an ingoing support relation to T, considering Ts which does not form cycles with T
* f(S) is the strengh of such support

f(S) = 0 **if** sum f(Uup) <= sum f(Udown)

f(S) = sum f(Uup) / sum f(U) **otherwise**

f(U) = 1 **if** there are no inconsistencies in U votes

f(U) = prod f(I) **otherwise**

where I is the set of inconsistencies in U votes.

## Inconsistencies in votes

There are many kind of inconsistencies:

**Type 1** vote two thesis that contradict
  each other.

Two thesis contradict each other if there is a contradiction relation that holds.
  
A contradiction holds between T1 and T2 when:
 * there is a contradiction relation between T1 and Ta that holds, that is f(S) > 0
 * there is a path: Ta <- Tb <- .. T1
  with supporting relation that holds (ei. f(S) > 0) going from T1 to Ta

*Note*: it is an inconcistency *even if* the user downvotes any of the involved relations, that is if she/he does not agree with the majority of the users.

f(I_type_1) = 1 - |f(T1)| * |f(Ta)| * f(Sab) * |f(Tb)| * f(Sbc) * ... * |f(T2)|

where:
* |f(T)| is f(T) / max f(T)
* T1, T2 are the upvoted thesis that contradict each other.

## Calculating strengths

As you can see thesis strength depends on users strength and vice versa.

The proposed algorithm is:
1. assume f(U) = 1 for every user
1. calculate f(T) and f(S)
1. calculate f(U)
1. if strengths converge stop, otherwise repeat from step 2

