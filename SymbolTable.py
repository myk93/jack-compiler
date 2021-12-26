"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.sym_table_cl = []
        self.sym_table_sr = []

        self.i_static = 0
        self.i_field = 0
        self.i_arg = 0
        self.i_var = 0

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        # Your code goes here!
        self.sym_table_sr = []
        self.i_arg = 0
        self.i_var = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        # Your code goes here!

        num = 0
        which_table = 1
        if kind == "STATIC":
            num = self.i_static
            self.i_static += 1
            which_table = 0
            to_enter = "static"
        elif kind == "FIELD":
            num = self.i_field
            self.i_field += 1
            which_table = 0
            to_enter = "field"
        elif kind == "ARG":
            num = self.i_arg
            self.i_arg += 1
            to_enter = "argument"
        elif kind == "VAR":
            num = self.i_var
            self.i_var += 1
            to_enter = "local"
        if which_table == 0:
            self.sym_table_cl.append({name, type, to_enter, num})
        else:
            self.sym_table_sr.append({name, type, to_enter, num})

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        # Your code goes here!
        if kind == "STATIC":
            return self.i_static
        elif kind == "FIELD":
            return self.i_field
        elif kind == "ARG":
            return self.i_arg
        else:
            return self.i_var

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        # Your code goes here!
        for row in self.sym_table_sr:
            if row[0] == name:
                return row[2]
        for row in self.sym_table_cl:
            if row[0] == name:
                return row[2]
        return None

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        # Your code goes here!
        for row in self.sym_table_sr:
            if row[0] == name:
                return row[1]
        for row in self.sym_table_cl:
            if row[0] == name:
                return row[1]
        return None

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        # Your code goes here!
        for row in self.sym_table_sr:
            if row[0] == name:
                return row[3]
        for row in self.sym_table_cl:
            if row[0] == name:
                return row[3]
        return None
