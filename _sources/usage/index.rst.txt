:navigation: header
:order: 20

=====
usage
=====

``geometor.model`` provides the symbolic compass-and-straightedge construction engine and golden-section analyzer for the GEOMETOR ecosystem.

Quickstart
----------

.. code-block:: python

   from geometor.model import Model

   model = Model("equilateral")
   A = model.set_point(0, 0, classes=["given"])
   B = model.set_point(1, 0, classes=["given"])
   model.construct_line(A, B)
   c1 = model.construct_circle(A, B)
   c2 = model.construct_circle(B, A)

Targeted Intersections & Deductive Proofs
-----------------------------------------

For multi-step Euclidean propositions and triangle-center constructions, disable global
pairwise intersections (``auto_intersect=False``), select exact roots via geometric
predicates (:meth:`~geometor.model.Model.intersect`), encapsulate auxiliary circles/lines
with :func:`~geometor.model.proposition` or :meth:`~geometor.model.Model.subconstruction`,
and verify exact algebraic theorems with :class:`~geometor.model.proof.ProofMixin`:

.. code-block:: python

   from geometor.model import Model

   mdl = Model("euclid_i1", logger=False, auto_intersect=False)
   A = mdl.given_point(0, 0, ID="A")
   B = mdl.given_point(1, 0, ID="B")

   c1 = mdl.construct_circle(A, B, by="Post.3")
   c2 = mdl.construct_circle(B, A, by="Post.3")
   C = mdl.intersect(c1, c2, side_of=(A, B, +1), ID="C", by="Def.15")

   ab = mdl.set_segment(A, B, by="Post.1")
   ac = mdl.set_segment(A, C, by="Post.1")
   bc = mdl.set_segment(B, C, by="Post.1")
   tri = mdl.set_polygon([A, B, C])

   mdl.assert_equal(ab, ac, bc, by="C.N.1")
   mdl.conclude(tri, kind="qef", by="I.1")

Guides
------

.. collection::
   :sort: order
