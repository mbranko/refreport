# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import sys
import os
import re
import glob
import jinja2
import codecs
from arpeggio import NoMatch
from bibtex import parse_bibtex

sys.stdout = codecs.getwriter('utf8')(sys.stdout)

points_table = {
    'M11': '15',
    'M12': '10',
    'M13': '6',
    'M14': '4',
    'M21': '8',
    'M22': '5',
    'M23': '3',
    'M24': '3',
    'M31': '3',
    'M32': '1.5',
    'M33': '1',
    'M34': '0.5',
    'M41': '7',
    'M42': '5',
    'M43': '3',
    'M44': '2',
    'M45': '1.5',
    'M51': '2',
    'M52': '1.5',
    'M53': '1',
    'M55': '2',
    'M56': '1',
    'M61': '1.5',
    'M62': '1',
    'M63': '0.5',
    'M71': '6',
    'M72': '3',
    'M81': '8',
    'M82': '6',
    'M83': '4',
    'M84': '3',
    'M85': '2',
    'M91': '10',
    'M92': '8',
}


def points(type):
    return points_table.get(type, '')


def coauthors_filter(author_list):
    return ", ".join(author_list[1:])


def isbn_issn(ref):
    return ref.get('isbn', ref.get('issn', ''))


def booktitle_journal(ref):
    return ref.get('booktitle', ref.get('journal', ''))


def check_keys(refs):
    """
    Check mandatory keys.
    """
    mandatory = [('project',), ('rank',), ('title',), ('booktitle', 'journal'),
                 ('author',), ('year',), ('isbn', 'issn'),
                 ('publisher',), ('pages',)]
    for r in refs:
        for key in mandatory:
            if all([x not in r or not r[x] for x in  key]):
                print("Polje {} ne postoji u referenci {}"
                      .format(" ili ".join(key), r['bibkey']))


def gen_html(refs):

    projects = {}
    for r in refs:
        project = r.get('project', None)
        if not project:
            project = "Bez projekta"
        if project not in projects:
            projects[project] = list()
        projects[project].append(r)

    # Initialize template engine.
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

    # Filters
    jinja_env.filters['points'] = points
    jinja_env.filters['coauthors'] = coauthors_filter
    jinja_env.filters['isbn_issn'] = isbn_issn
    jinja_env.filters['booktitle_journal'] = booktitle_journal

    # Load Java template
    template = jinja_env.get_template('refreport.template')

    # For each entity generate java file
    with codecs.open('refreport.html', 'w', encoding="utf-8") as f:
        f.write(template.render(projects=projects))


if __name__ == "__main__":
    refs = []
    bibtex_dir = os.path.join(os.path.dirname(__file__), 'bibtex-files')
    bibtex_files = glob.glob(os.path.join(bibtex_dir, '*.bib'))

    for f in bibtex_files:
        print("Obrađujem fajl {}".format(f))
        try:
            refs_f = parse_bibtex(f)
            for r in refs_f:
                r['author'] = [x.strip() for x in
                               re.split(' and |,', r['author'])]
            check_keys(refs_f)
            refs.extend(refs_f)
        except NoMatch as e:
            print(e)

    gen_html(refs)






