# Each case: the proposed new source of a function (the "change under review"),
# which symbol changed, whether it truly has a bug, and the ground-truth label.
EVAL_CASES = [
    {
        "name": "swapped_divide",
        "changed_symbol": "divide",
        "diff": "def divide(a, b):\n    return b / a",
        "has_bug": True,
        "true_label": "Operands swapped: returns b/a instead of a/b. Corrupts callers like average that assume a/b order.",
    },
    {
        "name": "swapped_subtract",
        "changed_symbol": "subtract",
        "diff": "def subtract(a, b):\n    return b - a",
        "has_bug": True,
        "true_label": "Operands swapped: returns b-a instead of a-b.",
    },
    {
        "name": "wrong_average_divisor",
        "changed_symbol": "average",
        "diff": "def average(a, b):\n    sum = add(a, b)\n    return divide(sum, 3)",
        "has_bug": True,
        "true_label": "Averages two numbers but divides by 3 instead of 2, so the result is wrong.",
    },
    {
        "name": "clean_rename_variable",
        "changed_symbol": "average",
        "diff": "def average(a, b):\n    total = add(a, b)\n    return divide(total, 2)",
        "has_bug": False,
        "true_label": "No functional issue: local variable renamed sum->total; behavior unchanged (also removes shadowing of the built-in sum).",
    },
    {
        "name": "clean_add_docstring",
        "changed_symbol": "multiply",
        "diff": "def multiply(a, b):\n    \"\"\"Return the product of a and b.\"\"\"\n    return a * b",
        "has_bug": False,
        "true_label": "No functional issue: docstring added, no behavior change.",
    },
]