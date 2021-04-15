import datetime

question_body1 = """
<p>When I attempt call <code>add()</code>, I get the following error:</p>

<ul>
<li><code>NameError: 'x' is not defined</code>.</li>
</ul>

<p>What is causing this <code>NameError</code> to be raised?</p>

<pre><code>def add():
    return x + 1
</code></pre>
"""

question_body2 = """
<p>Upon studying database relationships, a relation happens to be set of records
of the same type that is stored in the database. Yet, I'm not understanding
what purpose the primary key serves? How does a record benefit from having
a primary key?</p>
"""

question_body3 = """
<p>I'm currently reading about decorators in Python; yet I'm unsure of their
use cases. When are they commonly used? What benefits do they provide?</p>

<pre><code>@decorator
def go():
    pass
</code></pre>
"""

question_body4 = """
<p>I'm trying to filter a list using the built-in <code>filter</code> method.
When trying to print the result a <code>&lt;filter object&gt;</code>
is returned. I was expect for a list to be returned. What is the difference
between a list and a filter object?</p>

<pre><code>items = ['A', 'B', 'C', 'D', 'E']
result = filter(lambda x: x == 'B' or x == 'C', items)
print(result)
</code></pre>
"""


mock_questions_submitted = [
    {
        'title': 'NameError: \'x\' is not defined',
        'body': question_body1,
        'dated': datetime.date(2021, 3, 12)
    },
    {
        'title': "What is a primary key?",
        'body': question_body2,
        'dated': datetime.date(2021, 3, 10)
    },
    {
        'title': "What are Python decorators use cases?",
        'body': question_body3,
        'dated': datetime.date(2021, 3, 5)
    },
    {
        'title': "How do filter objects work?",
        'body': question_body4,
        'dated': datetime.date(2021, 2, 27)
    },
]
