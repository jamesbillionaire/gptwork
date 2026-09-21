"""Validate job data without inferring tax, commercial terms or project facts."""
from __future__ import annotations
import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILES = json.loads((Path(__file__).parent / 'profiles.json').read_text())
CENT = Decimal('0.01')

class ValidationError(ValueError):
    pass

def money(value):
    if isinstance(value, (float, bool)):
        raise ValidationError('Use a decimal string or integer, never a float/bool, for money.')
    try:
        out = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(f'Invalid decimal: {value!r}') from None
    if not out.is_finite():
        raise ValidationError('Amounts must be finite.')
    return out

def fmt(value):
    return f'PHP {money(value).quantize(CENT, rounding=ROUND_HALF_UP):,.2f}'

def priced_blocks(job):
    return [b for b in job['blocks'] if b['type'] == 'boq']

def totals(job):
    groups = [(b['title'], sum((money(r['qty']) * money(r['unit_price'])).quantize(CENT, rounding=ROUND_HALF_UP) for r in b['items'])) for b in priced_blocks(job)]
    base = sum((x[1] for x in groups), Decimal(0))
    # Inclusive unit prices are summed as-is. No implicit or automatic 12% add-on.
    adjustment = sum((money(a['amount']) for a in job.get('adjustments', [])), Decimal(0))
    return groups, base + adjustment

def validate(job):
    if job.get('schema_version') != 2:
        raise ValidationError('Use schema_version 2; legacy jobs require explicit migration.')
    brand = job.get('brand')
    if brand not in PROFILES:
        raise ValidationError('Select lavi or lifes-awesome explicitly; never guess a brand.')
    if job.get('template_id') != PROFILES[brand]['template_id']:
        raise ValidationError('Job template_id must match the active profile.')
    for k in ('title','quote_no','date','tax_treatment','amount_words','salutation','footer_label'):
        if not isinstance(job.get(k), str) or not job[k].strip():
            raise ValidationError(f'Missing {k}.')
    if job['tax_treatment'] not in ('VAT Inclusive', 'VAT Exclusive'):
        raise ValidationError('Write VAT Inclusive or VAT Exclusive in full.')
    if not isinstance(job.get('validity_days'), int) or isinstance(job['validity_days'], bool) or job['validity_days'] <= 0:
        raise ValidationError('An explicit positive validity_days is required.')
    for k in ('name','address','attention','role','location'):
        if not isinstance(job.get('client', {}).get(k), str):
            raise ValidationError(f'Missing client.{k}.')
    for k in ('name','role'):
        if not job.get('prepared_by', {}).get(k):
            raise ValidationError(f'Missing prepared_by.{k}.')
    if job.get('signature'):
        raise ValidationError('Reusable jobs must be unsigned; use an explicitly authorized signing workflow.')
    if not job.get('blocks') or not priced_blocks(job):
        raise ValidationError('At least one priced section is required.')
    allowed = {'heading','paragraph','note','list','table','boq','diagram','total','page_break','callout'}
    for b in job['blocks']:
        if b.get('type') not in allowed:
            raise ValidationError(f'Unknown block: {b.get("type")}')
        if b['type'] == 'boq':
            if not b.get('title') or not b.get('items'):
                raise ValidationError('BOQ needs a title and line items.')
            for r in b['items']:
                if money(r['qty']) <= 0 or money(r['unit_price']) < 0:
                    raise ValidationError('Quantity must be positive and price nonnegative.')
                ext = (money(r['qty']) * money(r['unit_price'])).quantize(CENT, rounding=ROUND_HALF_UP)
                if 'amount' in r and money(r['amount']) != ext:
                    raise ValidationError(f'Line extension mismatch: {r["description"][:50]}')
                if not r.get('description') or not r.get('unit'):
                    raise ValidationError('Missing description or unit.')
            subtotal = sum((money(r['qty']) * money(r['unit_price'])).quantize(CENT, rounding=ROUND_HALF_UP) for r in b['items'])
            if 'subtotal' in b and money(b['subtotal']) != subtotal:
                raise ValidationError(f'Section subtotal mismatch: {b["title"]}')
        if b['type'] == 'table':
            widths = b.get('widths', [])
            if not widths or abs(sum(widths) - 1) > 0.00001 or any(x <= 0 for x in widths):
                raise ValidationError('Table widths must be positive and sum to one.')
            if any(len(r) != len(widths) for r in b['rows']):
                raise ValidationError('Table row/column mismatch.')
        if b['type'] == 'diagram':
            if not b.get('rows') or any(not row.get('nodes') for row in b['rows']):
                raise ValidationError('Every diagram row needs nodes.')
    _, total = totals(job)
    if total < 0 or money(job['expected_total']) != total:
        raise ValidationError(f'Total mismatch; calculated {total}, declared {job["expected_total"]}.')
    for a in job.get('adjustments', []):
        if not a.get('label'):
            raise ValidationError('Adjustments must be explicitly labeled.')
    return {'brand': brand, 'template_id': job['template_id'], 'total': str(total), 'sections': len(priced_blocks(job))}
