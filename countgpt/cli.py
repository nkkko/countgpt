"""Command line interface for counting tokens in text files."""
import sys
import click
import tiktoken
from pathlib import Path
from typing import List, Dict, Union, Optional, TextIO
from .models import (
    count_tokens, 
    count_tokens_in_file, 
    get_available_models, 
    get_supported_llm_models,
    get_encoding_for_model
)
from .visualize import colorize_file, visualize_tokens


@click.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True, readable=True), required=False)
@click.option('--model', '-m', default='cl100k_base', 
              help='Tokenizer model or LLM model name. Default: cl100k_base')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information')
@click.option('--list-models', '-l', is_flag=True, help='List all supported models and exit')
@click.option('--visualize', '-c', is_flag=True, help='Visualize tokens with colorful output')
def main(files, model, verbose, list_models, visualize) -> None:
    """Count tokens in text files or from standard input.
    
    You can specify either a tiktoken encoding model (like cl100k_base) or an
    actual LLM model name (like gpt-4, gpt-3.5-turbo) to count tokens.
    
    EXAMPLES:
        countgpt file.txt
        countgpt file1.txt file2.md
        countgpt --model gpt-4 file.txt
        cat file.txt | countgpt
        echo "Hello world" | countgpt
    """
    if list_models:
        # Display tokenizer models
        click.echo("Available tokenizer models:")
        for enc_model in sorted(get_available_models()):
            click.echo(f"  {enc_model}")
        
        # Get all models and sort them
        all_models = get_supported_llm_models()
        
        # Display Anthropic models
        click.echo("\nAnthropic Models:")
        anthropic_models = [m for m in all_models if m.startswith(("claude", "o1", "o3")) or m in ["opus", "sonnet", "haiku"]]
        for llm_model in sorted(anthropic_models):
            encoding = get_encoding_for_model(llm_model)
            click.echo(f"  {llm_model} (uses {encoding})")
        
        # Display OpenAI models
        click.echo("\nOpenAI Models:")
        openai_models = [m for m in all_models if m.startswith(("gpt", "text-", "davinci", "babbage", "curie", "ada", "4", "3.5")) and m not in ["gpt2", "gpt-2"]]
        for llm_model in sorted(openai_models):
            encoding = get_encoding_for_model(llm_model)
            click.echo(f"  {llm_model} (uses {encoding})")
        
        # Display shorthands
        click.echo("\nShorthands:")
        shorthand_models = ["4o", "4", "3.5", "opus", "sonnet", "haiku", "chatgpt", "claude"]
        for llm_model in shorthand_models:
            if llm_model in all_models:
                encoding = get_encoding_for_model(llm_model)
                click.echo(f"  {llm_model} (uses {encoding})")
        
        # Display other models
        other_models = [m for m in all_models if m not in anthropic_models and m not in openai_models and m not in shorthand_models]
        if other_models:
            click.echo("\nOther Models:")
            for llm_model in sorted(other_models):
                encoding = get_encoding_for_model(llm_model)
                click.echo(f"  {llm_model} (uses {encoding})")
        
        return
    
    # Get the correct encoding based on model input (could be LLM name or encoding)
    try:
        encoding_name = get_encoding_for_model(model)
        encoding = tiktoken.get_encoding(encoding_name)
    except KeyError:
        click.echo(f"Error: Model '{model}' not found.", err=True)
        click.echo(f"Use --list-models to see available options.", err=True)
        sys.exit(1)
    
    # Check if we're getting data from pipe or files
    if not files and not sys.stdin.isatty():
        # Read from stdin (pipe)
        try:
            content: str = sys.stdin.read()
            tokens: List[int] = encoding.encode(content)
            token_count: int = len(tokens)
        except UnicodeDecodeError as e:
            click.echo(f"Error: Could not decode input. Please ensure it is valid UTF-8: {str(e)}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"Error processing stdin: {str(e)}", err=True)
            sys.exit(1)
        
        if visualize:
            # Show colorful visualization of tokens
            try:
                token_bytes: List[bytes] = [encoding.decode_single_token_bytes(token) for token in tokens]
                visualize_tokens(content, token_bytes)
            except Exception as e:
                click.echo(f"Error visualizing tokens: {str(e)}", err=True)
        elif verbose:
            click.echo(f"Stdin (piped input):")
            if model != encoding_name:
                click.echo(f"  Model: {model} (using {encoding_name} tokenizer)")
            else:
                click.echo(f"  Model: {model}")
            click.echo(f"  Token count: {token_count}")
            click.echo(f"  Character count: {len(content)}")
        else:
            click.echo(f"{token_count}")
    
    elif files:
        # Read from files
        total_tokens: int = 0
        
        for file_path in files:
            path = Path(file_path)
            try:
                content: str = path.read_text(encoding='utf-8')
                tokens: List[int] = encoding.encode(content)
                token_count: int = len(tokens)
                total_tokens += token_count
                
                if visualize:
                    # Show colorful visualization of tokens
                    click.echo(f"\n{path}:")
                    try:
                        token_bytes: List[bytes] = [encoding.decode_single_token_bytes(token) for token in tokens]
                        visualize_tokens(content, token_bytes)
                    except Exception as e:
                        click.echo(f"Error visualizing tokens: {str(e)}", err=True)
                elif verbose:
                    click.echo(f"{path}:")
                    if model != encoding_name:
                        click.echo(f"  Model: {model} (using {encoding_name} tokenizer)")
                    else:
                        click.echo(f"  Model: {model}")
                    click.echo(f"  Token count: {token_count}")
                    click.echo(f"  Character count: {len(content)}")
                else:
                    click.echo(f"{path}: {token_count}")
            except UnicodeDecodeError as e:
                click.echo(f"Error reading {path}: Could not decode file. Please ensure it is valid UTF-8: {str(e)}", err=True)
            except PermissionError as e:
                click.echo(f"Error reading {path}: Permission denied: {str(e)}", err=True)
            except Exception as e:
                click.echo(f"Error reading {path}: {str(e)}", err=True)
        
        if len(files) > 1 and not visualize:
            if verbose:
                click.echo(f"Total tokens across all files: {total_tokens}")
            else:
                click.echo(f"Total: {total_tokens}")
    
    else:
        # No files and no pipe, show help
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        
if __name__ == "__main__":
    main()