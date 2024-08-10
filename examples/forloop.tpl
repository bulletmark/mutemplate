{# comment - requires n to be passed #}
==== For loop:
{% for i in range(1, t.n + 1) %}
{% if i % 2 %}
{{i}} is odd
{% elif i == 3 %}
{{i}} is 3
{% else %}
{{i}} is even
{% endif %}
{% endfor %}

==== While loop:
{% set i = 5 %}
{% while i > 0 %}
{{i}}
{% set i = i - 1 %}
{% endwhile %}

==== Include child/child template:
{% include "squares.tpl" %}
