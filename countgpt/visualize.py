"""Token visualization functions for CountGPT."""
import random
import sys
from typing import List, Optional

# ANSI color codes for text background colors (bright versions)
BG_COLORS = [
    "\033[48;5;{}m".format(color) for color in 
    [153, 184, 214, 209, 183, 157, 156, 147, 146, 218, 222, 229, 193, 157, 122]
]
RESET = "\033[0m"


def get_token_positions(text: str, tokens: List[bytes]) -> List[tuple]:
    """Get the start and end positions of each token in the original text.
    
    Args:
        text: The original text
        tokens: List of token bytes
        
    Returns:
        List of (start, end, token) tuples
    """
    positions = []
    offset = 0
    
    for token in tokens:
        token_str = token.decode('utf-8', errors='replace')
        # Find the token in the text starting from the current offset
        try:
            start = text.index(token_str, offset)
            end = start + len(token_str)
            positions.append((start, end, token_str))
            offset = end
        except ValueError:
            # Token not found (might be because of tokenization oddities)
            # Just append it at the end for display purposes
            positions.append((offset, offset + len(token_str), token_str))
            offset += len(token_str)
    
    return positions


def visualize_tokens(text: str, tokens: List[bytes], output=sys.stdout) -> None:
    """Visualize tokens by coloring each token with a different background color.
    
    Args:
        text: The original text
        tokens: List of token bytes
        output: Output stream (default: stdout)
    """
    # If there are no tokens, just print the text
    if not tokens:
        print(text)
        return
    
    # Convert tokens to strings and get their positions
    token_positions = get_token_positions(text, tokens)
    
    # Generate colored text
    colored_text = ""
    last_end = 0
    
    for i, (start, end, token_str) in enumerate(token_positions):
        # If there's a gap between the last token and this one, add the text as-is
        if start > last_end:
            colored_text += text[last_end:start]
        
        # Add the colored token
        color = BG_COLORS[i % len(BG_COLORS)]
        colored_text += f"{color}{token_str}{RESET}"
        last_end = end
    
    # Add any remaining text
    if last_end < len(text):
        colored_text += text[last_end:]
    
    # Print the header
    print(f"Tokens: {len(tokens)}        Characters: {len(text)}\n", file=output)
    
    # Print the colored text
    print(colored_text, file=output)
    print("\n", file=output)


def colorize_file(file_path: str, encoding, output=sys.stdout) -> None:
    """Colorize tokens in a file.
    
    Args:
        file_path: Path to the file
        encoding: Tiktoken encoding to use
        output: Output stream (default: stdout)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    tokens = encoding.encode(text)
    visualize_tokens(text, [encoding.decode_single_token_bytes(token) for token in tokens], output)