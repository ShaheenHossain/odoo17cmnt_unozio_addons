###################################################################################
#
#    Copyright (C) 2020 Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

FILTER_CONDITION = [
    ("from", "From"),
    ("to", "To"),
    ("author", "Author"),
    ("recipients", "Recipients"),
    ("subject", "Subject"),
    ("body", "Body"),
]

CONDITION_STATE_CONTAINS = {"like": False, "not_like": True}
CONDITION_STATE_EQ = {"is": False, "not": True}

CONDITION = {
    "is": "is",
    "not": "not",
    "like": "contains",
    "not_like": "doesn't contain",
}
