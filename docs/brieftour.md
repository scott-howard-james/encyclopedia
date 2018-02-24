# Overview

## What Is It?

An Encyclopedia is an abstract container intended for smallish data sets which provides many of the benefits of a relational (and non-relational) database, but with lower syntactic friction.  In particular, an Encyclopedia uses arithmetic expressions typical of first-class objects (e.g. lists, dictionaries) to perform common dataset operations such as merging and subsetting. Encyclopedia supports functional composition, enabling modifications to entire Encyclopedias in a single statement, similar to data frame vectorization.

## But What Is It Really ...

An **Encyclopedia** is a [mapping](https://docs.python.org/3/library/stdtypes.html#typesmapping) class supporting the following additional features:

set operations
: Encyclopedias may be created and combined using standard arithmetic operators

functional composition
: Encyclopedia contents may be modified in their entirety by functions, as well as  other Encyclopedias

and the following optional features:

multi-valued assignments
: keys may be *assigned* single values or *tagged* with multiple values

inversion
: Encyclopedias may swap their key-value pairs

## Say that Differently

In math-speak, a collection of Encyclopedias is a similar to a mathematical [ring](https://en.wikipedia.org/wiki/Ring_%28mathematics%29)  of [relations](http://www.purplemath.com/modules/fcns.htm) where:

- keys serve as the  *domain*
- values serve as the *range*
- ring *addition* is performed by set union on these relations
- *additive inverse* is performed by set difference on these relations
- *multiplication* is performed by functional composition

So to say this yet another way, an Encyclopedia is a collection of key-value pairs which may be combined with other Encyclopedias using set operations and functional operators.

# Ok, But What is it Good For?

Data analysts have an [embarrassment of riches ](https://en.wikipedia.org/wiki/Embarrassment_of_riches) when it comes to manipulating their data.  We have multiple computational elements sitting on our laptop and have immediate access to nearly unlimited computational elements in The Cloud.   We have various topologies to help access and store our data including: tabular (e.g. HDF5), relational (e.g. SQL) and non-relational (e.g. NoSQL).  We have data-analyst-friendly languages (e.g. python, R) with increasingly sophisticated libraries (e.g. [SciPy](https://www.scipy.org), [tidyverse](https://www.tidyverse.org)) to make it all fit together.

On the more modest end of the data deluge resides the localized data: the tabular CSV reports, the hierarchical XML data elements and the binary, human-friendly tag clouds.   The Encyclopedia syntax is intended to be used in this realm, providing a common syntax for the "smaller" data elements, providing a bridge between the scripting container elements (e.g. lists, dictionaries) and the larger data ocean.

As an abstract class, Encyclopedia has limited value on its own.  Two *concrete* Encyclopedias however, are [Relations](https://simple.wikipedia.org/wiki/Relation_(mathematics)) and [Forests](https://en.wikipedia.org/wiki/Tree_(graph_theory)), which were the motivators for the creation of the Encyclopedia abstraction.  

## Relation

A [Relation](https://simple.wikipedia.org/wiki/Relation_(mathematics)) is an Indexed Encyclopedia which may be thought of as a multi-valued extension of a python  [dictionary](https://docs.python.org/3.6/library/stdtypes.html#typesmapping) or function.

![Function vs. Relation](http://www.mathwarehouse.com/algebra/relation/images2/function-vs-relation-with-arrow-chart.png)

In addition to the many-to-one behavior of a Dictionary, a Relation supports all four  [cardinalities](https://en.wikipedia.org/wiki/Cardinality_(data_modeling)):

M:1 (many-to-one)
: a function or dictionary

1:1 (one-to-one)
: an isomorphism or unique alias

1:M (one-to-many)
:  a partition

M:M (many-to-many)
: a general relation

A Relation instance is restricted to one of the cardinalities upon object instantiation.  Relations are invertible [^partially], providing direct mappings from values back to keys.  The following operators are supported:

Notation | Meaning
 ---  |  ---
R[x] = y | either overwrite or append to *x* values depending on cardinality of the Relation (Note: M:1 and 1:1 overwrite, the other two append)
del R[x] | remove *x* from domain of *E* and all associated values for *x*
R1 + R2 | similar to `{**R1, **R2}` for python dictionaries, but with associated cardinality constraints
R1 - R2 | remove any *R2*.keys that lie within *R1*.keys and the associated values
f * R  |  apply f to each element of R
R1 * R2 | apply R1 to each element of R2
~R |  reverse domain and range of R

Using notation similar to a python dictionary comprehension (but to be clear not *actually* valid python), a functional composition might be expressed as:

		{R[f(x)]:f(R[x]) for x in R}
		
A relational composition as:

		{R1[x]:R1[R2[x]) for x in R2}

And an inversion as:

		{R[x]:x for x in R}

As an example of the use of a relation, suppose we need to map qualitative weather conditions to dates:

		weather = Relation()
		weather['2011-7-23']='high-wind'
		weather['2011-7-24']='low-rain'
		weather['2011-7-25']='low-rain'
		weather['2011-7-25']='low-wind'

Note that in the last statement the assignment operator performs an append not an overwrite.  So:

		weather['2014-7-25']

produces a *set* of values:

		 {'low-rain','low-wind'}

Relation also provides an inverse:

		(~weather)['low-rain']

also producing a set of values:

		{'2014-7-25','2014-7-24'} 

See the [paper from SciPy 2015](https://github.com/scott-howard-james/relate/wiki/Rationale) for further exposition on Relation.

## Forest

[Forests](https://en.wikipedia.org/wiki/Tree_(graph_theory)) are Unindexed Encyclopedias formed from collections of [ trees](https://en.wikipedia.org/wiki/Tree_(graph_theory)). 

![Forest](https://qph.ec.quoracdn.net/main-qimg-708af2ed024c2fb8aa37cbac013573d7)

 Syntactically a tree, in our parlance, will grow "upwards"; thus the greater heights of a tree will be closer to the "leaves".  Each *node* in a tree connects upwards to a collection of distinct nodes; conversely each node has at most a single, directly-connecting lower node.  Forests may be combined with other Forests using set operations (*horizontal combination*), and be grown on top of other Forests using composition (*vertical combination*). 

Sub-branches of Forests are obtained through the bracket "get" notation:

	    F[x]

Note that the *keys* used in this bracket notation are different than *nodes*.   In particular, *nodes* within a  Forest are unique; however, *keys* may reference multiple nodes.  Therefore, there is a many-to-one relationship between keys and nodes; thus, the "get" returns *all* sub-branches in F with a root node *keyed* by *x*. 
 
To construct new branches, Forests use the "set" bracket notation.  The bracket notation of Forests allows for several nodes to be *referenced* by a single key, specifically:

    	F[x] = y

means: create a new node, keyed by *y*, *for every* node that is keyed by *x*.  

Forests form the topological foundation of many common hierarchical document formats e.g. XML, JSON, YAML etc...  Non-unique keys enable us to include repeated substructures.  For instance, the get notation in another context, namely when *y* is another forest:

    	F1[x] = F2

grafts the F2 Forest to *all* occurrences of *x* within F1.  An example of a related operation is a YAML alias.  This grafting can also be performed using composition notation:

	    F1 * F2

which means: create a new Forest such when F1 and F2 share a key *x*, the branches of F2[x] are grafted onto F1 at *x*.   An example of a related operation is when a library of sub-documents are instanced onto a document when ready for final document production.   The operations for a Forest are as follows:

Notation | Meaning
 ---  |  ---
F[x] = y | connect new nodes keyed by *y* to nodes keyed by *x*
F[x] | a Forest consisting all nodes reachable from *x*
F[x] = F2 | graft *F2* to *F1* at *x*
del F[x] | prune branches for all nodes keyed by *x*
F.keys() | return all node *keys* within Forest
F.values() | all *nodes* within Forest
F.canopy() | union of all leaf nodes in Forest
F.root(x) | return node(s) of Tree root containing *x*
F1 + F2 | combine two Forests such that common Trees within both Forests will only appear once (*union*)
F1 - F2 | remove Trees contained in *F2* from *F1* (*difference*)
F1 * F2  | for each *x* key common to *F1* and *F2*: graft *F2* onto *F1* at *x*.
f * F  | apply f to each node of F

An extension of a Forest is an Arboretum:  a Forest with inheritable node attributes.  Attributes are assigned using the second position in the bracket assignment, namely:

		F[x, attribute] = value
		
This assigns the key-value pair *(attribute, value)* directly to *x* as well as implicitly to the nodes above *x*.  Retrieving attributes is dynamic:

		F[x, attribute]

meaning, the tree is searched for an attribute starting at the node and descending down the tree until a parent is found with the assignment.  As a motivating example, suppose we had a hierarchical document:

		F['Document'] = 'Section 1'
		F['Section 1'] = 'Section 1.1'
		
Assigning the font 

		F['Section 1', 'font'] = 'Helvetica'

will affect *Section 1* and *Section 1.1*  but will not affect the overall document.  A new section created at the *Document* level

		F['Document'] = 'Section 2'
		
will be unaffected by the font assignment but further subsections below *Section 1.1* 

		F['Section 1.1'] = 'Section 1.1.1'

will have their default font set. 

## Dictionary

Another example of an Encyclopedia is simply a python dictionary which has been Encyclopedia-ified.  This new dictionary will behave much like its derived *dict* but will also support arithmetic set operations and composition.  As an example of the composition feature, if:

        fruit = Dictionary({'apple':'red', 'blueberry':'blue'})
        colors = Dictionary({'red':'FF0000', 'blue':'0000FF', 'green':'00FF00'})

then 

		fruit * colors == Dictionary({'apple': 'FF0000', 'blueberry': '0000FF'})

# Encyclopedia Operations

It may be illustrative (at least for those of us who *like* looking at summary tables) to now show an overview of operations for an Encyclopedia:

Operation | Description
 ---  |  ---
E[x] = y | tag *x* with *y*
del E[x] | remove *x* from domain of *E*  ... also known as [burglary](https://www.youtube.com/watch?v=R9n11xtjZ3Y).  Yep,  that was your obligatory Monty Python reference (*additive inverse*)
E1 + E2 | an encyclopedia created by combining elements of *E2* and *E1* (*union*)
E1 += E2 | add copy of *E2* to *E1* 
E1 - E2 | an encyclopedia created by removing keys of *E2* from *E1* (*difference*)
E1 & E2 | an encyclopedia with keys common to both *E1* and *E2* (intersection)
f * E  | apply *f*[^scaled] to all elements of *E* returning another encyclopedia.  (*functional composition*)
E1 \* E2 | apply *E1*[^composition] to elements of *E2* producing another encyclopedia (*entity composition*)

Certain implementations of Encyclopedia may be multi-valued, meaning that, assignment:

    	E[x] = y

may not *overwrite* the key's value, but instead *append* to the key value or *tag* the key.  Similarly, retrieval:

    	E[x]

may produce a set (or list) of values corresponding to the key.  

For the math-letes, note that encyclopedia addition is inherently commutative:

		E1+E2 == E2+E1

and associative:

		E1+(E2+E3) == (E1+E2)+E3

due to the nature of element-wise set operations.  Composition, however, is *not* necessarily commutative: 

		E1*E2 ?= E2*E1
		
but it is distributive[^composition]:

		E1*(E1+E3) == E1*(E2+E2)
		
as functions act element-wise on the keys.

## Signed Encyclopedia

An Encyclopedia is not a proper ring without the existence of a negative signed Encyclopedia:

		-E
		
Note that we specifically refer to the [unary](https://docs.python.org/3/reference/expressions.html)  operation and not the binary set difference.  Note too that this is a little conceptually unusual, as a negative encyclopedia behaves a bit like [antimatter](https://en.wikipedia.org/wiki/Antimatter), able to negate a collection of key-values, but not necessarily  to serve as a meaningful mapping in our eminently practical universe.  If the unary negative sign is supported by a derived Encyclopedia, the class will be known as a **Signed Encyclopedia**,  and the following features will also be supported:

Identity | Field
 ---  |  ---
Null[x] | existence of Null operator producing None or Error depending on implementation
abs(E) | invert "sign" of Encyclopedia
E + abs(E) | retain only positive ("real") components of the Encyclopedia
abs(E1-E2) + abs(E2-E1) | *symmetric difference*
(Null + E)[x] == E[x] | *additive identity*
(E - E)[x] == Null[x] | *additive inverse*

One important distinction between a Signed Encyclopedia and an Unsigned Encyclopedia is the implementation of the intersection.  For an Unsigned Encyclopedia, we may simply remove the elements of `E1` which are not in `E2`:

		E1&E2 == E1-(E1-E2)

For a Signed Encyclopedia however, this won't work as `-E1` is another Encyclopedia: 

		E1-(E1-E2) == E1-E1+E2 == E2

Instead we must use the Signed Encyclopedia's *abs* operator to remove the negative elements first:

		E1&E2 == E1-abs(E1-E2)

## Indexed Encyclopedia

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

# Past, Present and Future

## Past

As with many abstract types, the concept of Encyclopedia did not emerge from the void ready to be forward instantiated, but rather resulted from the backwards abstraction of specific, concrete implementations (not surprisingly to anyone following along at this point): Relations and Forests. These classes, in turn, were created to scratch particular itches:

- **Relation**:  generalize the notion of a python dictionary to allow for many-to-many relations and provide other conveniences such as invertibility
- **Forest**: provide a tree syntax using standard mathematical notation which can then be used to construct various hierarchical data structures

Syntax may not be everything, but it helps.  A lot.  As many data analysts have found, being able to express  something conveniently may determine whether  the analysis gets done *at all*.   Indeed, much of the power of scripting languages, including python, is the ability to express more complex structures, since the foundational structures (e.g. lists, sets, dictionaries) are so easy to describe.

Addressing Forests specifically, there are a number of different hierarchical structures (e.g. YAML, XML, JSON) which are each essentially trees, topologically, but are supported by different packages and syntaxes.  Moreover, with regard to content generation, they sometimes lack the syntax for easily building more complex trees from simpler ones,  such as, mentioned above, combining two trees either as a simple union or recursively, with one tree nested inside the other.  

## Present

The Encyclopedia specification, and implementations for:

- Relation 
- Forest
- Arboretum
- Dictionary (with a capital "D")

as well as  an:

- Encyclopedic wrapper for XML

Can be obtained at 

-  Github:  [https://github.com/scott-howard-james/encyclopedia](https://github.com/scott-howard-james/encyclopedia)
-  PyPi: [https://pypi.python.org/pypi/encyclopedia/0.25](https://pypi.python.org/pypi/encyclopedia/0.25) (or alternatively  just `pip encyclopedia`)

Note that Encyclopedia has no dependencies outside of the standard python distribution.

## Future

In the near-future, wrappers will be included for YAML and JSON.  Additionally, support for other graph types will be added.

[^scaled]: when *f* is a scalar, assume function is multiplicative

[^partially]: all relations are "invertible" in the sense that domain/range may be swapped; however, relations composed with their inverse will only create Unity properly when the cardinality is 1:M or 1:1

[^composition]: what encyclopedia composition actually *means* will depend on the specific encyclopedia implementation, but the *intention* of composition is to act element-wise, that is independently of other elements in the encyclopedia
