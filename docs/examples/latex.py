from mako.template import Template
import os
import locale
from simplepyged import *

def escape_latex(in_str):
    map = {'#': '\\#', 
	'$': '\\$', 
	'%': '\\%', 
	'^': '\\textasciicircum{}', 
	'&': '\\&', 
	'_': '\\_', 
	'{': '\\{', 
	'}': '\\}', 
	'~': '\\~{}', 
	'\\': '\\textbackslash{}'}

    in_str = unicode(in_str)

    retval = ''
    for c in in_str:
        if c in map.keys():
            c = map[c]
        retval += c

    return retval
            

def name(person):
    if person is None:
        return ""

    if person.surname() is None:
        s = ''
    else:
        s = person.surname()

    if person.given_name() is None:
        g = ''
    else:
        g = person.given_name()
    return s + ", " + g

def push(stack, item):
    if item == None:
        return stack

    if item in stack:
        return stack

    stack.append(item)
    return stack

def construct_stack(stack, depth):
    if depth == 0:
        return []
    if stack == []:
        return []

    for family in stack:
        if family == None:
            continue
        addendum = []
        for p in family.parents():
            addendum = push(addendum, p.parent_family())
        for c in family.children():
            for f in c.families():
                addendum = push(addendum, f)

    expanded_family = construct_stack(addendum, depth - 1)

    for e in expanded_family:
        stack = push(stack, e)

    return stack

def latex_index(stack):
    individuals = []
    for family in stack:
        for p in family.parents():
            individuals = push(individuals, p)
        for c in family.children():
            individuals = push(individuals, c)

    locale.setlocale(locale.LC_ALL, '')

    individuals.sort(cmp=lambda x, y: locale.strcoll(name(x), name(y)))

    return individuals

def pages(individual):
    pages = []
    if individual.parent_family() is not None:
        return [individual.parent_family().xref()]
    for f in individual.families():
        if f is not None:
            pages.append(f.xref())

    return pages

#g = Gedcom(os.path.abspath('../../test/mcintyre.ged'))
g = Gedcom(os.path.abspath('../../test/wright.ged'))
#fam = g.get_family('@F5@')
#stack = [fam]
#stack = construct_stack(stack, 6)

stack = g.family_list()

latex = Template(
    filename = 'template.tex',
    default_filters=['unicode', 'escape_latex'],
    imports=['from latex import escape_latex'])
source = latex.render_unicode(stack=stack, index=latex_index(stack), pages=pages).encode('utf-8')

print source
