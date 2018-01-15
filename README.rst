What is It
==========

An Encyclopedia is an abstract container intended for smallish data sets
which provides many of the benefits of a relational (and non-relational)
database but with lower syntactic friction. In particular, an
Encyclopedia uses arithmetic expressions typical of first-class python
objects (e.g. lists, dictionaries) to perform common dataset operations
such as merging, subsetting and object combination. Encyclopedias
supports functional composition so as to act on entire Encyclopedias in
a single statement similar to data frame vectorization.

But What is It Really
=====================

An **Encyclopedia** is a mapping with the following additional features:

-  **composition**: Encyclopedia contents may be altered by functions as
   well as other Encyclopedias
-  **set operations**: Encyclopedias may be combined using union,
   difference and intersection operators

Encyclopedias may, optionally, support:

-  **multi-valued**: keys may be *assigned* single values or *tagged*
   with multiple values
-  **inversion**: Encyclopedia may be inverted such that their values
   map to their keys

Say that Differently
====================

In math-speak, an Encyclopedia is a similar toa mathematical
`Ring <https://en.wikipedia.org/wiki/Ring_%28mathematics%29>`__ where:

-  keys serve as the *domain*
-  values serve as the *range*
-  ring *addition* is performed by set union
-  *additive inverse* is performed by set difference
-  *multiplication* is performed by the composition operator

In python-speak this could be called a *MutableMappingRing* derived from
the
`*MutableMapping* <https://docs.python.org/3/library/collections.abc.html>`__
abstract class.

When an *multiplicative inverse* (~E) is available, the Encyclopedia is
a Field of Relations where:

::

    ~E*E == ~E*E == Identity

that is,

::

    (~E*E)[x]==x

In python-speak this could be called a *MutableMappingField*.

Certain implementations of Encyclopedia may be multi-valued meaning
that, assignment:

::

    E[x] = y

May not *overwrite* the key’s value but instead *append* to the key
value or *tag* the key. Similarly, retrieval:

::

    E[x]

May produce a set (or list) of values corresponding to the key.

Encyclopedia Operations
=======================

Unindexed Encyclopedia
----------------------

The list of operations for an Encyclopedia follows:

+-----------------------------------+-----------------------------------+
| Operation                         | Description                       |
+===================================+===================================+
| E[x] = y                          | tag *x* with *y*                  |
+-----------------------------------+-----------------------------------+
| del E[x]                          | remove *x* from domain of *E*,    |
|                                   | also known as *burglary* (yes,    |
|                                   | the obligatory `Monty Python      |
|                                   | reference <https://www.youtube.co |
|                                   | m/watch?v=R9n11xtjZ3Y>`__)        |
+-----------------------------------+-----------------------------------+
| E1 + E2                           | a new Encyclopedia creating by    |
|                                   | combining elements of *E2* and    |
|                                   | *E1*. Note that set operations    |
|                                   | are inherently *commutative*      |
|                                   | (i.e. ``E1+E2==E2+E1``) and       |
|                                   | *associative* (i.e.               |
|                                   | ``E1+(E2+E3)==(E1+E2)+E3)``       |
+-----------------------------------+-----------------------------------+
| E1 += E2                          | add *E2* (copy) to *E1*           |
+-----------------------------------+-----------------------------------+
| E1 \| E2                          | same as ``E1+E2``, but same as    |
|                                   | with python set notation          |
+-----------------------------------+-----------------------------------+
| E1 - E2                           | a new Encyclopedia creating by    |
|                                   | removing elements of *E2* from    |
|                                   | E1.                               |
+-----------------------------------+-----------------------------------+
| E1 & E2                           | elements in both *E1* and *E2*,   |
|                                   | intersection. This is equivalent  |
|                                   | to as ``E1-(E1-E2)`` in an        |
|                                   | *Unsigned* Encyclopedia, but note |
|                                   | the lack of associativity:        |
|                                   | ``(E1-E1) + E2 = E2 != E1 - (E1-E |
|                                   | 2)``.                             |
|                                   | For a *Signed* Encyclopedia,      |
|                                   | however (see below),              |
|                                   | associativity is preserved.       |
+-----------------------------------+-----------------------------------+
| f \* E                            | functional composition: *f(E)*.   |
|                                   | Apply *f* to elements of E        |
|                                   | returning another Encyclopedia.   |
|                                   | When *f* is a scalar assume       |
|                                   | function is multiplicative        |
+-----------------------------------+-----------------------------------+
| E \* f                            | equivalent to *f* \* E            |
+-----------------------------------+-----------------------------------+
| E1 \* E2                          | *composition*: *E1(E2)*; apply    |
|                                   | *E1* to elements of *E2*          |
|                                   | producing another Encyclopedia.   |
|                                   | Note that Encyclopedia            |
|                                   | composition, unlike functional    |
|                                   | composition, is *not* necessarily |
|                                   | commutative (i.e.                 |
|                                   | ``E1*E2?= E2*E1``) however, it is |
|                                   | *distributive* (i.e.              |
|                                   | ``f(E1+E2)==f(E1)+f(E2)``) as the |
|                                   | function acts element-wise on the |
|                                   | keys                              |
+-----------------------------------+-----------------------------------+

An Encyclopedia is not a proper Ring without the existence of a negative
Encyclopedia, -E. Specifically, -E should exist outside the context of a
set difference (which would be of course then called a *burglar*). If
this is supported by a derived Encyclopedia the class will be known as
an *Signed* Encyclopedia and the following will also be supported:

+-----------------------------------+-----------------------------------+
| Identity                          | Field                             |
+===================================+===================================+
| Null[x]                           | existence of Null operator        |
|                                   | producing None or Error depending |
|                                   | on implementation                 |
+-----------------------------------+-----------------------------------+
| abs(E)                            | Invert “sign” of Encyclopedia     |
+-----------------------------------+-----------------------------------+
| E + abs(E)                        | retain only positive/“real”       |
|                                   | components of the Encyclopedia    |
+-----------------------------------+-----------------------------------+
| abs(E1-E2) + abs(E2-E1)           | symmetric difference              |
+-----------------------------------+-----------------------------------+
| (Null + E)[x] == E[x]             | *additive identity*               |
+-----------------------------------+-----------------------------------+
| (E - E)[x] == Null[x]             | *additive inverse*                |
+-----------------------------------+-----------------------------------+
| E1-abs(E1-E2)                     | intersection in a Signed          |
|                                   | Encyclopedia                      |
+-----------------------------------+-----------------------------------+
| E1 - (E1-E2) = E2                 | not intersection, as ``E1-E2``    |
|                                   | will preserve the *E2* values     |
|                                   | with a negative sign              |
+-----------------------------------+-----------------------------------+

Indexed Encyclopedia
--------------------

An *Indexed* Encyclopedia supports inversion, including the following
operators and identities:

+-----------------------------------+-----------------------------------+
| Notation                          | Meaning                           |
+===================================+===================================+
| Unity[x] == x                     | existence of *unity*              |
+-----------------------------------+-----------------------------------+
| ~E                                | *multiplicative inverse* of E     |
|                                   | (reverse domain and range)        |
+-----------------------------------+-----------------------------------+
| (E*~E)[x] == (~E*E)[x] == x       | Encyclopedia composed with its    |
|                                   | inverse produces Unity            |
+-----------------------------------+-----------------------------------+
| (Unity \* E)[x] == E[x]           | Unity composed with an            |
|                                   | Encyclopedia produces that        |
|                                   | Encyclopedia                      |
+-----------------------------------+-----------------------------------+

Ok, for instance?
=================

An Encyclopedia is an abstract class. Two *concrete* Encyclopedias are
`Relations <https://simple.wikipedia.org/wiki/Relation_(mathematics)>`__
and `Forests <https://en.wikipedia.org/wiki/Tree_(graph_theory)>`__.

A **Relation** is a multi-valued extension of a Dictionary. In addition
to the functional (many-to-one, M:1) behavior of a Dictionary, a
Relation supports all four *cardinalities*, specifically: M:1, 1:M, 1:1
and M:M. Relations are invertible  [1]_ providing direct mappings from
values back to keys.

A **Forest** is a collection of **Trees**. Forests use the standard
set/get for constructing Tree branches as well as common tree functions
such as branch(). Forests may be combined with other Forests using set
operations (*horizontal* combination) and be grown on top of other
Forests using composition (*vertical* combination)

Relation
--------

Relations are Indexed Encyclopedias which support all four
*cardinalities*:

-  Many-to-one (M:1), a **dictionary** or **function**
-  One-to-one (1:1), an **isomorphism** or **alias**
-  One-to-many (1:M), a **partition**
-  Many-to-many (M:M), a **general relation**

A Relation instance is restricted to one of the cardinalities upon
object instantiation. The following operators are supported:

+-----------------------------------+-----------------------------------+
| Notation                          | Meaning                           |
+===================================+===================================+
| R[x] = y                          | either overwrite or append to *x* |
|                                   | values depending on cardinality   |
|                                   | of the Relation (Note: M:1 and    |
|                                   | 1:1 overwrite, the other two      |
|                                   | append)                           |
+-----------------------------------+-----------------------------------+
| del R[x]                          | remove *x* from domain of E and   |
|                                   | all associated values for *x*     |
+-----------------------------------+-----------------------------------+
| R1 + R2                           | similar to ``{**E1,**E2}`` for    |
|                                   | python dictionaries but with      |
|                                   | associated cardinality            |
|                                   | constraints                       |
+-----------------------------------+-----------------------------------+
| R1 - R2                           | remove any *R2*.keys that lie     |
|                                   | within *R1*.keys and the          |
|                                   | associated values                 |
+-----------------------------------+-----------------------------------+
| f \* R                            | ``{R[f(x)]:f(R[x]) for x in R}``  |
|                                   |  [2]_                             |
+-----------------------------------+-----------------------------------+
| R1 \* R2                          | ``{R1[x]:R1[R2[x]) for x in R2}`` |
|                                   |  [3]_                             |
+-----------------------------------+-----------------------------------+
| ~R                                | ``{R[x]:x for x in R}``  [4]_     |
+-----------------------------------+-----------------------------------+

Forest
------

Forests are Encyclopedias formed from collections of Trees. A Tree, in
our parlance, grow “upwards”, thus the greater heights of a Tree will be
closer to the *leaves*. Each node in a Tree connects “upwards” to a
collection of distinct nodes; conversely each node has at most a single,
directly-connecting “lower” node.

The bracket notation of Forests allows for several nodes to be
*referenced* by a single key, specifically:

::

    F[x] = y
        

means: create a new node, keyed by *y*, *for every* node that is keyed
by *x*. Similarly, The get notation:

::

    F[x]

Returns a Forest created from *all* subbranches in F with a root node
keyed by *x*. In particular, *nodes* within the Forest are unique;
however, *keys* may reference multiple nodes.

Forests form the topological foundation of many common hierarchical
document formats e.g. XML, JSON, YAML etc… Non-unique keys enable us to
include repeated substructures. For instance, the get notation in
another context, namely when *y* is another forest:

::

    F1[x] = F2

Grafts the F2 Forest to *all* occurrences of *x* within F1. An example
of a related operation is a YAML alias. This grafting can also be
performed using composition notation:

::

    F1 * F2

Which means: create a new Forest such when F1 and F2 share a key *x*,
the branches of F2[x] are grafted onto F1 at *x*.

An example of a related operation is when a library of subdocuments are
instanced onto a document when ready for final document production.

The operations for a Forest are as follows:

+-----------------------------------+-----------------------------------+
| Notation                          | Meaning                           |
+===================================+===================================+
| F[x] = y                          | connect new nodes keyed by *y* to |
|                                   | nodes keyed by *x*, forming       |
|                                   | *branch(es)*                      |
+-----------------------------------+-----------------------------------+
| F[x]                              | a Forest consisting all nodes     |
|                                   | reachable from *x*                |
+-----------------------------------+-----------------------------------+
| F.branch(x)                       | same as F[x] but raise error if   |
|                                   | resulting Forest contains more    |
|                                   | than one Tree                     |
+-----------------------------------+-----------------------------------+
| F[x] = F2                         | graft F2 to F1 at *x*             |
+-----------------------------------+-----------------------------------+
| del F[x]                          | prune branches for all nodes      |
|                                   | keyed by *x*.                     |
+-----------------------------------+-----------------------------------+
| F.copy()                          | (deep) copy of branch within F    |
+-----------------------------------+-----------------------------------+
| F.keys()                          | all node *keys*                   |
+-----------------------------------+-----------------------------------+
| F.values()                        | all *nodes* within Forest         |
+-----------------------------------+-----------------------------------+
| len(F)                            | number of *nodes* within Forest   |
+-----------------------------------+-----------------------------------+
| F.leaves(x)                       | all topmost nodes reachable by    |
|                                   | *x*                               |
+-----------------------------------+-----------------------------------+
| F.canopy()                        | union of all leaf nodes in F      |
+-----------------------------------+-----------------------------------+
| F.sprout(x)                       | function to create a unique node  |
|                                   | ID accessed by key *x*. May be    |
|                                   | called directly by user           |
|                                   | (producing a Node) or called at   |
|                                   | set-time to produce the unique    |
|                                   | node ID.                          |
+-----------------------------------+-----------------------------------+
| F.root(x)                         | return node(s) of Tree root       |
|                                   | containing *x*                    |
+-----------------------------------+-----------------------------------+
| F.below(x)                        | return parent node(s) immediately |
|                                   | *below* *x*                       |
+-----------------------------------+-----------------------------------+
| F.above(x)                        | return child nodes immediately    |
|                                   | *above* *x*                       |
+-----------------------------------+-----------------------------------+
| F1 + F2                           | (set) union of two Forests.       |
|                                   | Common Trees within both Forests  |
|                                   | will only appear once in the      |
|                                   | union.                            |
+-----------------------------------+-----------------------------------+
| F1 - F2                           | remove Trees contained in F2 from |
|                                   | F1                                |
+-----------------------------------+-----------------------------------+
| F1 \* F2                          | for each *x* key common to F1 and |
|                                   | F2: graft F2.branch(x) to F1 at   |
|                                   | *x*.                              |
+-----------------------------------+-----------------------------------+
| f \* J                            | ``{f(x):f(J[x]) for x in J if f[x |
|                                   | ] is not None}``\  [5]_           |
+-----------------------------------+-----------------------------------+

Nodes are hashable, unique elements within a Forest and may be used in
set-get notation. They contain the following properties:

+----------+-----------------------------------------------------------------+
| Notation | Meaning                                                         |
+==========+=================================================================+
| X.alias  | the (non-unique) key for this node within its containing Forest |
+----------+-----------------------------------------------------------------+
| X.id     | the unique ID within Forest (the \__hash__)                     |
+----------+-----------------------------------------------------------------+

.. [1]
   all relations are “invertible” in the sense that domain/range may be
   swapped; however, relations composed with their inverse will only
   create Unity properly when the cardinality is 1:M or 1:1.

.. [2]
   Here we use the brace “{…}” to *loosely* denote the creation of an
   Encylopedia “comprehension” using the syntax of a standard python
   Dictionary comprehension.

.. [3]
   Here we use the brace “{…}” to *loosely* denote the creation of an
   Encylopedia “comprehension” using the syntax of a standard python
   Dictionary comprehension.

.. [4]
   Here we use the brace “{…}” to *loosely* denote the creation of an
   Encylopedia “comprehension” using the syntax of a standard python
   Dictionary comprehension.

.. [5]
   Here we use the brace “{…}” to *loosely* denote the creation of an
   Encylopedia “comprehension” using the syntax of a standard python
   Dictionary comprehension.
