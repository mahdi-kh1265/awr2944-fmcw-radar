"""Configuration parser for AR1 function calls.

Provides safe parsing without using eval() to extract function names and arguments.
"""

from typing import Any


class AR1ParseError(ValueError):
    """Raised when an AR1 command string is malformed or contains invalid arguments."""
    pass


def _parse_arg(arg_str: str) -> int | float:
    """Safely parse a single argument string into int or float.
    
    Supports:
    - Decimal integers (e.g. '42', '-5')
    - Hex integers (e.g. '0x0', '0xFF')
    - Floats (e.g. '29.982', '-1.5')
    """
    s = arg_str.strip()
    if not s:
        raise AR1ParseError("Empty argument found")
        
    # Check for hex
    if s.lower().startswith("0x"):
        try:
            return int(s, 16)
        except ValueError:
            raise AR1ParseError(f"Invalid hex integer format: '{s}'")
            
    # Try integer
    try:
        return int(s)
    except ValueError:
        pass
        
    # Try float
    try:
        return float(s)
    except ValueError:
        raise AR1ParseError(f"Invalid numeric format: '{s}'")


def parse_ar1_call(raw_cmd: str) -> dict[str, Any]:
    """Parse a simple ar1 function call string into its name and arguments.
    
    Example: 'ar1.ProfileConfig(0, 77.0, 256)'
    Returns:
    {
        "name": "ProfileConfig",
        "args": [0, 77.0, 256],
        "arg_count": 3,
        "raw": "ar1.ProfileConfig(0, 77.0, 256)"
    }
    
    This parser is safe and does not use eval(). It only supports numeric arguments
    (ints, hex ints, floats).
    """
    s = raw_cmd.strip()
    
    if not s.endswith(")"):
        raise AR1ParseError(f"Command does not end with ')': {raw_cmd}")
        
    try:
        paren_idx = s.index("(")
    except ValueError:
        raise AR1ParseError(f"No '(' found in command: {raw_cmd}")
        
    func_part = s[:paren_idx].strip()
    if func_part.startswith("ar1."):
        func_name = func_part[4:]
    else:
        func_name = func_part
        
    if not func_name:
        raise AR1ParseError(f"Empty function name in command: {raw_cmd}")
        
    args_part = s[paren_idx + 1:-1].strip()
    
    parsed_args = []
    if args_part:
        raw_args = args_part.split(",")
        for ra in raw_args:
            parsed_args.append(_parse_arg(ra))
            
    return {
        "name": func_name,
        "args": parsed_args,
        "arg_count": len(parsed_args),
        "raw": raw_cmd
    }
