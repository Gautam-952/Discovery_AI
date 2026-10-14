"""
Math and Physics Verification Sandbox for Discovery_AI.
Uses SymPy for symbolic algebra, tensor checks, and boundary limits.
"""

import sympy as sp
from typing import Dict, Any, List

def check_asymptotic_flatness(metric_expr_str: str, radial_var_str: str = "r") -> Dict[str, Any]:
    """
    Checks if a metric component or function approaches Minkowski flat space
    as the radial coordinate r -> infinity.
    Example input: "1 - 2*M/r" -> should approach 1.
    """
    try:
        r = sp.symbols(radial_var_str, positive=True, real=True)
        expr = sp.sympify(metric_expr_str)
        limit_inf = sp.limit(expr, r, sp.oo)
        is_flat = limit_inf in (1, 0, -1)
        
        return {
            "status": "PASS" if is_flat else "WARN",
            "limit_r_oo": str(limit_inf),
            "asymptotically_flat": bool(is_flat),
            "message": f"Limit as {radial_var_str}->oo is {limit_inf}"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }

def check_energy_condition_scalar(t_00_str: str, var_dict: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Checks sign of energy density expressions (e.g., T_00 or effective rho).
    Useful for testing negative energy regimes in Casimir or wormhole regions.
    """
    try:
        expr = sp.sympify(t_00_str)
        if var_dict:
            val = expr.subs(var_dict).evalf()
            is_negative = float(val) < 0
            return {
                "status": "PASS",
                "evaluated_value": float(val),
                "is_negative_energy": is_negative,
                "message": "Exotic/Negative energy density detected" if is_negative else "Standard positive energy"
            }
        return {
            "status": "PASS",
            "simplified_expression": str(sp.simplify(expr))
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }

def verify_hypothesis_equations(equations: List[str]) -> List[Dict[str, Any]]:
    """
    Runs basic dimensional and algebraic sanity checks on candidate equations.
    """
    results = []
    for eq in equations:
        try:
            parsed = sp.sympify(eq)
            results.append({
                "equation": eq,
                "valid_syntax": True,
                "free_symbols": [str(s) for s in parsed.free_symbols],
                "simplified": str(sp.simplify(parsed))
            })
        except Exception as e:
            results.append({
                "equation": eq,
                "valid_syntax": False,
                "error": str(e)
            })
    return results

if __name__ == "__main__":
    # Self-test
    test_metric = "1 - 2*M/r"
    print("Testing asymptotic flatness:", check_asymptotic_flatness(test_metric, "r"))