import re
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

transformations = standard_transformations + (implicit_multiplication_application,)

def clean_latex_to_sympy(latex_str: str) -> str:
    s = latex_str.strip()
    s = s.replace(r"\frac", " ").replace(r"\ln", "log").replace(r"\log", "log")
    s = s.replace(r"\mu", "mu").replace(r"\hbar", "hbar").replace(r"\beta", "beta")
    s = s.replace(r"\alpha", "alpha").replace(r"\sum", "sum")
    s = re.sub(r'\{([^{}]+)\}', r'(\1)', s)
    s = re.sub(r'\\([a-zA-Z]+)', r'\1', s)
    s = s.replace("^", "**")
    return s

def verify_hypothesis_equations(equations: list) -> list:
    results = []
    for raw_eq in equations:
        cleaned = clean_latex_to_sympy(raw_eq)
        # If chained equality a = b = c, split and check the first relation
        parts = cleaned.split("=")
        if len(parts) >= 2:
            test_eq = f"{parts[0].strip()} - ({parts[-1].strip()})"
        else:
            test_eq = cleaned

        try:
            parsed = parse_expr(test_eq, transformations=transformations)
            simplified = sp.simplify(parsed)
            results.append({
                "equation": raw_eq,
                "valid_syntax": True,
                "simplified": str(simplified)
            })
        except Exception as e:
            results.append({
                "equation": raw_eq,
                "valid_syntax": False,
                "error": str(e)
            })
    return results

def check_asymptotic_flatness(metric_comp_str: str, radial_var_str: str = "r") -> dict:
    try:
        r = sp.Symbol(radial_var_str, positive=True, real=True)
        M = sp.Symbol("M", positive=True, real=True)
        cleaned = clean_latex_to_sympy(metric_comp_str)
        if "=" in cleaned:
            cleaned = cleaned.split("=")[-1].strip()
        expr = parse_expr(cleaned, transformations=transformations)
        lim_val = sp.limit(expr, r, sp.oo)
        return {
            "status": "PASSED" if lim_val != sp.nan else "FAILED",
            "limit_r_oo": str(lim_val),
            "message": f"lim r->oo evaluates to {lim_val}"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e)
        }
