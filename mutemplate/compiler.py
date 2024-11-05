# Some of the code in this file is based on
# https://github.com/pfalcon/utemplate/blob/master/utemplate/source.py
# which is (c) 2014-2019 Paul Sokolovsky. MIT license.
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO

START = '{'
END = '}'
STATEMENT = '%'
EXPRESSION = '{'
COMMENT = '#'
CLOSE_CHARS = {STATEMENT: '%}', EXPRESSION: '}}', COMMENT: '#}'}

NAMESPACE = 't'

def split_keyword(text: str) -> tuple[str, str]:
    'Split keyword from the rest of the text, return as tuple'
    tokens = text.split(maxsplit=1)
    return tokens[0], tokens[1] if len(tokens) > 1 else ''

@dataclass
class _Compiler:
    filename: Path
    file_out: IO
    funcname: str
    in_literal: bool = False
    stack: list[str] = field(default_factory=list)

    def indent(self, adjust: int = 0) -> None:
        if self.funcname:
            self.file_out.write(f'def {self.funcname}({NAMESPACE}):\n')
            self.stack.append('def')
            self.funcname = ''

        self.file_out.write('    ' * (len(self.stack) + adjust))

    def literal(self, s: str) -> None:
        if s:
            if not self.in_literal:
                self.in_literal = True
                self.indent()
                self.file_out.write('yield """')

            self.file_out.write(s.replace('"', '\\"'))

    def close_literal(self) -> None:
        if self.in_literal:
            self.file_out.write('"""\n')
            self.in_literal = False

    def parse_args(self, args: str) -> str:
        'Normalize arguments string in the form of "a=b, c=d"'
        if not args:
            return ''

        argslist = args.split(',')
        alist = []
        for arg in argslist:
            sa = re.sub(r'\s*=\s*', '=', arg.strip())
            if '=' not in sa[1:-1]:
                raise ValueError(f'Template "{self.filename}": '
                                 f'Require "var=<expr>" in argument: "{sa}" in '
                                 f'argument list "{args}"')
            alist.append(sa)

        return ', '.join(a.strip() for a in alist)

    def parse_statement(self, stmt: str) -> None:
        keyword, rest = split_keyword(stmt)
        if keyword == 'args':
            # This keyword which is used by the original version of
            # utemplate but we don't need it.
            raise NotImplementedError(f'Template "{self.filename}": '
                                      f'"{keyword}" keyword is not supported')
        elif keyword == 'set':
            self.indent()
            self.file_out.write(stmt[3:].strip() + '\n')
        elif keyword == 'include':
            if self.funcname:
                self.indent()

            keyword, rest = split_keyword(rest)
            name = keyword[2:-2] \
                    if keyword[0] == '{' else f'"{Path(keyword[1:-1]).stem}"'

            args = self.parse_args(rest)
            if args:
                args = f', {args}'

            self.indent()
            self.file_out.write(f'yield from Template({name}).generate('
                                f'{NAMESPACE}._dict{args})\n')
        elif rest:
            if keyword == 'elif':
                assert self.stack[-1] == 'if', 'elif without if for "{stmt}"'
                self.indent(-1)
                self.file_out.write(f'{stmt}:\n')
            else:
                self.indent()
                self.file_out.write(f'{stmt}:\n')
                self.stack.append(keyword)
        else:
            if stmt.startswith('end'):
                assert self.stack[-1] == stmt[3:], \
                        f'mismatched "{stmt}" for "{self.stack[-1]}"'
                self.stack.pop()
            elif stmt == 'else':
                assert self.stack[-1] == 'if', 'else without if for "{stmt}"'
                self.indent(-1)
                self.file_out.write('else:\n')
            else:
                assert False, f'Unknown statement "{stmt}"'

    def parse_expression(self, expr: str) -> None:
        self.indent()
        self.file_out.write(f'yield str({expr})\n')

    def parse_line(self, line: str) -> None:
        while line:
            start = line.find(START)
            if start < 0:
                self.literal(line)
                break

            self.literal(line[:start])
            line = line[start:]
            token = line[1]
            if token in CLOSE_CHARS:
                self.close_literal()
                line = line[2:]
                end = line.find(CLOSE_CHARS[token])
                assert end >= 0, f'No matching end for "{START}{token}" ' \
                        f'in "{line.strip()}" in "{self.filename}"'
                content = line[:end].strip()
                line = line[end + 2:]
                if token == STATEMENT:
                    self.parse_statement(content)
                elif token == EXPRESSION:
                    self.parse_expression(content)
                    continue

                if line == '\n':
                    break
            else:
                self.literal(line[0])
                line = line[1:]

def compile(filename_in: Path, file_out: IO, funcname: str) -> None:
    'Compile a template file to a Python function'
    comp = _Compiler(filename_in, file_out, funcname)
    out = False
    with filename_in.open() as file_in:
        for line in file_in:
            out = True
            comp.parse_line(line)

    # If the template file is empty, we need to at least yield an empty
    # string.
    if not out:
        comp.indent()
        comp.file_out.write('yield ""\n')

    comp.close_literal()
