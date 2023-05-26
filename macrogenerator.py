import re

INPUT_FILE = "test1.txt"
# INPUT_FILE = "test2.txt"
# INPUT_FILE = "test3.txt"
# INPUT_FILE = "test4.txt"
# INPUT_FILE = "test5.txt"
# INPUT_FILE = "test6.txt"
# INPUT_FILE = "test7.txt"
# INPUT_FILE = "test8.txt"
# INPUT_FILE = "test9.txt"
# INPUT_FILE = "test10.txt"
# INPUT_FILE = "test11.txt"
OUTPUT_FILE = "output.txt"

PRIMARY_REGEX = re.compile(r"\.DEF\s\S+\s\S+\s\.ENDM|\.REPT\s\S+\s|.ENDM")
NUMBER_REGEX = re.compile(r"-?\d+\.?\d*")

input: str = ""
definitions: dict[str, float] = {}
rept_stack: list[dict["exp":int, "txt":str]] = [{"exp": 1, "txt": ""}]


def definition_handler(line: str):
    [start, key, value, end] = re.split(r"\s", line)

    if end != ".ENDM" or start != ".DEF":
        Exception("Invalid definition")

    if re.search(r"^[a-zA-z]+\w*$", key) is None:
        print(f"Error: Variable name {key} is not valid.")
        return

    if re.fullmatch(NUMBER_REGEX, value) is None:
        print(f"Error: Variable value for {key} is not a number.")
        return

    if key in definitions:
        print(f"Warning: Variable {key} is overwritten.")

    definitions[key] = float(value)


def calculate(eq: str):
    try:
        if eq in definitions:
            return definitions[eq]

        elif re.fullmatch(NUMBER_REGEX, eq):
            return float(eq)

        elif "-" in eq:
            [minuend, subtrahend] = eq.split("-", 1)
            return str(float(calculate(minuend)) - float(calculate(subtrahend)))

        elif "+" in eq:
            [addend1, addend2] = eq.split("+", 1)
            return str(float(calculate(addend1)) + float(calculate(addend2)))

        elif "*" in eq:
            [factor1, factor2] = eq.split("*", 1)
            return str(float(calculate(factor1)) * float(calculate(factor2)))

        elif "/" in eq:
            [dividend, divisor] = eq.split("/", 1)
            return str(float(calculate(dividend)) / float(calculate(divisor)))

        elif "^" in eq:
            [base, exponent] = eq.split("^", 1)
            return str(float(calculate(base)) ** float(calculate(exponent)))

        else:
            return None

    except TypeError:
        return None
    except ZeroDivisionError:
        return None


def expression_handler(expression: str):
    result = calculate(expression)

    if result is None:
        print("Error: Invalid expression. Defaulting to 1.")
        return 1

    result = float(result)

    if result < 0:
        print("Error: Expression result is negative. Defaulting to 1.")
        return 1

    if result == 0:
        print(
            "Warning: Expression result is 0. Repeatable text will not show up in the output."
        )

    elif result.is_integer() is False:
        print("Warning: Expression result is not an integer. Rounding down.")

    return int(result)


with open(INPUT_FILE, "r") as in_file:
    input = in_file.read()

while len(input) > 0:
    search_result = re.search(PRIMARY_REGEX, input)

    if search_result is not None:
        rept_stack[len(rept_stack) - 1]["txt"] += input[: search_result.start()]
        macro = input[search_result.start() : search_result.end()]

        if macro.startswith(".DEF"):
            definition_handler(macro)
            input = input[search_result.end() + 1 :]

        elif macro.startswith(".REPT"):
            expression = macro[6:-1]
            rept_stack.append({"exp": expression_handler(expression), "txt": ""})
            input = input[search_result.end() :]

        elif macro.startswith(".ENDM"):
            if len(rept_stack) == 1:
                print("Error: .ENDM without .REPT")
                input = input[search_result.end() :]
                continue

            last = rept_stack.pop()
            rept_stack[len(rept_stack) - 1]["txt"] += last["txt"] * last["exp"]
            input = input[search_result.end() + 1 :]

        else:
            Exception("Invalid macro")

    else:
        rept_stack[len(rept_stack) - 1]["txt"] += input
        input = ""

while len(rept_stack) > 1:
    print("Error: .REPT without .ENDM")
    last = rept_stack.pop()
    rept_stack[len(rept_stack) - 1]["txt"] += last["txt"] * last["exp"]

with open(OUTPUT_FILE, "w") as out_file:
    out_file.write(rept_stack[0]["txt"])
