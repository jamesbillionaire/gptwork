"""Padded, two-column LAVI sign-off. No table zebra fill or inherited zero padding.

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
    spaceBefore = 4.0
    spaceAfter = 0.0

    def __init__(self, builder):
        super().__init__()
        self.b = builder
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
        self.height = max(100.0, 56.0 + self.person_height + self.padding)
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
                c.roundRect(x, 0, self.col_width, self.height, 4, fill=1, stroke=1)
                c.setStrokeColor(b.c('accent'))
                c.setLineWidth(.9)
                c.line(x + self.padding, self.height - 31,
                       x + self.col_width - self.padding, self.height - 31)
                _, h = label.wrap(self.inner_width, 100)
                label.drawOn(c, x + self.padding, self.height - self.padding - h)

            # Space to sign above the prepared-by identity.
            c.setStrokeColor(b.c('muted'));c.setLineWidth(.4)
            c.line(self.padding, self.height - 50,
                   self.col_width - self.padding, self.height - 50)
            self.person.drawOn(c, self.padding, self.height - 56 - self.person_height)

            # Same text style as the body; three separate writable fields.
            x = self.col_width + self.gutter + self.padding
            right = self.width - self.padding
            size = b.p['body'][0]
            c.setFont(b.font, size);c.setFillColor(b.c('ink'))
            for top, label in zip((40.0, 59.0, 78.0), self.fields):
                baseline = self.height - top
                rendered = label + ':'
                c.drawString(x, baseline, rendered)
                start = x + pdfmetrics.stringWidth(rendered, b.font, size) + 8
                c.line(start, baseline - 2, right, baseline - 2)
        finally:
            c.restoreState()
