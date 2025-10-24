"""
src/schema.py
--------------------------------
Defines the Pydantic schema for structured course data.

INSTRUCTIONS FOR STUDENTS:
  • This file defines the schema the model will use when returning structured JSON.
  • See the lab instructions for the full list of fields and constraints.
  • Add the missing fields (between 'program' and 'tags') and any validators
    needed to enforce the rules described in the lab.
  • Use None for optional or missing values.
"""
from pydantic import BaseModel, field_validator
from typing import Optional
import re

class SectionRow(BaseModel):
    program:  str                   # Three-letter uppercase code (e.g. CSC, MAT).
    number:   str	                  #	Course number (e.g. “210” or “210L”).
    section:  Optional[str] = None  # Single lowercase letter (e.g. a, b).
    title:	  str	                  # Course title in title case.
    credits:	float	                #	Numeric values such as 3.0, 4.0, or 0.0.
    days:	    Optional[str] = None  #	Use None if “-------”.
    times:	  Optional[str] = None  #	Use None if “TBA”.
    room:	    Optional[str] = None  #	Building and room (e.g. “OLIN 208”). Use None if “TBA”.
    faculty:	str	                  #	Instructor name.
    tags:	    Optional[str] = None  #	Optional classification codes such as E1 or E1,A.


    @field_validator("program")
    @classmethod
    def validate_program(cls, v: str) -> str:
        """Program must be three uppercase letters like CSC or MAT."""
        v = v.upper()
        if not re.fullmatch(r"[A-Z]{3}", v):
            print(f"program must be like ECO, DSC letters but was {v}")
            return v
        return v   
    @field_validator("number")
    @classmethod
    def validate_number(cls, v: str) -> str:
        """Course number must be “210”  or 210L"""
        if not re.fullmatch(r"^[0-9]{3}[L]?$", v):
            print("course number must be three digits optionally followed by 'L'")
        return v
   
    @field_validator("section")
    @classmethod
    def validate_section(cls, v: Optional[str]) -> Optional[str]:
        """Section must be a single lowercase letter like 'a' or 'b'."""
        if v is None:
            return None
        v = v.lower()
        if not re.fullmatch(r"[a-z]", v):
            print("section must be a single lowercase letter")
        return v


    @field_validator("credits")
    @classmethod
    def validate_credits(cls, v: float) -> float:
        """Credits must be a valid number like 3.0, 4.0, or 0.0."""
        if not isinstance(v, (int, float)):
            print("credits must be a number")
        if v < 0:
            print("credits cannot be negative")
        # Round to 1 decimal place to ensure proper format
        return round(v, 1)
       
    @field_validator("days")
    @classmethod
    def validate_days(cls, v: Optional[str]) -> Optional[str]:
        """Days must be normalized to '-M-W-F-' or '--T-R--' format, or None if '-------'."""
        if v == "-------":
            return None
        if v is not None:
            # Remove any non-letter characters and convert to uppercase
            days = ''.join(c for c in v.upper() if c.isalpha())
            
            # Check and normalize MWF pattern
            if set(days) <= set('MWF') and len(days) > 0:
                return "-M-W-F-"
            # Check and normalize TR pattern
            elif set(days) <= set('TR') and len(days) > 0:
                return "--T-R--"
            else:
                print("days must contain either M,W,F or T,R")
        return v      
    @field_validator("room")
    @classmethod
    def validate_room(cls, v: Optional[str]) -> Optional[str]:
        """Room must be in format 'BUILDING ROOM' (e.g. 'OLIN 208') or None if 'TBA'."""
        if v == "TBA":
            return None
        if v is not None:
            # Check format: uppercase building name, space, room number
            if not re.fullmatch(r"[A-Z]+ [0-9]+", v):
                print("room must be in format 'BUILDING ROOM' (e.g. 'OLIN 208')")
        return v        
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[str]) -> Optional[str]:
        """Tags must be in format like 'E1' or 'E1,A' or None."""
        if v is None or v.strip().lower() == "none" or v.strip() == "":
            return None
        # Split by comma if multiple tags
        tags = [tag.strip() for tag in v.split(',')]
        print(f"Actual Values: {tags}")
        for tag in tags:
            # Each tag should be either:
            # - E followed by a number (E1, E2, etc.)
            # - A single uppercase letter (A, B, etc.)
            if tag.strip() == "":
                continue
            if not re.fullmatch(r'E[0-9]+|[A-Z]', tag):
                print("tags must be in format 'E1' or 'A' or 'E1,A'")
        return v