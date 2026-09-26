"""Balanced, two-column LAVI sign-off with real signing space.

Geometry is relative to the full content rail. This indivisible flowable moves as
one unit when the page has insufficient space. It never inserts a signature image.
"""
from __future__ import annotations
from xml.sax.saxutils import escape
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Flowable

class TwoColumnSignoff(Flowable):
    gutter = 18.0
    padding = 14.0

    def __init__(self, builder):
        super().__init__()
        self.b = builder
        p = builder.p
        self.spaceBefore = p.get('signoff_space_before', 12.0)
        self.spaceAfter = p.get('signoff_space_after', 2.0)
        self.width = builder.w
        self.col_width = (self.width - self.gutter) / 2
        self.inner_width = self.col_width - 2 * self.padding
        self.labels = [builder.P(t, 'label', alignment=TA_LEFT)
                       for t in ('PREPARED BY', 'CONFORME')]
        person = builder.job['prepared_by']
        self.person = builder.P(
            '<b>' + escape(person['name']) + '</b><br/>' +
            escape(person['role']) + ' | ' + escape(builder.p['display_name']),
            'meta', alignment=TA_LEFT, spaceAfter=0)
        _, self.person_height = self.person.wrap(self.inner_width, 1000)
        self.height = max(float(p.get('signoff_height', 148.0)),
                          102.0 + self.person_height + self.padding)
        fields = builder.job.get('conforme_fields', {})
        self.fields = [fields.get(k, default) for k, default in (
            ('authorized_name', 'Authorized name'), ('signature', 'Signature'),
            ('date', 'Date'))]
        size = builder.p['body'][0]
        for label in self.fields:
            if pdfmetrics.stringWidth(label + ':', builder.font, size) > self.inner_width - 64:
                raise ValueError('Conforme label leaves insufficient writing space.')

    def wrap(self, availWidth, availHeight):
        if self.width > availWidth + .1:
            raise ValueError('Sign-off is wider than the content rail.')
        return self.width, self.height

    def draw(self):
        c, b = self.canv, self.b
        c.saveState()
        try:
            for i, label in enumerate(self.labels):
                x = i * (self.col_width + self.gutter)
                c.setFillColorRGB(1, 1, 1)
                c.setStrokeColor(b.c('border'))
                c.setLineWidth(.5)
                c.roundRect(x, 0, self.col_width, self.height, 5, fill=1, stroke=1)
                _, h = label.wrap(self.inner_width, 100)
                label_y = self.height - self.padding - h
                label.drawOn(c, x + self.padding, label_y)
                rule_y = self.height - 34.0
                c.setStrokeColor(b.c('accent'))
                c.setLineWidth(.9)
                c.line(x + self.padding, rule_y,
                       x + self.col_width - self.padding, rule_y)

            c.setStrokeColor(b.c('muted'))
            c.setLineWidth(.45)
            person_y = 18.0
            left_line_y = person_y + self.person_height + 7.0
            c.line(self.padding, left_line_y,
                   self.col_width - self.padding, left_line_y)
            self.person.drawOn(c, self.padding, person_y)

            x = self.col_width + self.gutter + self.padding
            right = self.width - self.padding
            size = b.p['body'][0]
            c.setFont(b.font, size)
            c.setFillColor(b.c('ink'))
            baselines = [self.height - 58.0, self.height - 90.0, self.height - 122.0]
            for baseline, label in zip(baselines, self.fields):
                rendered = label + ':'
                c.drawString(x, baseline, rendered)
                start = x + pdfmetrics.stringWidth(rendered, b.font, size) + 8
                c.setStrokeColor(b.c('muted'))
                c.setLineWidth(.4)
                c.line(start, baseline - 2, right, baseline - 2)
        finally:
            c.restoreState()
