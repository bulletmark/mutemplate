## MUTEMPLATE - Compiles Template Files into a Standalone Python File
[![PyPi](https://img.shields.io/pypi/v/mutemplate)](https://pypi.org/project/mutemplate/)
[![AUR](https://img.shields.io/aur/version/mutemplate)](https://aur.archlinux.org/packages/mutemplate/)

[`mutemplate`][mutemplate] is a command line tool you run on your
development host/PC to compile one or more template text files into
a single dynamically created stand-alone Python source file which can be
imported into your project and rendered by specifying the template name
and it's parameter arguments. `mutemplate` creates very lightweight and
memory-efficient templates which are primarily designed for resource
constrained environments such as [MicroPython][mp] on a
micro-controller, although created templates can be used with standard
Python also. `mutemplate` is derived from [`utemplate`][utemplate] and
uses the same template format which is very similar to
[`Django`][django] and [`Jinja`][jinja] templates. (e.g. `{% if %}`,
`{{var}}`).

Only essential template features are offered, for example, "filters"
(`{{var|filter}}`) are syntactic sugar for function calls so are not
implemented, function calls can be used directly instead:
`{{filter(var)}}`).

`mutemplate` compiles templates to Python source code. Think of a
compiled template as a enhanced "`f`" string that can embed `for` loops
and `if/else` conditionals evaluated for the arguments given at
run-time. A `generate()` generator function can be iterated over to
produce consecutive sub-strings of the rendered template. This allows
for minimal memory usage during template substitution and output.
Alternatively, the `render()` function can be used to return the entire
rendered template as a single string.

`mutemplate` provides the following two commands:

|Command  |Alias|Description                                                          |
|---------|-----|---------------------------------------------------------------------|
|`compile`|`c`  |Compile one or more template files into a single Python source file. |
|`render` |`r`  |Render given templates + arguments to output, for exercising/testing.|

These are described in detail in the later [Usage](#usage) section.

This utility has been developed and tested on Linux and should work on
Mac OS and Windows but has not been tried on those platforms. Raise an
issue or start a discussion on the [`mutemplate`][mutemplate] GitHub site
if you want.

## Syntax Reference

- `{{<expr>}}` - evaluates the given Python `<expr>` expression,
  converting it to a string and outputting to rendered content. Can be a
  bare variable name, or a function call, a yield from/await
  expressions, etc.
- `{% if <expr> %}, {% elif <expr> %}, {% else %}, {% endif %}` - analogous to Python's if statement.
- `{% for <var> in <expr> %}, {% endfor %}` - analogous to Python's for statement.
- `{% while <expr> %}, {% endwhile %}` - analogous to Python's while statement.
- `{% set <var> = <expr> %}` - assignment statement.
- `{% include "name.tpl" %}` - include another template. The
name can be a string literal or a variable, e.g. `{% include {{name}} %}`.
- `{# this is a comment #}` - comment line which is not compiled into the template.

Note that all expressions and statements of the types above must be on a single line.

## Template Variables Namespace

`mutemplate` uses a unique approach to pass template variables from your program
into the template. The user passes values to a `generate(*args,
**kwargs)` or `render(*args, **kwargs)` function as keyword and/or dict
arguments, specifically anything the Python [`dict()` constructor can
accept](https://docs.python.org/3/library/stdtypes.html#dict). The passed
keyword arguments are stored as attributes in a `t` namespace which is passed as
the single argument to a template to access the variables, e.g. the user passes
`avalue=5` and it is accessed within the template as `A value = {{t.avalue}}`.

A child template (i.e. a template included from another template) automatically
receives the same `t` namespace argument although you can change and/or add
attribute values by adding keyword arguments to the `include` line. For example,
`{% include name.tpl name="mary" %}` will change the previous example `t.name`
to `mary` whereas `{% include name.tpl name2="mary" %}` will pass `t.name` as
`mark` (i.e. as it was passed to the parent template), and add `t.name2` as
`mary`.

## Example

Create some source template files in a directory on your PC, e.g. in
`templates/*.tpl`. Wherever you want an argument to be substituted in
the template at runtime, use `{{t.var}}` or `{% if t.var %}` etc.
An example simple template file may be:

```sh
$ cat templates/hello.tpl
...
Hello, {{t.name}}!
...
```

Then run the compiler at the command line on your PC:

```sh
$ mutemplate compile -o templates.py templates/*.tpl

# Note: if you only have *.tpl files in the templates directory you can
# alternately specify just the directory name:

$ mutemplate compile -o templates.py templates
```

This compiles all the template files in `templates/*.tpl` into a single
newly created `./templates.py` file. Copy that single file (or just the
`.mpy` bytecode) to your MicroPython project, import it, and use it as
follows:

```python
from microdot import Response
from templates import Template
..
return Response(body=Template("hello").generate(name="mark"))
```

This example is using [Microdot][microdot] to output a web page and is
using `mutemplate` to provide output in "string chunks" which is
the [most efficient
approach](https://microdot.readthedocs.io/en/latest/intro.html#streaming-responses).
You can alternately return the complete string by using `render()` in
the above instead of `generate()`.

> Note: if your template is HTML, then don't forget to set the `Content-Type`
> header for Microdot.

```python
return Response(body=Template("a_html_template").generate(data=data),
                headers={'Content-Type': 'text/html'}
```

More simple text examples are available in the [examples/](examples/)
directory.

## Render Command

Apart from the primary `compile` command line argument, a `render` command is
also provided to render templates to your screen for checking and testing. You
must specify the name of a previously compiled `templates.py` file, the template
name, and it's keyword arguments. Example usage for the above template:

```sh
$ mutemplate render templates.py hello name=mark
```

Arguments must be passed as `name=value` pairs. The value is converted to a
native Python type if possible, otherwise it is treated as a string.
`name=mark` is passed as a string (e.g. same as `'name="mark"'`), `age=42` would
be passed as an int, `values=[1,2,3]` would be passed as a list, etc. You may
need to brush on [shell quoting rules](https://mywiki.wooledge.org/Quotes)
if you want to get tricky with this.

## Differences from `utemplate`

1. `mutemplate` is a command line tool only. It produces a single python
file containing all your compiled templates so no run time compilation
occurs on your Micropython device and no dynamic imports are done by the
template engine.

2. The `utemplate` "`args`"" parameter is not recognised and an error is
reported if it is used in `mutemplate` templates. `utemplate` needs the
`args` parameter to assign values to variable names based on the order
you pass them to the template function but you define the relationship
`var=value` in the call for `mutemplate` so order is not relevant. Note
an advantage of the `mutemplate` approach is that to add a new template
variable you only need to add it to the template and to the calling
function but `utemplate` requires you to also add it to the `args`
parameter line and you also must ensure you maintain correct order which
is easy to get wrong. Also, the clear distinction in your templates
between internal variables (i.e. temporary loop counters/variables etc)
and externally passed-in values (i.e. those in the `t.*` namespace) is
useful.

3. `utemplate` compiles and stores multiple copies of child templates
when they are included multiple times from different parent templates
but `mutemplate` compiles and stores every template once only. All
`mutemplate` parent templates link to the one same child template. E.g.
if you have 10 templates, all including a common `header.tpl` and a
`footer.tpl` then `utemplate` will compile and store 10 copies of the
`header` templates + 10 copies of the `footer` templates, `mutemplate`
will compile and store 1 of each only.

4. `utemplate` (which appears to be unmaintained - no activity for 3
years) has an issue where it breaks and `yields` more sub-strings then
it needs to (whenever it hits **any** "`{`" character) but the parser
has been improved in `mutemplate` to avoid this. `mutemplate` only
breaks to a new `yield` when it must for a Python statement or
expression, so templates are rendered a little more efficiently and
quickly.

5. `mutemplate` also allows `{# comment #}` tags which are missing from
`utemplate` but are provided by [`Django`][django] and [`Jinja`][jinja]
templates and are simple to implement so are added for consistency.

## Usage

Type `mutemplate` or `mutemplate -h` to view the usage summary:

```
usage: mutemplate [-h] {compile,c,render,r} ...

Command line tool to compile one or more template text files into a single
importable python source file.

options:
  -h, --help            show this help message and exit

Commands:
  {compile,c,render,r}
    compile (c)         Compile one or more template files into a single
                        Python source file.
    render (r)          Render given templates + arguments to output, for
                        exercising/testing.
```

Type `mutemplate <command> -h` to see specific help/usage for any
individual command:

### Command `compile`

```
usage: mutemplate compile [-h] [-o OUTFILE] [-w] [-q]
                           template_file [template_file ...]

Compile one or more template files into a single Python source file.

positional arguments:
  template_file         input template file[s] (or dir[s] containing template
                        file[s])

options:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        output file, default is stdout
  -w, --watch           watch specified files forever and run on any change
  -q, --quiet           do not print any informational messages

aliases: c
```

### Command `render`

```
usage: mutemplate render [-h] [-d] template_file template_name [args ...]

Render given templates + arguments to output, for exercising/testing.

positional arguments:
  template_file    python template file
  template_name    name of template to render
  args             arguments for template

options:
  -h, --help       show this help message and exit
  -d, --delineate  delineate chunks with "|" in generated output

aliases: r
```

## Installation and Upgrade

Python 3.7 or later is required. Arch Linux users can install
[`mutemplate` from the
AUR](https://aur.archlinux.org/packages/mutemplate) and skip this
section.

The easiest way to install [`mutemplate`][mutemplate] is to use
[`pipx`][pipx] (or [`pipxu`][pipxu], or [`uv tool`][uvtool]).

```sh
$ pipx install mutemplate
```

To upgrade:

```sh
$ pipx upgrade mutemplate
```

To uninstall:

```sh
$ pipx uninstall mutemplate
```

## License

Copyright (C) 2024 Mark Blakeney. This program is distributed under the
terms of the GNU General Public License. This program is free software:
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation,
either version 3 of the License, or any later version. This program is
distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License at
<http://www.gnu.org/licenses/> for more details.

[mutemplate]: https://github.com/bulletmark/mutemplate
[utemplate]: https://github.com/pfalcon/utemplate
[mp]: https://micropython.org/
[microdot]: https://microdot.readthedocs.io/
[django]: https://docs.djangoproject.com/en/5.0/ref/templates/
[jinja]: https://jinja.palletsprojects.com/en/3.1.x/templates/
[pipx]: https://github.com/pypa/pipx
[pipxu]: https://github.com/bulletmark/pipxu
[uvtool]: https://docs.astral.sh/uv/guides/tools/#installing-tools

<!-- vim: se ai syn=markdown: -->
