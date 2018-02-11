# Overview

## What Is It?

An Encyclopedia is an abstract container intended for smallish data sets which provides many of the benefits of a relational (and non-relational) database but with lower syntactic friction.  In particular, an Encyclopedia uses arithmetic expressions typical of first-class objects (e.g. lists, dictionaries) to perform common dataset operations such as merging and subsetting.  Encyclopedias supports functional composition, enabling modifications to entire Encyclopedias in a single statement, similar to data frame vectorization.

## But What Is It Really ...

An **Encyclopedia** is a [mapping](https://docs.python.org/3/library/stdtypes.html#typesmapping) class supporting the following additional features:

set operations
: Encyclopedias may be created and combined using standard arithmetic operators

functional composition
: Encyclopedia contents may be modified in their entirety by functions as well as  other Encyclopedias

and the following optional features:

multi-valued assignments
: keys may be *assigned* single values or *tagged* with multiple values

inversion
: Encyclopedias may be inverted such that their values map to their keys

## Say that Differently

In math-speak, a collection of Encyclopedias is a similar to a mathematical [ring](https://en.wikipedia.org/wiki/Ring_%28mathematics%29)  of [relations](http://www.purplemath.com/modules/fcns.htm) where:

- keys serve as the  *domain*
- values serve as the *range*
- ring *addition* is performed by set union on these relations
- *additive inverse* is performed by set difference on these relations
- *multiplication* is performed by functional composition

So to say this yet another way, an Encyclopedia is a collection of key-value pairs which may be combined with other Encyclopedias using set operations and functional operators.

## But Why 

Data analysysts have an [embarrassment of riches ](https://en.wikipedia.org/wiki/Embarrassment_of_riches) when it comes to manipulating their data.  We have multiple computation elements sitting on our laptop with immediate access to an unlimited computational elements in the cloud.   We have various topologies to help access and store our data including: tabular (e.g. HDF5), relational (e.g. SQL) and non-relational (e.g. NoSQL).  We have data-analyst-friendly languages (e.g. python, R) with increasingly sophisticated libraries (e.g. [scientfic python](https://www.scipy.org), [tidyverse](https://www.tidyverse.org)) to make it all fit together.

On the more modest end of the data deluge resides the localized data: the tabular CSV reports, the hierarchical XML data elements and the binary, human-friendly tag clouds.   The Encylopedia syntax is intended to be used in this realm, providing a common syntax for the "smaller" data elements, providing a bridge between the scripting container elements (e.g. lists, dictionaries) and the larger data ocean.

## Encyclopedia Operations

It might be illustrative (at least for those of us who *like* looking at summary tables) to show an overview of operations for an Encyclopedia:

Operation | Description
 ---  |  ---
E[x] = y | tag *x* with *y*
del E[x] | remove *x* from domain of *E*  ... also known as [burglary](https://www.youtube.com/watch?v=R9n11xtjZ3Y),  yep,  that was your obligatory Monty Python reference (*additive inverse*)
E1 + E2 | an encyclopedia created by combining elements of *E2* and *E1* (*union*)
E1 += E2 | add copy of *E2* to *E1* 
E1 - E2 | an encyclopedia created by removing keys of *E2* from *E1* (*difference*)
E1 & E2 | an encyclopedia with keys common to both *E1* and *E2* (intersection)
f * E  | apply *f*[^scaled] to all elements of *E* returning another encyclopedia.  (*functional composition*)
E1 \* E2 | apply *E1*[^composition] to elements of *E2* producing another encyclopedia (*entity composition*)

Certain implementations of Encyclopedia may be multi-valued meaning that, assignment:

    	E[x] = y

may not *overwrite* the key's value but instead *append* to the key value or *tag* the key.  Similarly, retrieval:

    	E[x]

May produce a set (or list) of values corresponding to the key.

For the math-letes, note that encyclopedia addition is inherently commutative:

		E1+E2==E2+E1

and associative

		E1+(E2+E3) == (E1+E2)+E3

due to the nature of element-wise set operations.  Composition, however, is *not* necessarily commutative 

		E1*E2?= E2*E1
		
but it is distributive[^composition]:

		E1*(E1+E3)==E1*(E2+E2)
		
as functions act element-wise on the keys.

## Signed Encyclopedias

An Encyclopedia is not a proper ring without the existence of a negative signed Encyclopedia:

		-E
		
Note that we specifically referring to the [unary](https://docs.python.org/3/reference/expressions.html)  operation and not the binary set difference.  Note too that this is a little conceptually unusual as a negative encyclopedia behaves a bit like [antimatter](https://en.wikipedia.org/wiki/Antimatter), able to negate a collection of key-values, but not necessarily  to serve meaningful mapping in our eminently practical universe.  If the unary negative sign is supported by a derived Encyclopedia the class will be known as a **Signed Encyclopedia**  and the following features will also be supported:

Identity | Field
 ---  |  ---
Null[x] | existence of Null operator producing None or Error depending on implementation
abs(E) | invert "sign" of Encyclopedia
E + abs(E) | retain only positive ("real") components of the Encyclopedia
abs(E1-E2) + abs(E2-E1) | *symmetric difference*
(Null + E)[x]==E[x] | *additive identity*
(E - E)[x]==Null[x] | *additive inverse*

One important distinction between a Signed Encyclopedia and an Unsigned Enclopedia is the implementation of the intersection.  For an Unsigned Encyclopedia, we may simply remove the elements of `E1` which are not in `E2`:

		E1&E2==E1-(E1-E2)

For a Signed Encyclopedia however, this won't work as `-E1` is another Encyclopedia: 

		E1-(E1-E2)==E1-E1+E2==E2

Instead we must use the Signed Encyclopedia's *abs* operator to remove the negative elements first:

		E1&E2==E1-abs(E1-E2)

## Indexed Encyclopedias

When a multiplicative inverse:

		~E
		
 is available, the Encyclopedia is a [field](https://en.wikipedia.org/wiki/Field_(mathematics)) where:

	    ~E*E == ~E*E == Identity

that is,

    	(~E*E)[x]==x

Finally, an *Indexed* Encyclopedia supports inversion, including the following operators and identities:

Notation | Meaning
 ---  |  ---
Unity[x] == x | existence of *unity*
~E |  swap domain and range of *E* (*multiplicative inverse*)
(E\*~E)[x] == (~E\*E)[x] == x | Encyclopedia composed with its inverse produces Unity
(Unity * E)[x] == E[x] | Unity composed with an Encyclopedia produces that Encyclopedia

# Ok, But What is Good Gor?

An Encyclopedia is an abstract class and so has limited value on its own.  Two *concrete* Encyclopedias are [Relations](https://simple.wikipedia.org/wiki/Relation_(mathematics)) and[Forests](https://en.wikipedia.org/wiki/Tree_(graph_theory)) and were the motivators for the creation of the Encyclopedia abstraction.

## Relations

A **Relation** is an Indexed Encyclopedia which may be thought of as a multi-valued extension of a python  [dictionary](https://docs.python.org/3.6/library/stdtypes.html#typesmapping).  In addition to the many-to-one behavior of a Dictionary, a Relation supports all four  [cardinalities](https://en.wikipedia.org/wiki/Cardinality_(data_modeling)):

M:1 (many-to-one)
: a function or dictionary

1:1 (one-to-one)
: an isomorphism or unique alias

1:M (one-to-many)
:  a partition

M:M (many-to-many)
: a general relation

A Relation instance is restricted to one of the cardinalities upon object instantiation.  Relations are invertible [^partially] providing direct mappings from values back to keys.  The following operators are supported:

Notation | Meaning
 ---  |  ---
R[x] = y | either overwrite or append to *x* values depending on cardinality of the Relation (Note: M:1 and 1:1 overwrite, the other two append)
del R[x] | remove *x* from domain of *E* and all associated values for *x*
R1 + R2 | similar to `{**E1, **E2}` for python dictionaries but with associated cardinality constraints
R1 - R2 | remove any *R2*.keys that lie within *R1*.keys and the associated values
f * R  |  apply f to each element of R
R1 * R2 | apply R1 to each element of R2
~R |  reverse domain and range of R

Using notation similar to a python dictionary comprehension (but to be clear not *actually* valid python) a functional composition might be expressed as:

		{R[f(x)]:f(R[x]) for x in R}
		
A relational composition as:

		{R1[x]:R1[R2[x]) for x in R2}

And an inversion as:

		{R[x]:x for x in R}

See [here](https://github.com/scott-howard-james/relate/wiki/Rationale) for further details on Relation.

## Forest

Forests are Unindexed Encyclopedias formed from collections of [ trees](https://en.wikipedia.org/wiki/Tree_(graph_theory)).  Syntactically a tree, in our parlance, will grow "upwards"; thus the greater heights of a tree will be closer to the "leaves".  Each *node* in a tree connects upwards to a collection of distinct nodes; conversely each node has at most a single, directly-connecting lower node.  Forests may be combined with other Forests using set operations (*horizontal combination*) and be grown on top of other Forests using composition (*vertical combination*). 

Subbranches of Forests are obtained through the bracket get notation:

	    F[x]

However, an important subtley to note is the *keys* used in this bracket selection are different than *nodes*.   In particular, *nodes* within a  Forest are unique; however, *keys* may reference multiple nodes; that is, there is a many-to-one relationship between keys and nodes.  Thus the bracket-get returns *all* subbranches in F with a root node *keyed* by *x*. 
 
  
To construct new branches, Forests use the set bracket notation.  The bracket notation of Forests allows for several nodes to be *referenced* by a single key, specifically:

    	F[x] = y

means: create a new node, keyed by *y*, *for every* node that is keyed by *x*.  


Forests form the topological foundation of many common hierarchical document formats e.g. XML, JSON, YAML etc...  Non-unique keys enable us to include repeated substructures.  For instance, the get notation in another context, namely when *y* is another forest:

    	F1[x] = F2

Grafts the F2 Forest to *all* occurrences of *x* within F1.  An example of a related operation is a YAML alias.  This grafting can also be performed using composition notation:

	    F1 * F2

Which means: create a new Forest such when F1 and F2 share a key *x*, the branches of F2[x] are grafted onto F1 at *x*.   An example of a related operation is when a library of subdocuments are instanced onto a document when ready for final document production.   The operations for a Forest are as follows:

Notation | Meaning
 ---  |  ---
F[x] = y | connect new nodes keyed by *y* to nodes keyed by *x*
F[x] | a Forest consisting all nodes reachable from *x*
F[x] = F2 | graft *F2* to *F1* at *x*
del F[x] | prune branches for all nodes keyed by *x*
F.keys() | return all node *keys* within Forest
F.values() | all *nodes* within Forest
F.canopy() | union of all leaf nodes in F
F.root(x) | return node(s) of Tree root containing *x*
F1 + F2 | combine two Forests such that common Trees within both Forests will only appear once (*union*)
F1 - F2 | remove Trees contained in *F2* from *F1* (*diference*)
F1 * F2  | for each *x* key common to *F1* and *F2*: graft *F2* onto *F1* at *x*.
f * F  | apply f to each node of F

# Past Breadcrumbs and (Near) Future Plans

As with many abstract types, the concept of Encyclopedia did not emerge from the void ready to be forward instantiated but rather resulted from the backwards abstraction of specific, concrete implementations (not surprisingly to anyone following along at this point): Relations and Forests. These classes, in turn, were created to scratch particular itches:

- **Relation**:  generalize the notion of a python dictionary to allow for many-to-many relations and provide other conveniences such as invertibility
- **Forest**: provide a tree syntax using standard mathematical notation which can them be used to construct various hierarchical data structures

Syntax may not be everything, but it helps.  A lot.  As many data analysts have found, being able to express  something conveniently may determine whether  the analysis gets done *at all*.   Indeed, much of the power of scripting languages, including python, is the ability to express more complex structures since the foundational structures (e.g. lists, sets, dictionaries) are so easy to describe.

Addressing Forests specifically, there are a number of different hierachical structures (e.g. YAML, XML, JSON) which are each essentially trees, topologically, but are supported by different packages and syntaxes.  Moreover, with regard to content generation, they sometimes lack the syntax for easily building more complex trees from simpler ones,  such as, mentioned above, combining two trees either as a simple union or recursively, with one tree nested inside the other.  

Implementations for Relation and Forest, as well as the Encyclopedia specification, can be found [here](https://github.com/scott-howard-james/encyclopedia).  In the near-future, light wrappers will be included for YAML, XML and JSON which will provide Encyclopedia syntax to existing various existing libraries which support these data containers directly.

[^scaled]: when *f* is a scalar, assume function is multiplicative

[^partially]: all relations are "invertible" in the sense that domain/range may be swapped; however, relations composed with their inverse will only create Unity properly when the cardinality is 1:M or 1:1.

[^composition]: what encyclopedia composition actually *means* will depend on the specific encyclopedia implementation but the *intention* of composition is to act element-wise, that is independently of other elements in the encyclopedia
