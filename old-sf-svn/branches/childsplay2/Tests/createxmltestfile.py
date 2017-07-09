
xml = """
   <question id="%s" type="text">
    <difficulty>1</difficulty>
            <question_text audio=''>Als je 50 jaar getrouwd bent dan vier je welk jubileum?</question_text>
            <answer audio=''>Goud</answer>
            <data></data>
            <wrong_answer1 audio=''>Robijn</wrong_answer1>
            <wrong_answer2 audio=''>Parelen</wrong_answer2>
            <wrong_answer3 audio=''>Kroonjuwelen</wrong_answer3>
    </question>
    """

lines = ["""<?xml version="1.0" encoding="utf-8"?>\n<questions>\n"""]

for i in xrange(1000):
    lines.append(xml % i)
lines.append('</questions>')
f = open('test.xml', 'w')
f.writelines(lines)
f.close()
