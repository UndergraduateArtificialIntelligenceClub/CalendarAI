# The deadline shape the AI parser returns. Keep it in sync with frontend/src/types.ts.

from typing import Literal

from pydantic import BaseModel

Category = Literal["assignment", "lab", "quiz", "midterm", "final", "other"]


class Deadline(BaseModel):
    course: str                  # e.g. "CMPUT 174"
    title: str                   # e.g. "Assignment 2"
    date: str                    # "YYYY-MM-DD"
    category: Category
    source_text: str             # the exact sentence from the syllabus
    weight: float | None = None  # percent of final grade, e.g. 15. None when unknown


# What POST /parse and POST /parse-pdf return
class ParseResponse(BaseModel):
    deadlines: list[Deadline]
    instructor: str | None = None  # e.g. "Dr. Smith". None when the syllabus doesn't say
