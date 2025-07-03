#!/usr/bin/env python3
"""
Soorj (Սուրճ) - Armenian Programming Language
A simple interpreter for an Armenian programming language
"""

import sys
import os
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter


def run_file(filename: str) -> None:
    """Run a Soorj file"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            source = file.read()
        run_source(source)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def run_source(source: str) -> None:
    """Run Soorj source code"""
    try:
        # Tokenize
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Interpret
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
    except Exception as e:
        print(f"Error: {e}")


def print_help():
    """Print help information"""
    print("""
Սուրճ (Soorj) - Armenian Programming Language REPL
================================================

Commands:
  .help     - Show this help message
  .exit     - Exit the REPL
  .clear    - Clear the screen
  .example  - Show example code

Armenian Keywords:
  եթե        - if
  հպ         - else
  մինչև      - while
  գործ       - function
  տուր       - return
  այո        - true
  ոչ         - false
  հեչ        - null
  և          - and
  կամ        - or
  չի         - not

Built-in Functions:
  գրէ(...)   - Print values (write)
  թիվ(x)     - Convert to number
  բառ(x)     - Convert to string (word)

Example: ա = 5; գրէ("Բարեւ աշխարգ!")
""")


def print_example():
    """Print example code"""
    print("""
Example Soorj Programs:
=======================

1. Hello World:
   գրէ("Բարեւ աշխարգ!")

2. Variables and arithmetic:
   ա = 10
   բ = 20
   գումար = ա + բ
   գրէ("Գումարը:", գումար)

3. Conditional (if-else):
   ա = 15
   եթե ա > 10 {
       գրէ("Ա-ն մեծ է 10-ից")
   } հպ {
       գրէ("Ա-ն փոքր է կամ հավասար 10-ին")
   }

4. Loop (while):
   ի = 1
   մինչև ի <= 5 {
       գրէ("Հաշվարկ:", ի)
       ի = ի + 1
   }

5. Function definition:
   գործ ողջունել(անուն) {
       գրէ("Բարեւ,", անուն, "!")
       տուր "Ողջունեցի " + անուն
   }
   
   արդյունք = ողջունել("Հայաստան")
   գրէ("Գործառույթը վերադարձրեց:", արդյունք)
""")


def repl():
    """Start the REPL"""
    interpreter = Interpreter()
    
    print("Սուրճ (Soorj) Armenian Programming Language")
    print("Type .help for help, .exit to quit")
    print("=========================================")
    
    while True:
        try:
            source = input("soorj> ")
            
            # Handle REPL commands
            if source.strip() == ".exit":
                print("Ցտեսություն! (Goodbye!)")
                break
            elif source.strip() == ".help":
                print_help()
                continue
            elif source.strip() == ".clear":
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
            elif source.strip() == ".example":
                print_example()
                continue
            elif source.strip() == "":
                continue
            
            # Execute the source code
            try:
                # Tokenize
                lexer = Lexer(source)
                tokens = lexer.tokenize()
                
                # Parse
                parser = Parser(tokens)
                ast = parser.parse()
                
                # Interpret
                for statement in ast.statements:
                    result = interpreter.execute(statement)
                    # Print result for single expressions (like a calculator)
                    if (result is not None and 
                        hasattr(statement, 'expression') and
                        len(ast.statements) == 1):
                        print(result)
                
            except KeyboardInterrupt:
                print("\nInterrupted")
                continue
            except Exception as e:
                print(f"Error: {e}")
                continue
                
        except KeyboardInterrupt:
            print("\nցտեսություն! (Goodbye!)")
            break
        except EOFError:
            print("\nցտեսություն! (Goodbye!)")
            break


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Run file
        filename = sys.argv[1]
        run_file(filename)
    else:
        # Start REPL
        repl()


if __name__ == "__main__":
    main() 