"""Token visualization functions for CountGPT."""
import random
import sys
from typing import List, Optional, Tuple, TextIO

# ANSI color codes for text background colors (bright versions)
BG_COLORS = [
    "\033[48;5;{}m".format(color) for color in 
    [153, 184, 214, 209, 183, 157, 156, 147, 146, 218, 222, 229, 193, 157, 122]
]
RESET = "\033[0m"


def get_token_positions(text: str, tokens: List[bytes]) -> List[Tuple[int, int, str]]:
    """Get the start and end positions of each token in the original text.
    
    Args:
        text: The original text
        tokens: List of token bytes
        
    Returns:
        List of (start, end, token) tuples
        
    Raises:
        ValueError: If token positions cannot be accurately determined
        UnicodeDecodeError: If token bytes cannot be decoded properly
    """
    positions: List[Tuple[int, int, str]] = []
    offset: int = 0
    error_count: int = 0
    max_errors: int = 5  # Maximum number of token positioning errors before raising warning
    
    for token in tokens:
        try:
            token_str: str = token.decode('utf-8', errors='replace')
            # Find the token in the text starting from the current offset
            try:
                start: int = text.index(token_str, offset)
                end: int = start + len(token_str)
                positions.append((start, end, token_str))
                offset = end
            except ValueError:
                # Token not found (might be because of tokenization oddities)
                # Just append it at the end for display purposes
                positions.append((offset, offset + len(token_str), token_str))
                offset += len(token_str)
                error_count += 1
                
                # Warn if we hit too many token positioning errors
                if error_count == max_errors:
                    print("Warning: Multiple token positioning errors encountered. Visualization may be inaccurate.", 
                          file=sys.stderr)
        except UnicodeDecodeError as e:
            # Handle token decoding errors gracefully
            positions.append((offset, offset + 1, "�"))
            offset += 1
            print(f"Warning: Failed to decode token: {str(e)}", file=sys.stderr)
    
    return positions


def visualize_tokens(text: str, tokens: List[bytes], output: Optional[TextIO]=sys.stdout) -> None:
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
    token_positions: List[Tuple[int, int, str]] = get_token_positions(text, tokens)
    
    # Generate colored text
    colored_text: str = ""
    last_end: int = 0
    
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


def colorize_file(file_path: str, encoding: 'tiktoken.Encoding', output: Optional[TextIO]=sys.stdout) -> None:
    """Colorize tokens in a file.
    
    Args:
        file_path: Path to the file
        encoding: Tiktoken encoding to use
        output: Output stream (default: stdout)
        
    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read due to permissions
        UnicodeDecodeError: If the file contains invalid UTF-8
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text: str = f.read()
        
        tokens: List[int] = encoding.encode(text)
        token_bytes: List[bytes] = [encoding.decode_single_token_bytes(token) for token in tokens]
        visualize_tokens(text, token_bytes, output)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
    except PermissionError:
        print(f"Error: Permission denied when reading {file_path}", file=sys.stderr)
    except UnicodeDecodeError:
        print(f"Error: Cannot decode file {file_path}. Please ensure it contains valid UTF-8", file=sys.stderr)
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}", file=sys.stderr)