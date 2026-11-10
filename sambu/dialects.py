"""Small, explicit source bridges for Pascal, Delphi and Fortran idioms.

These are translators for a documented interoperable subset, not complete
reimplementations of the original languages. All generated code is parsed and
executed by the normal SAMBU frontend/runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal

DialectName = Literal["pascal", "delphi", "fortran"]


class DialectSyntaxError(ValueError):
    """A source error in one of the supported compatibility profiles."""

    def __init__(self, dialect: str, line: int, message: str) -> None:
        self.dialect = dialect
        self.line = line
        self.message = message
        super().__init__(f"{dialect} dialect, line {line}: {message}")


@dataclass(frozen=True, slots=True)
class DialectResult:
    dialect: str
    source: str
    generated_source: str
    source_lines: tuple[int, ...]


def _strip_comment(
    line: str,
    dialect: str,
    block_comment: list[str | None] | None = None,
) -> str:
    """Remove dialect comments, including multi-line Pascal/Delphi blocks."""
    if dialect in {"pascal", "delphi"} and block_comment is not None and block_comment[0]:
        closing = block_comment[0]
        end = line.find(closing)
        if end < 0:
            return ""
        line = line[end + len(closing):]
        block_comment[0] = None

    quote: str | None = None
    escaped = False
    i = 0
    while i < len(line):
        char = line[i]
        if quote:
            if char == quote and not escaped:
                quote = None
            if char == "\\" and not escaped:
                escaped = True
            else:
                escaped = False
            i += 1
            continue
        if char in "'\"":
            quote = char
            i += 1
            continue
        if dialect == "fortran" and char == "!":
            return line[:i]
        if dialect in {"pascal", "delphi"}:
            if line.startswith("//", i):
                return line[:i]
            if char == "{":
                end = line.find("}", i + 1)
                if end < 0:
                    if block_comment is not None:
                        block_comment[0] = "}"
                    return line[:i]
                line = line[:i] + " " + line[end + 1:]
                continue
            if line.startswith("(*", i):
                end = line.find("*)", i + 2)
                if end < 0:
                    if block_comment is not None:
                        block_comment[0] = "*)"
                    return line[:i]
                line = line[:i] + " " + line[end + 2:]
                continue
        i += 1
    return line

def _split_csv(text: str) -> list[str]:
    """Split a short argument/declaration list without splitting nested calls."""
    result: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    escaped = False
    for index, char in enumerate(text):
        if quote:
            if char == quote and not escaped:
                quote = None
            if char == "\\" and not escaped:
                escaped = True
            else:
                escaped = False
            continue
        if char in "'\"":
            quote = char
        elif char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == "," and depth == 0:
            item = text[start:index].strip()
            if item:
                result.append(item)
            start = index + 1
    tail = text[start:].strip()
    if tail:
        result.append(tail)
    return result


def _fold_identifiers(text: str, known_names: set[str] | frozenset[str] = frozenset()) -> str:
    """Apply the case-insensitive identifier convention of these dialects."""
    out: list[str] = []
    i = 0
    quote: str | None = None
    escaped = False
    while i < len(text):
        char = text[i]
        if quote:
            out.append(char)
            if char == quote and not escaped:
                quote = None
            if char == "\\" and not escaped:
                escaped = True
            else:
                escaped = False
            i += 1
            continue
        if char in "'\"":
            quote = char
            out.append(char)
            i += 1
            continue
        if char.isalpha() or char == "_":
            end = i + 1
            while end < len(text) and (text[end].isalnum() or text[end] == "_"):
                end += 1
            identifier = text[i:end]
            folded = identifier.casefold()
            # Unit constants retain SAMBU's canonical SI spellings while
            # ordinary identifiers follow Pascal/Fortran case-insensitivity.
            units = {
                "k": "K", "j": "J", "kj": "kJ", "ev": "eV",
                "pa": "Pa", "hz": "Hz", "n": "N", "l": "L",
            }
            out.append(folded if folded in known_names else units.get(folded, folded))
            i = end
            continue
        out.append(char)
        i += 1
    return "".join(out)


def _expression(
    text: str, dialect: str, *, condition: bool = False,
    known_names: set[str] | frozenset[str] = frozenset(),
) -> str:
    value = text.strip().rstrip(";").strip()
    if dialect in {"pascal", "delphi"}:
        value = re.sub(r"<>", "!=", value)
        value = re.sub(r"\bdiv\b", "/", value, flags=re.IGNORECASE)
        value = re.sub(r"\bmod\b", "%", value, flags=re.IGNORECASE)
    else:
        replacements = {
            r"\.true\.": "true", r"\.false\.": "false",
            r"\.and\.": "and", r"\.or\.": "or", r"\.not\.": "not",
            r"\.eqv\.": "==", r"\.neqv\.": "!=", r"\.eq\.": "==",
            r"\.ne\.": "!=", r"\.lt\.": "<", r"\.le\.": "<=",
            r"\.gt\.": ">", r"\.ge\.": ">=",
        }
        for pattern, replacement in replacements.items():
            value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
        if condition:
            value = re.sub(r"(?<![<>=!])=(?!=)", "==", value)
    return _fold_identifiers(value, known_names)


def _parameter_names(raw: str, dialect: str) -> tuple[str, ...]:
    params: list[str] = []
    if not raw.strip():
        return ()
    parts = _split_csv(raw.replace(";", ",") if dialect in {"pascal", "delphi"} else raw)
    for part in parts:
        item = part.strip()
        if dialect in {"pascal", "delphi"}:
            item = re.sub(r"\b(const|var|out|in|constref)\s+", "", item, flags=re.IGNORECASE)
            item = item.split(":", 1)[0].strip()
        else:
            item = item.split("*", 1)[0].strip()
        if not re.fullmatch(r"[A-Za-z_]\w*", item):
            raise ValueError(f"unsupported parameter declaration {part!r}")
        params.append(item.casefold())
    return tuple(params)


def _declarations(line: str, dialect: str) -> list[tuple[str, str | None]] | None:
    """Return typed declarations as (name, initializer) pairs."""
    if dialect in {"pascal", "delphi"}:
        match = re.match(r"^(?:var|const)\s+(.+)$", line, re.IGNORECASE)
        if match:
            line = match.group(1).strip()
        else:
            match = re.match(
                r"^([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s*:\s*([\w.]+)(?:\s*:=\s*(.+))?\s*;?$",
                line, re.IGNORECASE,
            )
            if not match:
                return None
            names, _type_name, initializer = match.groups()
            return [
                (name.strip().casefold(), initializer.strip() if initializer else None)
                for name in names.split(",")
            ]
        if not line:
            return []
        const_match = re.match(r"^([A-Za-z_]\w*)\s*=\s*(.+);?$", line)
        if const_match:
            return [(const_match.group(1).casefold(), const_match.group(2).rstrip(";"))]
        typed_match = re.match(
            r"^([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s*:\s*([\w.]+)(?:\s*:=\s*(.+))?\s*;?$",
            line, re.IGNORECASE,
        )
        if typed_match:
            names, _type_name, initializer = typed_match.groups()
            return [
                (name.strip().casefold(), initializer.strip() if initializer else None)
                for name in names.split(",")
            ]
        return []

    match = re.match(
        r"^(integer|int|real|double\s+precision|logical|character(?:\s*\([^)]*\))?)(?:\s*,\s*[^:]*)?\s*::\s*(.+)$",
        line, re.IGNORECASE,
    )
    if not match:
        return None
    entries: list[tuple[str, str | None]] = []
    for item in _split_csv(match.group(2)):
        item_match = re.match(r"^([A-Za-z_]\w*)(?:\s*=\s*(.+))?$", item)
        if not item_match:
            raise ValueError(f"unsupported Fortran declaration item {item!r}")
        entries.append((item_match.group(1).casefold(), item_match.group(2)))
    return entries


def transpile(source: str, dialect: DialectName | str) -> DialectResult:
    """Translate the safe common subset into canonical SAMBU source.

    Supported statements: simple typed declarations, assignment-once bindings,
    functions/procedures, output, conditionals and counted loops. Type
    annotations are erased: this bridge does not claim source type equivalence.
    Mutable variables, pointers, exceptions, arbitrary records, compiler
    directives and GUI frameworks are intentionally rejected or documented
    as unsupported rather than silently miscompiled.
    """
    normalized = str(dialect).casefold().replace("object-pascal", "delphi")
    aliases = {
        "object pascal": "delphi",
        "free-form fortran": "fortran",
        "f90": "fortran",
        "f95": "fortran",
        "pas": "pascal",
        "dpr": "delphi",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in {"pascal", "delphi", "fortran"}:
        raise ValueError("dialect must be 'pascal', 'delphi', or 'fortran'")

    output: list[str] = []
    source_lines: list[int] = []
    assigned: set[str] = set()
    known_names: set[str] = set()
    block_stack: list[str] = []
    function_results: list[str | None] = []
    pending_if_close = False
    program_started = False
    block_comment: list[str | None] = [None]

    def emit(value: str, line_number: int) -> None:
        output.append(value)
        source_lines.append(line_number)

    for line_number, original in enumerate(source.splitlines(), 1):
        line = _strip_comment(original, normalized, block_comment).strip()
        if not line:
            continue
        low = line.casefold().strip()

        if pending_if_close and low != "else" and not low.startswith("else ") and not low.startswith("else\t") and not low.startswith("end else"):
            emit("}", line_number)
            if block_stack and block_stack[-1] == "if":
                block_stack.pop()
            pending_if_close = False

        # Program/unit/module scaffolding does not have runtime semantics here.
        if normalized in {"pascal", "delphi"}:
            if re.match(r"^(program|unit)\s+\w+\s*;?$", low):
                continue
            if low == "uses" or low.startswith("uses "):
                continue
            if low in {"interface", "implementation", "initialization", "finalization", "var", "const", "type"}:
                continue
            if low in {"public", "private", "protected", "published", "strict private", "strict protected"}:
                continue
            # Property declarations are discarded as declaration metadata only.
            # They do not create executable SAMBU properties or backing fields.
            if low.startswith("property "):
                continue
        else:
            if re.match(r"^(program|module)\s+\w+$", low):
                continue
            if low in {"implicit none", "contains"} or low.startswith("use "):
                continue

        if normalized in {"pascal", "delphi"} and low == "begin":
            if not program_started and not block_stack:
                program_started = True
                continue
            if block_stack and block_stack[-1] in {"function", "if", "else", "do"}:
                continue
            emit("{", line_number)
            block_stack.append("block")
            continue

        # Function/procedure declarations.
        if normalized in {"pascal", "delphi"}:
            fn = re.match(
                r"^(?:function|procedure)\s+([A-Za-z_]\w*)\s*\((.*?)\)\s*(?::\s*[\w.]+)?\s*;?$",
                line, re.IGNORECASE,
            )
            if fn:
                name, raw_params = fn.group(1).casefold(), fn.group(2)
                result_name = name if low.startswith("function") else None
                params = _parameter_names(raw_params, normalized)
                known_names.update(params)
                if result_name is not None:
                    known_names.add(result_name)
                emit(f"fn {name}({', '.join(params)}) {{", line_number)
                block_stack.append("function")
                function_results.append(result_name)
                continue
        else:
            fn = re.match(
                r"^(?:(?:integer|real|double\s+precision|logical|character(?:\s*\([^)]*\))?)\s+)?"
                r"(recursive\s+)?(function|subroutine)\s+([A-Za-z_]\w*)\s*\((.*?)\)"
                r"(?:\s+result\s*\(\s*([A-Za-z_]\w*)\s*\))?\s*$",
                line, re.IGNORECASE,
            )
            if fn:
                kind, name, raw_params, result_name = fn.group(2).casefold(), fn.group(3), fn.group(4), fn.group(5)
                name = name.casefold()
                result_name = result_name.casefold() if result_name else None
                result_name = result_name or (name if kind == "function" else None)
                params = _parameter_names(raw_params, normalized)
                emit(f"fn {name}({', '.join(params)}) {{", line_number)
                block_stack.append("function")
                function_results.append(result_name)
                continue

        # Fortran program unit terminators are not executable block closures.
        if normalized == "fortran" and re.match(r"^end\s*(?:program|module)(?:\s+\w+)?$", low):
            continue

        # Structural terminators.
        if normalized == "fortran":
            terminator = re.match(r"^end\s+(if|do|function|subroutine)\b(?:\s+\w+)?\s*$", low)
            if terminator:
                kind = terminator.group(1)
                expected = {"if": {"if", "else"}, "do": {"do"}, "function": {"function"}, "subroutine": {"function"}}[kind]
                if not block_stack or block_stack[-1] not in expected:
                    raise DialectSyntaxError(normalized, line_number, f"unmatched END {kind.upper()}")
                block_stack.pop()
                emit("}", line_number)
                if kind in {"function", "subroutine"} and function_results:
                    function_results.pop()
                continue
        else:
            if low.startswith("end else"):
                if not block_stack or block_stack[-1] != "if":
                    raise DialectSyntaxError(normalized, line_number, "END ELSE without an open IF")
                block_stack.pop()
                emit("} else {", line_number)
                block_stack.append("else")
                pending_if_close = False
                continue
            if low in {"end", "end;", "end."} or low.startswith("end;") or low.startswith("end."):
                if not block_stack:
                    continue
                top = block_stack[-1]
                if top == "if":
                    pending_if_close = True
                    continue
                block_stack.pop()
                emit("}", line_number)
                if top == "function" and function_results:
                    function_results.pop()
                if low.endswith(".") and not block_stack:
                    program_started = True
                continue

        # Alternate branch. Fortran keeps IF open until END IF; Pascal/Delphi
        # place END immediately before ELSE.
        if normalized == "fortran" and low == "else":
            if not block_stack or block_stack[-1] != "if":
                raise DialectSyntaxError(normalized, line_number, "ELSE without a matching IF")
            block_stack.pop()
            emit("} else {", line_number)
            block_stack.append("else")
            continue
        if low == "else" or low == "else begin" or low.startswith("else "):
            if not pending_if_close or not block_stack or block_stack[-1] != "if":
                raise DialectSyntaxError(normalized, line_number, "ELSE without a matching END IF")
            block_stack.pop()
            emit("} else {", line_number)
            block_stack.append("else")
            pending_if_close = False
            continue

        # Opening conditional blocks.
        if normalized in {"pascal", "delphi"}:
            conditional = re.match(r"^if\s+(.+?)\s+then(?:\s+begin)?\s*;?$", line, re.IGNORECASE)
        else:
            conditional = re.match(r"^if\s*\((.+)\)\s*then\s*$", line, re.IGNORECASE)
        if conditional:
            condition = _expression(conditional.group(1), normalized, condition=True, known_names=known_names)
            emit(f"if {condition} {{", line_number)
            block_stack.append("if")
            continue

        # Counted loops use an inclusive upper bound in Pascal and Fortran.
        if normalized in {"pascal", "delphi"}:
            loop = re.match(
                r"^for\s+([A-Za-z_]\w*)\s*:=\s*(.+?)\s+(to|downto)\s+(.+?)\s+do(?:\s+begin)?\s*;?$",
                line, re.IGNORECASE,
            )
            if loop:
                variable, start, direction, stop = loop.groups()
                variable = variable.casefold()
                known_names.add(variable)
                if direction.casefold() == "to":
                    iterable = f"range({_expression(start, normalized, known_names=known_names)}, ({_expression(stop, normalized, known_names=known_names)}) + 1)"
                else:
                    iterable = f"range({_expression(start, normalized, known_names=known_names)}, ({_expression(stop, normalized, known_names=known_names)}) - 1, -1)"
                emit(f"for {variable} in {iterable} {{", line_number)
                block_stack.append("do")
                continue
        else:
            loop = re.match(
                r"^do\s+([A-Za-z_]\w*)\s*=\s*(.+?)\s*,\s*(.+?)(?:\s*,\s*(.+?))?$",
                line, re.IGNORECASE,
            )
            if loop:
                variable, start, stop, step = loop.groups()
                variable = variable.casefold()
                known_names.add(variable)
                step_expr = _expression(step, normalized, known_names=known_names) if step else "1"
                if step_expr.startswith("-"):
                    inclusive = f"({_expression(stop, normalized, known_names=known_names)}) - 1"
                else:
                    inclusive = f"({_expression(stop, normalized, known_names=known_names)}) + 1"
                emit(f"for {variable} in range({_expression(start, normalized, known_names=known_names)}, {inclusive}, {step_expr}) {{", line_number)
                block_stack.append("do")
                continue

        # A bare nested BEGIN creates a block; a BEGIN after a control header
        # is consumed because the header already emitted its opening brace.
        if normalized in {"pascal", "delphi"} and low == "begin":
            if block_stack and block_stack[-1] in {"function", "if", "else", "do"}:
                continue
            emit("{", line_number)
            block_stack.append("block")
            continue

        declaration = _declarations(line, normalized)
        if declaration is not None:
            for name, initializer in declaration:
                known_names.add(name)
                if initializer is not None:
                    if name in assigned:
                        raise DialectSyntaxError(normalized, line_number, f"'{name}' is assigned more than once; SAMBU bindings are immutable")
                    assigned.add(name)
                    emit(f"let {name} = {_expression(initializer, normalized, known_names=known_names)}", line_number)
            continue

        # Reject syntax that would otherwise be mistaken for an expression or
        # an assignment and silently produce a different program.
        if re.search(
            r"\b(?:goto|case|record|object|pointer|allocate|deallocate|try|except|finally|raise|with|while|repeat|until|select|where|forall|equivalence|common|namelist|bind)\b",
            low,
        ) or re.search(r"=\s*class\b", low):
            raise DialectSyntaxError(normalized, line_number, "construct is outside the supported compatibility subset")

        # Output forms.
        if normalized in {"pascal", "delphi"}:
            output_match = re.match(r"^(?:write|writeln)\s*\((.*)\)\s*;?$", line, re.IGNORECASE)
            if output_match:
                args = _split_csv(output_match.group(1))
                payload = args[0] if len(args) == 1 else "[" + ", ".join(args) + "]"
                emit(f"print({_expression(payload, normalized, known_names=known_names)})", line_number)
                continue
        else:
            output_match = re.match(r"^print\s*\*\s*,\s*(.+)$", line, re.IGNORECASE)
            if output_match:
                args = _split_csv(output_match.group(1))
                payload = args[0] if len(args) == 1 else "[" + ", ".join(args) + "]"
                emit(f"print({_expression(payload, normalized, known_names=known_names)})", line_number)
                continue
            output_match = re.match(r"^write\s*\(\s*\*\s*,\s*\*\s*\)\s*(.*)$", line, re.IGNORECASE)
            if output_match:
                args = _split_csv(output_match.group(1))
                payload = args[0] if len(args) == 1 else "[" + ", ".join(args) + "]"
                emit(f"print({_expression(payload, normalized, known_names=known_names)})", line_number)
                continue

        # Calls and explicit returns.
        call = re.match(r"^call\s+([A-Za-z_]\w*\s*\(.*\))\s*;?$", line, re.IGNORECASE)
        if call:
            emit(_expression(call.group(1), normalized, known_names=known_names), line_number)
            continue
        if low in {"return", "return;"}:
            emit("return", line_number)
            continue
        exit_match = re.match(r"^exit\s*\((.*)\)\s*;?$", line, re.IGNORECASE)
        if exit_match:
            emit(f"return {_expression(exit_match.group(1), normalized, known_names=known_names)}", line_number)
            continue

        assignment = re.match(r"^([A-Za-z_]\w*)\s*(:=|=)\s*(.+?)\s*;?$", line)
        if assignment:
            name, _operator, rhs = assignment.groups()
            name = name.casefold()
            known_names.add(name)
            if function_results and function_results[-1] == name:
                emit(f"return {_expression(rhs, normalized, known_names=known_names)}", line_number)
            elif name in assigned:
                raise DialectSyntaxError(normalized, line_number, f"'{name}' is assigned more than once; SAMBU bindings are immutable")
            else:
                assigned.add(name)
                emit(f"let {name} = {_expression(rhs, normalized, known_names=known_names)}", line_number)
            continue

        if line.endswith(";"):
            line = line[:-1].strip()
        if not line:
            continue
        emit(_expression(line, normalized, known_names=known_names), line_number)

    if block_comment[0] is not None:
        raise DialectSyntaxError(
            normalized,
            max(1, len(source.splitlines())),
            f"unclosed block comment: {block_comment[0]}",
        )
    if pending_if_close:
        emit("}", max(1, len(source.splitlines())))
        if block_stack and block_stack[-1] == "if":
            block_stack.pop()
    if block_stack:
        raise DialectSyntaxError(normalized, max(1, len(source.splitlines())), f"unclosed block(s): {', '.join(block_stack)}")
    generated = "\n".join(output) + ("\n" if output else "")
    return DialectResult(normalized, source, generated, tuple(source_lines))


def execute_dialect(source: str, dialect: DialectName | str, *, output=None):
    """Translate and execute a supported dialect source file with SAMBU."""
    from .interpreter import execute

    translated = transpile(source, dialect)
    if output is None:
        return execute(translated.generated_source)
    return execute(translated.generated_source, output=output)


__all__ = ["DialectName", "DialectResult", "DialectSyntaxError", "execute_dialect", "transpile"]
