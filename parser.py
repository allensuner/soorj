from typing import List, Optional
from lexer import Token, TokenType
from dataclasses import dataclass
from abc import ABC


# AST Node base class
class ASTNode(ABC):
    pass


# Expression nodes
@dataclass
class NumberLiteral(ASTNode):
    value: float


@dataclass
class StringLiteral(ASTNode):
    value: str


@dataclass
class BooleanLiteral(ASTNode):
    value: bool


@dataclass
class NullLiteral(ASTNode):
    pass


@dataclass
class Identifier(ASTNode):
    name: str


@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode


@dataclass
class Assignment(ASTNode):
    target: str
    value: ASTNode


@dataclass
class FunctionCall(ASTNode):
    name: str
    arguments: List[ASTNode]


# Statement nodes
@dataclass
class ExpressionStatement(ASTNode):
    expression: ASTNode


@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_branch: List[ASTNode]
    else_branch: Optional[List[ASTNode]] = None


@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: List[ASTNode]


@dataclass
class ReturnStatement(ASTNode):
    value: Optional[ASTNode] = None


@dataclass
class FunctionDeclaration(ASTNode):
    name: str
    parameters: List[str]
    body: List[ASTNode]


@dataclass
class Program(ASTNode):
    statements: List[ASTNode]


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF
    
    def peek(self) -> Token:
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        
        current_token = self.peek()
        raise SyntaxError(
            f"{message}. Got {current_token.type} at line {current_token.line}"
        )
    
    def skip_newlines(self):
        while self.match(TokenType.NEWLINE):
            pass
    
    def parse(self) -> Program:
        statements = []
        
        while not self.is_at_end():
            self.skip_newlines()
            if not self.is_at_end():
                stmt = self.statement()
                if stmt:
                    statements.append(stmt)
        
        return Program(statements)
    
    def statement(self) -> Optional[ASTNode]:
        self.skip_newlines()
        
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.FUNCTION):
            return self.function_declaration()
        
        # Check if we're at a token that can't start a statement
        if self.check(TokenType.RIGHT_BRACE) or self.check(TokenType.EOF):
            return None
        
        return self.expression_statement()
    
    def if_statement(self) -> IfStatement:
        condition = self.expression()
        self.skip_newlines()
        
        # Expect opening brace
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after if condition")
        self.skip_newlines()
        
        then_branch = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmt = self.statement()
            if stmt:
                then_branch.append(stmt)
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after if body")
        
        else_branch = None
        if self.match(TokenType.ELSE):
            self.skip_newlines()
            self.consume(TokenType.LEFT_BRACE, "Expected '{' after else")
            self.skip_newlines()
            
            else_branch = []
            while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
                stmt = self.statement()
                if stmt:
                    else_branch.append(stmt)
            
            self.consume(TokenType.RIGHT_BRACE, "Expected '}' after else body")
        
        return IfStatement(condition, then_branch, else_branch)
    
    def while_statement(self) -> WhileStatement:
        condition = self.expression()
        self.skip_newlines()
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after while condition")
        self.skip_newlines()
        
        body = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmt = self.statement()
            if stmt:
                body.append(stmt)
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after while body")
        return WhileStatement(condition, body)
    
    def return_statement(self) -> ReturnStatement:
        value = None
        if (not self.check(TokenType.NEWLINE) and 
                not self.is_at_end()):
            value = self.expression()
        
        return ReturnStatement(value)
    
    def function_declaration(self) -> FunctionDeclaration:
        name = self.consume(TokenType.IDENTIFIER, 
                            "Expected function name").value
        
        self.consume(TokenType.LEFT_PAREN, 
                     "Expected '(' after function name")
        
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            param_name = self.consume(TokenType.IDENTIFIER, 
                                      "Expected parameter name").value
            parameters.append(param_name)
            while self.match(TokenType.COMMA):
                param_name = self.consume(TokenType.IDENTIFIER, 
                                          "Expected parameter name").value
                parameters.append(param_name)
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        self.skip_newlines()
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' before function body")
        self.skip_newlines()
        
        body = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmt = self.statement()
            if stmt:
                body.append(stmt)
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after function body")
        return FunctionDeclaration(name, parameters, body)
    
    def expression_statement(self) -> ExpressionStatement:
        expr = self.expression()
        return ExpressionStatement(expr)
    
    def expression(self) -> ASTNode:
        return self.assignment()
    
    def assignment(self) -> ASTNode:
        expr = self.logical_or()
        
        if self.match(TokenType.ASSIGN):
            value = self.assignment()
            if isinstance(expr, Identifier):
                return Assignment(expr.name, value)
            
            raise SyntaxError("Invalid assignment target")
        
        return expr
    
    def logical_or(self) -> ASTNode:
        expr = self.logical_and()
        
        while self.match(TokenType.OR):
            operator = self.previous().value
            right = self.logical_and()
            expr = BinaryOp(expr, operator, right)
        
        return expr
    
    def logical_and(self) -> ASTNode:
        expr = self.equality()
        
        while self.match(TokenType.AND):
            operator = self.previous().value
            right = self.equality()
            expr = BinaryOp(expr, operator, right)
        
        return expr
    
    def equality(self) -> ASTNode:
        expr = self.comparison()
        
        while self.match(TokenType.EQUALS, TokenType.NOT_EQUALS):
            operator = self.previous().value
            right = self.comparison()
            expr = BinaryOp(expr, operator, right)
        
        return expr
    
    def comparison(self) -> ASTNode:
        expr = self.term()
        
        while self.match(TokenType.GREATER_THAN, TokenType.GREATER_EQUAL, 
                         TokenType.LESS_THAN, TokenType.LESS_EQUAL):
            operator = self.previous().value
            right = self.term()
            expr = BinaryOp(expr, operator, right)
        
        return expr
    
    def term(self) -> ASTNode:
        expr = self.factor()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous().value
            right = self.factor()
            expr = BinaryOp(expr, operator, right)
        
        return expr
    
    def factor(self) -> ASTNode:
        expr = self.unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.previous().value
            right = self.unary()
            expr = BinaryOp(expr, operator, right)
        
        return expr
    
    def unary(self) -> ASTNode:
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator = self.previous().value
            right = self.unary()
            return UnaryOp(operator, right)
        
        return self.call()
    
    def call(self) -> ASTNode:
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break
        
        return expr
    
    def finish_call(self, callee: ASTNode) -> FunctionCall:
        arguments = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                arguments.append(self.expression())
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
        
        if isinstance(callee, Identifier):
            return FunctionCall(callee.name, arguments)
        
        raise SyntaxError("Invalid function call")
    
    def primary(self) -> ASTNode:
        if self.match(TokenType.TRUE):
            return BooleanLiteral(True)
        
        if self.match(TokenType.FALSE):
            return BooleanLiteral(False)
        
        if self.match(TokenType.NULL):
            return NullLiteral()
        
        if self.match(TokenType.NUMBER):
            return NumberLiteral(float(self.previous().value))
        
        if self.match(TokenType.STRING):
            return StringLiteral(self.previous().value)
        
        if self.match(TokenType.IDENTIFIER):
            return Identifier(self.previous().value)
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr
        
        current_token = self.peek()
        raise SyntaxError(f"Unexpected token {current_token.type} at line {current_token.line}") 