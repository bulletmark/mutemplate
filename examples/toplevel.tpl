==== Table of squares with default n:
{% include "squares.tpl" %}
====

==== Table of squares with n=n*2:
{% include "squares.tpl" n = t.n * 2 %}
====

==== Table of squares dynamic name and n=n*3:
{% set name = "squares.tpl" %}
{% include {{name}} n = t.n * 3 %}
====

{% include "forloop.tpl" %}

==== Empty file:
{% include "empty.tpl" %}
====
