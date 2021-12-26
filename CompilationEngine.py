"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

SYMBOLS = ["{", "}", "[", "]", "(", ")", ".", ",", ";", "+", "-", "*", "/",
           "&", "|", "<", ">", "=", "~"]

KEYWORDS = ["class", "method", "function", "constructor", "int", "boolean",
            "char", "void", "var", "static", "field", "let", "do", "if",
            "else", "while", "return", "true", "false", "null", "this"]


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: typing.TextIO,
                 output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        self.jack_tokenizer = JackTokenizer(input_stream)
        self.sym_tab = SymbolTable()
        self.vm_writer = VMWriter(output_stream)
        self.if_count = 0
        self.while_count = 0
        pass

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!

        self.jack_tokenizer.eat("***")  # class
        self.cl_name = self.jack_tokenizer.eat("***")  # class name
        self.jack_tokenizer.eat("***")  # {
        while self.jack_tokenizer.is_next_class_var_dec():
            self.compile_class_var_dec()
        while self.jack_tokenizer.is_next_class_sub_dec():
            self.compile_subroutine()
        self.jack_tokenizer.eat("***")  # }

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        kind = self.jack_tokenizer.eat("***")  # static|field
        type = self.jack_tokenizer.eat("***")  # type
        name = self.jack_tokenizer.eat("***")  # varName
        self.sym_tab.define(name, type, kind)
        check = self.jack_tokenizer.eat(",")
        while check != "":
            name = self.jack_tokenizer.eat("***")  # varName
            self.sym_tab.define(name, type, kind)
            check = self.jack_tokenizer.eat(",")
        self.jack_tokenizer.eat("***")  # ;

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        # Your code goes here!
        self.sym_tab.start_subroutine()
        typ_of_fun = self.jack_tokenizer.eat("***")  # (constructor|function|method)
        type = self.jack_tokenizer.eat("***")  # type|void
        name = self.jack_tokenizer.eat("***")  # subroutine name
        self.jack_tokenizer.eat("***")  # (
        parm_i = 0
        if typ_of_fun == "method":
            parm_i = 1
        parm_i += self.compile_parameter_list()
        self.vm_writer.write_function(self.cl_name + "." + name, parm_i)
        if typ_of_fun == "constructor":
            self.vm_writer.write_push("constant", parm_i)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)

        self.jack_tokenizer.eat("***")  # )

        self.jack_tokenizer.eat("***")  # {
        while self.jack_tokenizer.is_next_var_dec():
            self.compile_var_dec()
        self.compile_statements()
        self.jack_tokenizer.eat("***")  # }
        if type == "void":
            self.vm_writer.write_pop("temp", 0)

        pass

    def compile_parameter_list(self):
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        # Your code goes here!
        i = 0
        if not self.jack_tokenizer.is_next_is_par():
            type_1 = self.jack_tokenizer.eat("***")  # type
            name = self.jack_tokenizer.eat("***")  # varName
            self.sym_tab.define(name, type_1, "arg")
            i += 1
            check = self.jack_tokenizer.eat(",")
            while check != "":
                type_1 = self.jack_tokenizer.eat("***")  # type
                name = self.jack_tokenizer.eat("***")  # varName
                self.sym_tab.define(name, type_1, "arg")
                i += 1
                check = self.jack_tokenizer.eat(",")
        return i

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        kind = self.jack_tokenizer.eat("***")  # var
        type = self.jack_tokenizer.eat("***")  # type
        name = self.jack_tokenizer.eat("***")  # varName
        self.sym_tab.define(name, type, kind)
        check = self.jack_tokenizer.eat(",")
        while check != "":
            name = self.jack_tokenizer.eat("***")  # varName
            self.sym_tab.define(name, type, kind)
            check = self.jack_tokenizer.eat(",")
        self.jack_tokenizer.eat("***")  # ;

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        # Your code goes here!
        stam = self.jack_tokenizer.is_next_statment()

        while stam != "":
            if stam == "let":
                self.compile_let()
            elif stam == "if":
                self.compile_if()
            elif stam == "while":
                self.compile_while()
            elif stam == "do":
                self.compile_do()
            else:
                self.compile_return()
            stam = self.jack_tokenizer.is_next_statment()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        self.jack_tokenizer.eat("***")  # do

        name = self.jack_tokenizer.eat("***")  # (className|varName)
        i = 0
        if self.jack_tokenizer.is_next_dot():
            self.jack_tokenizer.eat("***")  # .
            sub_name = self.jack_tokenizer.eat("***")  # name
            if self.sym_tab.kind_of(name) is not None:
                self.vm_writer.write_push(self.sym_tab.kind_of(name), self.sym_tab.index_of(name))
                i = 1
                name = sub_name
            else:
                name = name + "." + sub_name
        self.jack_tokenizer.eat("***")  # (
        i += self.compile_expression_list()
        self.vm_writer.write_call(name, i)
        self.jack_tokenizer.eat("***")  # )
        self.jack_tokenizer.eat("***")  # ;
        self.vm_writer.write_pop("temp", 0)

    def compile_let(self) -> None:  # DONE
        """Compiles a let statement."""
        # Your code goes here!
        tempoo = False

        self.jack_tokenizer.eat("***")  # dispose of let
        curr_var = self.jack_tokenizer.eat("***")  # get the var name
        if self.sym_tab.kind_of(curr_var) == "field":
            if self.sym_tab.index_of("this") is not None:  # we are in a consructor
                self.vm_writer.write_push("argument", 0)
                self.vm_writer.write_pop("pointer", 0)
            sagment = "this"
        else:
            sagment = self.sym_tab.kind_of(curr_var)
        if self.jack_tokenizer.is_next_is_bracket():
            self.vm_writer.write_push(sagment, self.sym_tab.index_of(curr_var))
            self.jack_tokenizer.eat("***")  # dispose of  [
            self.compile_expression()
            self.jack_tokenizer.eat("***")  # dispose of  ]
            self.vm_writer.write_arithmetic("add")
            tempoo = True

        self.jack_tokenizer.eat("***")  # dispose of  =
        self.compile_expression()
        if tempoo:
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)
        else:
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop(sagment, self.sym_tab.index_of(curr_var))
        self.jack_tokenizer.eat("***")  # dispose of ;

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        start_loop = "SL" + str(self.while_count)
        end_loop = "EL" + str(self.while_count)
        self.while_count += 1

        self.jack_tokenizer.eat("***")  # while
        self.jack_tokenizer.eat("***")  # (
        self.vm_writer.write_label(start_loop)
        self.compile_expression()
        self.vm_writer.write_push("temp", 0)
        self.vm_writer.write_arithmetic("neg")
        self.vm_writer.write_if(end_loop)
        self.jack_tokenizer.eat("***")  # )
        self.jack_tokenizer.eat("***")  # {
        self.compile_statements()
        self.vm_writer.write_goto(start_loop)
        self.jack_tokenizer.eat("***")  # }
        self.vm_writer.write_label(end_loop)

        pass

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!

        self.jack_tokenizer.eat("***")  # return
        if not self.jack_tokenizer.is_next_poi_br():
            self.compile_expression()
        else:
            self.vm_writer.write_push("constant", 0)
        self.jack_tokenizer.eat("***")  # ;
        self.vm_writer.write_return()
        pass

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        end_if = "EIL" + str(self.if_count)
        else_if = "EI" + str(self.if_count)
        self.if_count += 1

        self.jack_tokenizer.eat("***")  # if
        self.jack_tokenizer.eat("***")  # (
        self.compile_expression()
        self.jack_tokenizer.eat("***")  # )
        self.jack_tokenizer.eat("***")  # {
        self.vm_writer.write_push("temp", 0)
        self.vm_writer.write_arithmetic("neg")

        self.vm_writer.write_if(else_if)
        self.compile_statements()
        self.vm_writer.write_goto(end_if)
        self.jack_tokenizer.eat("***")  # }
        check = self.jack_tokenizer.eat("else")
        if check != "":  # else
            self.vm_writer.write_label(else_if)
            self.jack_tokenizer.eat("***")  # {
            self.compile_statements()
            self.jack_tokenizer.eat("***")  # }
        else:
            end_if = else_if
        self.vm_writer.write_label(end_if)

    def compile_expression(self) -> None:  # DONE
        """Compiles an expression."""
        # Your code goes here!
        self.compile_term()
        while self.jack_tokenizer.is_next_is_op():
            op = self.jack_tokenizer.eat("***")
            self.compile_term()
            if op == "+":
                self.vm_writer.write_arithmetic("add")
            elif op == "-":
                self.vm_writer.write_arithmetic("sub")
            elif op == "*":
                self.vm_writer.write_call("Math.multiply", 2)
            elif op == "/":
                self.vm_writer.write_call("Math.divide", 2)
            elif op == "&":
                self.vm_writer.write_arithmetic("and")
            elif op == "|":
                self.vm_writer.write_arithmetic("or")
            elif op == "<":
                self.vm_writer.write_arithmetic("lt")
            elif op == ">":
                self.vm_writer.write_arithmetic("gt")
            elif op == "=":
                self.vm_writer.write_arithmetic("eq")

    def compile_term(self) -> None:  # missing string impl
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        if self.jack_tokenizer.token_type() == "stringConstant":
            the_str = self.jack_tokenizer.eat("***")
            self.vm_writer.write_push("constant", len(the_str))
            self.vm_writer.write_call("Sting.new", 1)
            for s in the_str:
                self.vm_writer.write_push("constant", ord(s))
                self.vm_writer.write_call("String.appendChar", 1)

        elif self.jack_tokenizer.token_type() == "integerConstant":
            self.vm_writer.write_push("constant", int(self.jack_tokenizer.eat("***")))
        elif self.jack_tokenizer.is_next_k_w_const():
            curr_k_w = self.jack_tokenizer.eat("***")  # k_w_const maybe missing null
            if curr_k_w == "true":
                self.vm_writer.write_push("constant", 1)
                self.vm_writer.write_arithmetic("neg")
            if curr_k_w == "false" or "null":
                self.vm_writer.write_push("constant", 0)
            if curr_k_w == "this":
                self.vm_writer.write_push("pointer", 0)
        elif self.jack_tokenizer.is_next_is_un_op():
            curr_op = self.jack_tokenizer.eat("***")  # unary op
            self.compile_term()
            if curr_op == "-":
                self.vm_writer.write_arithmetic("neg")
            if curr_op == "~":
                self.vm_writer.write_arithmetic("not")
            if curr_op == "#":
                self.vm_writer.write_arithmetic("shiftleft")
            if curr_op == "^":
                self.vm_writer.write_arithmetic("shiftright")
        elif self.jack_tokenizer.is_next_is_par():
            self.jack_tokenizer.eat("***")  # (
            self.compile_expression()
            self.jack_tokenizer.eat("***")  # )
        else:
            curr_name = self.jack_tokenizer.eat("***")  # varName
            if self.jack_tokenizer.is_next_is_left_bracket():
                self.vm_writer.write_push(self.sym_tab.kind_of(curr_name), self.sym_tab.index_of(curr_name))
                self.jack_tokenizer.eat("***")  # [
                self.compile_expression()
                self.jack_tokenizer.eat("***")  # ]
                self.vm_writer.write_arithmetic("add")
                self.vm_writer.write_pop("pointer", 1)
                self.vm_writer.write_push("that", 0)
            elif self.jack_tokenizer.is_next_dot():
                self.jack_tokenizer.eat("***")  # .
                sr_name = self.jack_tokenizer.eat("***")  # subroutone name
                if self.sym_tab.kind_of(curr_name) is not None:
                    self.vm_writer.write_push(self.sym_tab.kind_of(curr_name), self.sym_tab.index_of(curr_name))
                    curr_name = sr_name
                    in_a = 1
                else:
                    curr_name = curr_name + "." + sr_name
                    in_a = 0
                self.jack_tokenizer.eat("***")  # (
                in_a += self.compile_expression_list()
                self.jack_tokenizer.eat("***")  # )
                self.vm_writer.write_call(curr_name, in_a)

            elif self.jack_tokenizer.is_next_is_left_par():
                self.jack_tokenizer.eat("***")  # (
                in_a = self.compile_expression_list()
                self.jack_tokenizer.eat("***")  # )
                self.vm_writer.write_call(curr_name, in_a)
            self.vm_writer.write_pop("temp", 0)

    def compile_expression_list(self):  # done
        """Compiles a (possibly empty) comma-separated list of expressions."""
        i = 0
        if not self.jack_tokenizer.is_next_is_right_par():
            i = 1
            self.compile_expression()
            check = self.jack_tokenizer.eat(",")
            while check != "":
                i = i + 1
                curr_name = self.jack_tokenizer.eat("***")  # varName
                self.vm_writer.write_push(self.sym_tab.kind_of(curr_name), self.sym_tab.index_of(curr_name))
                check = self.jack_tokenizer.eat(",")
        return i
