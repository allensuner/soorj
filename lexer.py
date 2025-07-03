from enum import Enum, auto
from typing import List, NamedTuple, Optional


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    
    # Armenian Keywords
    IF = auto()          # եթե
    ELSE = auto()        # հպ
    WHILE = auto()       # մինչև
    FUNCTION = auto()    # գործ
    RETURN = auto()      # տուր
    TRUE = auto()        # այո
    FALSE = auto()       # ոչ
    NULL = auto()        # հեչ
    AND = auto()         # և
    OR = auto()          # կամ
    NOT = auto()         # չի
    
    # Operators
    PLUS = auto()        # +
    MINUS = auto()       # -
    MULTIPLY = auto()    # *
    DIVIDE = auto()      # /
    MODULO = auto()      # %
    ASSIGN = auto()      # =
    EQUALS = auto()      # ==
    NOT_EQUALS = auto()  # !=
    LESS_THAN = auto()   # <
    GREATER_THAN = auto() # >
    LESS_EQUAL = auto()  # <=
    GREATER_EQUAL = auto() # >=
    
    # Delimiters
    LEFT_PAREN = auto()  # (
    RIGHT_PAREN = auto() # )
    LEFT_BRACE = auto()  # {
    RIGHT_BRACE = auto() # }
    COMMA = auto()       # ,
    
    # Special
    NEWLINE = auto()
    EOF = auto()


class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # Armenian keywords mapping
        self.keywords = {
            'եթե': TokenType.IF,        # if
            'հպ': TokenType.ELSE,       # else (short for հակառակ պարագային)
            'մինչև': TokenType.WHILE,   # while
            'գործ': TokenType.FUNCTION, # function (work)
            'տուր': TokenType.RETURN,   # return (give)
            'այո': TokenType.TRUE,      # true (yes)
            'ոչ': TokenType.FALSE,      # false (no)
            'հեչ': TokenType.NULL,      # null (nothing)
            'և': TokenType.AND,         # and
            'կամ': TokenType.OR,        # or
            'չի': TokenType.NOT,        # not
        }
        
        # Single character tokens
        self.single_chars = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            ',': TokenType.COMMA,
        }
        
        # Two character tokens
        self.two_chars = {
            '==': TokenType.EQUALS,
            '!=': TokenType.NOT_EQUALS,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
        }
    
    def current_char(self) -> Optional[str]:
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        peek_pos = self.position + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self):
        if self.position < len(self.source):
            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def is_armenian_char(self, char: str) -> bool:
        """Check if character is Armenian Unicode"""
        if not char:
            return False
        code_point = ord(char)
        # Armenian Unicode blocks:
        # U+0530-U+058F: Armenian
        # U+FB13-U+FB17: Armenian ligatures
        return (0x0530 <= code_point <= 0x058F) or (0xFB13 <= code_point <= 0xFB17)
    
    def is_identifier_char(self, char: str) -> bool:
        """Check if character can be part of an identifier - Armenian only"""
        if not char:
            return False
        return self.is_armenian_char(char)
    
    def is_valid_string_char(self, char: str) -> bool:
        """Check if character is valid in string literals"""
        if not char:
            return False
        # Allow Armenian characters, numbers, spaces, common punctuation
        return (self.is_armenian_char(char) or 
                char.isdigit() or 
                char in ' \t\n\r.,!?:;-()[]{}"\'/\\' or
                char in '՛՜՝՞՟։՚՛՜՝՞՟')  # Armenian punctuation
    
    def read_number(self) -> Token:
        start_column = self.column
        number_str = ""
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            number_str += self.current_char()
            self.advance()
        
        return Token(TokenType.NUMBER, number_str, self.line, start_column)
    
    def read_string(self) -> Token:
        start_column = self.column
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        
        string_value = ""
        while self.current_char() and self.current_char() != quote_char:
            char = self.current_char()
            if char == '\\':
                self.advance()
                next_char = self.current_char()
                if next_char == 'n':
                    string_value += '\n'
                elif next_char == 't':
                    string_value += '\t'
                elif next_char == 'r':
                    string_value += '\r'
                elif next_char == '\\':
                    string_value += '\\'
                elif next_char == quote_char:
                    string_value += quote_char
                elif next_char:
                    string_value += next_char
                self.advance()
            else:
                # Validate that character is allowed in strings
                if not self.is_valid_string_char(char):
                    raise ValueError(
                        f"Invalid character '{char}' in string at line {self.line}, "
                        f"column {self.column}. Only Armenian characters, numbers, "
                        f"and punctuation allowed."
                    )
                string_value += char
                self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # Skip closing quote
        
        return Token(TokenType.STRING, string_value, self.line, start_column)
    
    def read_identifier(self) -> Token:
        start_column = self.column
        identifier = ""
        
        while self.current_char() and self.is_identifier_char(self.current_char()):
            identifier += self.current_char()
            self.advance()
        
        # Check if it's a keyword
        token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
        return Token(token_type, identifier, self.line, start_column)
    
    def tokenize(self) -> List[Token]:
        while self.position < len(self.source):
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            char = self.current_char()
            
            # Handle newlines
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, char, self.line, self.column))
                self.advance()
                continue
            
            # Handle comments
            if char == '#':
                # Skip until end of line
                while self.current_char() and self.current_char() != '\n':
                    self.advance()
                continue
            
            # Handle numbers
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Handle strings
            if char in '"\'':
                self.tokens.append(self.read_string())
                continue
            
            # Handle identifiers and keywords (Armenian characters only)
            if self.is_armenian_char(char):
                self.tokens.append(self.read_identifier())
                continue
            
            # Handle two-character operators
            if char in '=!<>':
                next_char = self.peek_char()
                two_char = char + (next_char or '')
                if two_char in self.two_chars:
                    self.tokens.append(Token(self.two_chars[two_char], two_char, self.line, self.column))
                    self.advance()
                    self.advance()
                    continue
            
            # Handle single character tokens
            if char in self.single_chars:
                self.tokens.append(Token(self.single_chars[char], char, self.line, self.column))
                self.advance()
                continue
            
            # Handle assignment operator
            if char == '=':
                self.tokens.append(Token(TokenType.ASSIGN, char, self.line, self.column))
                self.advance()
                continue
            
            # Handle comparison operators
            if char == '<':
                self.tokens.append(Token(TokenType.LESS_THAN, char, self.line, self.column))
                self.advance()
                continue
            
            if char == '>':
                self.tokens.append(Token(TokenType.GREATER_THAN, char, self.line, self.column))
                self.advance()
                continue
            
            # If we get here, it's an unknown character
            raise ValueError(f"Unknown character '{char}' at line {self.line}, column {self.column}")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens 