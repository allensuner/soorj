from typing import Any, Dict, List, Optional, Callable
from parser import (
    ASTNode, NumberLiteral, StringLiteral, BooleanLiteral, NullLiteral,
    Identifier, BinaryOp, UnaryOp, Assignment, FunctionCall,
    ExpressionStatement, IfStatement, WhileStatement, ReturnStatement,
    FunctionDeclaration, Program
)


class SoorjValue:
    """Represents a value in the Soorj language"""
    def __init__(self, value: Any, type_name: str):
        self.value = value
        self.type_name = type_name
    
    def __str__(self):
        if self.type_name == "null":
            return "հեչ"  # nothing
        elif self.type_name == "boolean":
            return "այո" if self.value else "ոչ"  # yes/no
        elif self.type_name == "string":
            return self.value  # Don't add quotes for output
        else:
            return str(self.value)
    
    def is_truthy(self) -> bool:
        """Determine if a value is truthy in Soorj"""
        if self.type_name == "null":
            return False
        elif self.type_name == "boolean":
            return self.value
        elif self.type_name == "number":
            return self.value != 0
        elif self.type_name == "string":
            return len(self.value) > 0
        return True


class ReturnValue(Exception):
    """Exception used to handle return statements"""
    def __init__(self, value: SoorjValue):
        self.value = value


class SoorjFunction:
    """Represents a user-defined function"""
    def __init__(self, name: str, parameters: List[str], body: List[ASTNode]):
        self.name = name
        self.parameters = parameters
        self.body = body
    
    def call(self, interpreter: 'Interpreter', arguments: List[SoorjValue]) -> SoorjValue:
        if len(arguments) != len(self.parameters):
            raise RuntimeError(f"Function {self.name} expects {len(self.parameters)} arguments, got {len(arguments)}")
        
        # Create new environment for function execution
        prev_env = interpreter.environment
        interpreter.environment = Environment(prev_env)
        
        # Bind parameters to arguments
        for param, arg in zip(self.parameters, arguments):
            interpreter.environment.define(param, arg)
        
        try:
            # Execute function body
            for stmt in self.body:
                interpreter.execute(stmt)
            
            # If no return statement, return null
            return SoorjValue(None, "null")
        
        except ReturnValue as ret:
            return ret.value
        
        finally:
            # Restore previous environment
            interpreter.environment = prev_env


class BuiltinFunction:
    """Represents a built-in function"""
    def __init__(self, name: str, func: Callable):
        self.name = name
        self.func = func
    
    def call(self, interpreter: 'Interpreter', arguments: List[SoorjValue]) -> SoorjValue:
        return self.func(arguments)


class Environment:
    """Environment for variable and function storage"""
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, SoorjValue] = {}
    
    def define(self, name: str, value: SoorjValue):
        self.variables[name] = value
    
    def get(self, name: str) -> SoorjValue:
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise RuntimeError(f"Undefined variable '{name}'")
    
    def assign(self, name: str, value: SoorjValue):
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise RuntimeError(f"Undefined variable '{name}'")


class Interpreter:
    def __init__(self):
        self.environment = Environment()
        self.setup_builtins()
    
    def setup_builtins(self):
        """Set up built-in functions"""
        def builtin_gre(args: List[SoorjValue]) -> SoorjValue:
            """գրէ (write/print) - Print values to console"""
            if len(args) == 0:
                print()
            else:
                output = " ".join(str(arg) for arg in args)
                print(output)
            return SoorjValue(None, "null")
        
        def builtin_tiv(args: List[SoorjValue]) -> SoorjValue:
            """թիվ (number) - converts to number"""
            if len(args) != 1:
                raise RuntimeError("թիվ expects exactly 1 argument")
            
            arg = args[0]
            if arg.type_name == "number":
                return arg
            elif arg.type_name == "string":
                try:
                    return SoorjValue(float(arg.value), "number")
                except ValueError:
                    return SoorjValue(0, "number")
            elif arg.type_name == "boolean":
                return SoorjValue(1 if arg.value else 0, "number")
            else:
                return SoorjValue(0, "number")
        
        def builtin_bar(args: List[SoorjValue]) -> SoorjValue:
            """բառ (word/string) - converts to string"""
            if len(args) != 1:
                raise RuntimeError("բառ expects exactly 1 argument")
            
            arg = args[0]
            if arg.type_name == "string":
                return arg
            elif arg.type_name == "null":
                return SoorjValue("", "string")
            else:
                return SoorjValue(str(arg.value), "string")
        
        # Define built-in functions with Armenian names
        self.environment.define("գրէ", 
                               SoorjValue(BuiltinFunction("գրէ", builtin_gre), "function"))
        self.environment.define("թիվ", 
                               SoorjValue(BuiltinFunction("թիվ", builtin_tiv), "function"))
        self.environment.define("բառ", 
                               SoorjValue(BuiltinFunction("բառ", builtin_bar), "function"))
    
    def interpret(self, program: Program) -> None:
        """Interpret a program"""
        try:
            for statement in program.statements:
                self.execute(statement)
        except RuntimeError as e:
            print(f"Runtime error: {e}")
    
    def execute(self, node: ASTNode) -> Optional[SoorjValue]:
        """Execute an AST node"""
        if isinstance(node, Program):
            for stmt in node.statements:
                self.execute(stmt)
            return None
        
        elif isinstance(node, ExpressionStatement):
            return self.evaluate(node.expression)
        
        elif isinstance(node, IfStatement):
            condition = self.evaluate(node.condition)
            if condition.is_truthy():
                for stmt in node.then_branch:
                    self.execute(stmt)
            elif node.else_branch:
                for stmt in node.else_branch:
                    self.execute(stmt)
            return None
        
        elif isinstance(node, WhileStatement):
            while True:
                condition = self.evaluate(node.condition)
                if not condition.is_truthy():
                    break
                for stmt in node.body:
                    self.execute(stmt)
            return None
        
        elif isinstance(node, ReturnStatement):
            value = SoorjValue(None, "null")
            if node.value:
                value = self.evaluate(node.value)
            raise ReturnValue(value)
        
        elif isinstance(node, FunctionDeclaration):
            func = SoorjFunction(node.name, node.parameters, node.body)
            self.environment.define(node.name, SoorjValue(func, "function"))
            return None
        
        else:
            return self.evaluate(node)
    
    def evaluate(self, node: ASTNode) -> SoorjValue:
        """Evaluate an expression node"""
        if isinstance(node, NumberLiteral):
            return SoorjValue(node.value, "number")
        
        elif isinstance(node, StringLiteral):
            return SoorjValue(node.value, "string")
        
        elif isinstance(node, BooleanLiteral):
            return SoorjValue(node.value, "boolean")
        
        elif isinstance(node, NullLiteral):
            return SoorjValue(None, "null")
        
        elif isinstance(node, Identifier):
            return self.environment.get(node.name)
        
        elif isinstance(node, Assignment):
            value = self.evaluate(node.value)
            try:
                self.environment.assign(node.target, value)
            except RuntimeError:
                # If variable doesn't exist, define it
                self.environment.define(node.target, value)
            return value
        
        elif isinstance(node, BinaryOp):
            return self.evaluate_binary_op(node)
        
        elif isinstance(node, UnaryOp):
            return self.evaluate_unary_op(node)
        
        elif isinstance(node, FunctionCall):
            return self.evaluate_function_call(node)
        
        else:
            raise RuntimeError(f"Unknown node type: {type(node)}")
    
    def evaluate_binary_op(self, node: BinaryOp) -> SoorjValue:
        """Evaluate binary operations"""
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        
        if node.operator == "+":
            if left.type_name == "number" and right.type_name == "number":
                return SoorjValue(left.value + right.value, "number")
            elif left.type_name == "string" or right.type_name == "string":
                return SoorjValue(str(left.value) + str(right.value), "string")
            else:
                raise RuntimeError("Invalid operands for +")
        
        elif node.operator == "-":
            if left.type_name == "number" and right.type_name == "number":
                return SoorjValue(left.value - right.value, "number")
            else:
                raise RuntimeError("Invalid operands for -")
        
        elif node.operator == "*":
            if left.type_name == "number" and right.type_name == "number":
                return SoorjValue(left.value * right.value, "number")
            else:
                raise RuntimeError("Invalid operands for *")
        
        elif node.operator == "/":
            if left.type_name == "number" and right.type_name == "number":
                if right.value == 0:
                    raise RuntimeError("Division by zero")
                return SoorjValue(left.value / right.value, "number")
            else:
                raise RuntimeError("Invalid operands for /")
        
        elif node.operator == "%":
            if left.type_name == "number" and right.type_name == "number":
                return SoorjValue(left.value % right.value, "number")
            else:
                raise RuntimeError("Invalid operands for %")
        
        elif node.operator == "==":
            return SoorjValue(left.value == right.value, "boolean")
        
        elif node.operator == "!=":
            return SoorjValue(left.value != right.value, "boolean")
        
        elif node.operator == "<":
            if left.type_name == "number" and right.type_name == "number":
                return SoorjValue(left.value < right.value, "boolean")
            else:
                raise RuntimeError("Invalid operands for <")
        
        elif node.operator == ">":
            if left.type_name == "number" and right.type_name == "number":
                return SoorjValue(left.value > right.value, "boolean")
            else:
                raise RuntimeError("Invalid operands for >")
        
        elif node.operator == "<=":
            if left.type_name == "number" and right.type_name == "number":
                return SoorjValue(left.value <= right.value, "boolean")
            else:
                raise RuntimeError("Invalid operands for <=")
        
        elif node.operator == ">=":
            if left.type_name == "number" and right.type_name == "number":
                return SoorjValue(left.value >= right.value, "boolean")
            else:
                raise RuntimeError("Invalid operands for >=")
        
        elif node.operator in ["և"]:  # և (and)
            return SoorjValue(left.is_truthy() and right.is_truthy(), "boolean")
        
        elif node.operator in ["կամ"]:  # կամ (or)
            return SoorjValue(left.is_truthy() or right.is_truthy(), "boolean")
        
        else:
            raise RuntimeError(f"Unknown binary operator: {node.operator}")
    
    def evaluate_unary_op(self, node: UnaryOp) -> SoorjValue:
        """Evaluate unary operations"""
        operand = self.evaluate(node.operand)
        
        if node.operator == "-":
            if operand.type_name == "number":
                return SoorjValue(-operand.value, "number")
            else:
                raise RuntimeError("Invalid operand for unary -")
        
        elif node.operator in ["չի", "not"]:  # չի (not)
            return SoorjValue(not operand.is_truthy(), "boolean")
        
        else:
            raise RuntimeError(f"Unknown unary operator: {node.operator}")
    
    def evaluate_function_call(self, node: FunctionCall) -> SoorjValue:
        """Evaluate function calls"""
        function_value = self.environment.get(node.name)
        
        if function_value.type_name != "function":
            raise RuntimeError(f"'{node.name}' is not a function")
        
        # Evaluate arguments
        args = [self.evaluate(arg) for arg in node.arguments]
        
        # Call the function
        func = function_value.value
        return func.call(self, args) 