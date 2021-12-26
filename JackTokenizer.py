"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

KEYWORDS = ["class", "method", "function", "constructor", "int", "boolean",
            "char", "void", "var", "static", "field", "let", "do", "if",
            "else", "while", "return", "true", "false", "null", "this"]

SYMBOLS = ["{", "}", "[", "]", "(", ")", ".", ",", ";", "+", "-", "*", "/",
           "&", "|", "<", ">", "=", "~", "^", "#"]


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is:
        self.tokenized_lines = []
        self.input_lines = input_stream.read().splitlines()
        self.cleanup_lines()
        self.tokenize_lines()
        self.current = 0

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if self.current >= len(self.tokenized_lines):
            return False
        return True

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.current += 1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        if self.tokenized_lines[self.current] in KEYWORDS:
            return "keyword"
        if self.tokenized_lines[self.current] in SYMBOLS:
            return "symbol"
        if str(self.tokenized_lines[self.current][0]).isdigit():
            return "integerConstant"
        if self.tokenized_lines[self.current][0] == '"':
            return "stringConstant"
        else:
            return "identifier"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return str(self.tokenized_lines[self.current]).upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        return self.tokenized_lines[self.current]

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        # Your code goes here!
        return self.tokenized_lines[self.current]

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return int(self.tokenized_lines[self.current])

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        return self.tokenized_lines[self.current]

    def cleanup_lines(self) -> None:
        """Removes all comments from the input stream.
        """
        i = 0
        while i != len(self.input_lines):
            # remove empty lines and inline comments
            self.input_lines[i] = self.input_lines[i].replace("\t", " ")

            if "//" in self.input_lines[i]:
                self.input_lines[i] = self.input_lines[i].split("//")[0]
            elif len(self.input_lines[i].replace(" ", "")) == 0 or self.input_lines[i].replace(" ", "")[0:2] == "//":
                self.input_lines.pop(i)

            # remove lines between /* and */
            elif self.input_lines[i].replace(" ", "")[0:2] == "/*":
                if "*/" in self.input_lines[i].replace(" ", ""):
                    self.input_lines.pop(i)
                    continue
                while len(self.input_lines[i].replace(" ", "")) == 0 or self.input_lines[i].replace(" ", "")[
                                                                        0:2] != "*/":
                    self.input_lines.pop(i)
                self.input_lines.pop(i)
            else:
                ' '.join(self.input_lines[i].split())
                i += 1

    def tokenize_lines(self):
        """Tokenizes the input stream.
        """
        self.tokenized_lines = []
        i = 0
        current_str = ""
        in_string = False
        # split the line from input_lines where there is a space and '(', ')', '{', '}', '.', ',' , ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~', '"'
        for line in self.input_lines:
            for chara in range(len(line)):
                if line[chara] in SYMBOLS and not in_string:
                    if current_str != "":
                        self.tokenized_lines.append(current_str)
                    self.tokenized_lines.append(line[chara])
                    current_str = ""
                elif line[chara] == " " and not in_string:
                    self.tokenized_lines.append(current_str)
                    current_str = ""
                elif line[chara] == "\"":  # in case we are in string
                    in_string = not in_string
                    current_str += line[chara]
                    if not in_string:
                        self.tokenized_lines.append(current_str)
                        current_str = ""
                elif not str(line[chara]).isdigit() and str(current_str).isdigit() and not in_string:  # in case integer
                    self.tokenized_lines.append(current_str)
                    current_str = line[chara]
                else:
                    current_str += line[chara]
        while i != len(self.tokenized_lines):
            # remove empty lines
            if len(self.tokenized_lines[i]) == 0:
                self.tokenized_lines.pop(i)
            else:
                i = i + 1

    def eat(self, token: str) -> str:
        if token == "***":
            token = self.tokenized_lines[self.current]
        if token != self.tokenized_lines[self.current]:
            return ""

       # if token == "<":
        #    token = "&lt;"
        #elif token == ">":
        #    token="&gt;"
        #elif token == "&":
        #    token = "&amp;"
        #elif token == '"':
        #    token = "&quot;"
        if self.token_type() == 'stringConstant':
            token = token[1:-1]
        str_statement = token
        if self.has_more_tokens():
            self.advance()
        return str_statement

    def get_op(self):
        return self.tokenized_lines[self.current]

    def is_next_dot(self):
        if self.tokenized_lines[self.current] == ".":
            return True
        return False

    def is_next_statment(self):
        if self.tokenized_lines[self.current] in ["let", "if", "while", "do", "return"]:
            return self.tokenized_lines[self.current]
        return ""

    def is_next_var_dec(self):
        if self.tokenized_lines[self.current] == "var":
            return True
        return False

    def is_next_class_var_dec(self):
        if self.tokenized_lines[self.current] in ["static", "field"]:
            return True
        return False

    def is_next_class_sub_dec(self):
        if self.tokenized_lines[self.current] in ["constructor", "function", "method"]:
            return True
        return False

    def is_next_k_w_const(self):
        if self.tokenized_lines[self.current] in ["true", "false", "null", "this"]:
            return True
        return False

    def is_next_is_op(self):
        opar = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
        if self.tokenized_lines[self.current] in opar:
            return True
        return False

    def is_next_is_un_op(self):
        opar = ["-", "~", "^", "#"]
        if self.tokenized_lines[self.current] in opar:
            return True
        return False

    def is_next_is_bracket(self):
        brack = ["[", "]"]
        if self.tokenized_lines[self.current] in brack:
            return True
        return False
    def is_next_is_left_bracket(self):
        brack = ["["]
        if self.tokenized_lines[self.current] in brack:
            return True
        return False
    def is_next_is_par(self):
        brack = ["(", ")"]
        if self.tokenized_lines[self.current] in brack:
            return True
        return False

    def is_next_is_left_par(self):
        brack = ["("]
        if self.tokenized_lines[self.current] in brack:
            return True
        return False

    def is_next_is_right_par(self):
        brack = [")"]
        if self.tokenized_lines[self.current] in brack:
            return True
        return False

    def is_next_is_cur_bracket(self):
        brack = ["{", "}"]
        if self.tokenized_lines[self.current] in brack:
            return True
        return False

    def is_next_poi_br(self):
        if self.tokenized_lines[self.current] == ";":
            return True
        return False
        pass
