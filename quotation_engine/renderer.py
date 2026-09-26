"""Shared, data-driven production renderer for the two approved CPSC design profiles.

No embedded customer, pricing, validity, duration or signing defaults. Typography
and component geometry come from the locked brand profile, never a job override.
"""
from __future__ import annotations
import os
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle, Spacer, PageBreak, NextPageTemplate, Flowable, CondPageBreak
from PIL import Image
from .validation import PROFILES, ROOT, validate, totals, fmt, money
from .diagrams import Diagram
from .signoff import TwoColumnSignoff

class PageCanvas(Canvas):
    def __init__(self,*a,**kw):
        kw['invariant']=1
        super().__init__(*a,**kw);self.states=[]
    def showPage(self):
        self.states.append(dict(self.__dict__));self._startPage()
    def save(self):
        total=len(self.states)
        for state in self.states:
            self.__dict__.update(state)
            self.setFont(self._page_font,self._page_furniture_size);self.setFillColor(colors.HexColor('#65717E'))
            self.drawRightString(self._pagesize[0]-self._page_margin,self._page_footer_y,f'Page {self._pageNumber} of {total}')
            super().showPage()
        super().save()

def register_fonts(profile):
    family=profile['font']
    dirs=[Path(os.environ.get('QUOTATION_FONT_DIR','/nonexistent')),Path('/usr/share/fonts/truetype/liberation'),Path('/usr/share/fonts/truetype/liberation2'),Path('/usr/share/fonts/truetype/dejavu'),Path('C:/Windows/Fonts')]
    if family=='LiberationSans': names=['LiberationSans-Regular.ttf','LiberationSans-Bold.ttf','LiberationSans-Italic.ttf']
    else:names=['DejaVuSans.ttf','DejaVuSans-Bold.ttf','DejaVuSans-Oblique.ttf']
    regs=[family,family+'-Bold',family+'-Italic']
    for name,reg in zip(names,regs):
        path=next((d/name for d in dirs if (d/name).is_file()),None)
        if path is None:raise RuntimeError(f'Missing {name}; install the documented font package or set QUOTATION_FONT_DIR. No silent substitution.')
        if reg not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont(reg,str(path)))
    pdfmetrics.registerFontFamily(family,normal=regs[0],bold=regs[1],italic=regs[2],boldItalic=regs[1])
    return regs

class Heading(Flowable):
    keepWithNext=1
    def __init__(self,paragraph,width,color,space_before=10,space_after=8):
        super().__init__();self.paragraph=paragraph;self.width=width;self.color=color
        self.spaceBefore=space_before;self.spaceAfter=space_after
    def wrap(self,aW,aH):
        _,h=self.paragraph.wrap(self.width,aH);self.height=h+5;return self.width,self.height
    def draw(self):
        self.paragraph.drawOn(self.canv,0,5)
        self.canv.setStrokeColor(self.color);self.canv.setLineWidth(.65);self.canv.line(0,0,self.width,0)

class ListMarker(Flowable):
    """Draw a list marker on the exact first-line baseline of its sibling paragraph."""
    def __init__(self, marker, width, font, font_size, leading, color):
        super().__init__()
        self.marker=str(marker); self.width=width; self.height=leading
        self.font=font; self.font_size=font_size; self.color=color
        self.ascent=pdfmetrics.getAscent(font, font_size)

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        c=self.canv
        c.saveState()
        try:
            c.setFont(self.font,self.font_size)
            c.setFillColor(self.color)
            c.drawRightString(self.width,self.height-self.ascent,self.marker)
        finally:
            c.restoreState()

class Builder:
    def __init__(self,job):
        validate(job);self.job=job;self.p=PROFILES[job['brand']];p=self.p
        self.font,self.bold,self.italic=register_fonts(p)
        self.w=p['page'][0]-2*p['margin'];self.software=job['brand']=='lifes-awesome'
        self.styles={}
        for name,key in [('body','body'),('note','note'),('cell','table'),('heading','heading'),('sub','subheading'),('title','title')]:
            size,leading=p[key]
            space_after=(6 if name in ('body','note') else 0) if self.software else (5 if name=='body' else 4 if name=='note' else 0)
            self.styles[name]=ParagraphStyle(name,fontName=self.bold if name in ('heading','sub','title') else self.font,fontSize=size,leading=leading,
                textColor=self.c('heading_color' if name=='heading' else ('dark' if name in ('sub','title') else 'ink')),
                alignment=TA_JUSTIFY if name in ('body','note') else TA_LEFT,spaceAfter=space_after)
        self.styles['head']=ParagraphStyle('head',fontName=self.bold,fontSize=p.get('table_header_size',10),leading=p.get('table_header_leading',12),textColor=colors.white,alignment=TA_CENTER)
        self.styles['meta']=ParagraphStyle('meta',fontName=self.font,fontSize=p.get('metadata_size',10),leading=p.get('metadata_leading',13),textColor=self.c('ink'))
        self.styles['label']=ParagraphStyle('label',fontName=self.bold,fontSize=p.get('metadata_size',10),leading=p.get('metadata_leading',13),textColor=self.c('heading_color'))
    def c(self,key):return colors.HexColor(self.p.get(key,key))
    def P(self,text,style='body',**kw):
        st=self.styles[style]
        # Content roles cannot be shrunk below their semantic style. Only metadata
        # may intentionally use the smaller contact/footer furniture size.
        floor=self.p['minimum_font_size'] if style=='meta' else st.fontSize
        size=max(floor,kw.get('fontSize',st.fontSize))
        leading=max(kw.get('leading',st.leading),size*1.2)
        st=ParagraphStyle(style+'-local',parent=st,**{**kw,'fontSize':size,'leading':leading})
        return Paragraph(str(text),st)
    def page_geometry(self):
        """Measure live contact/header/footer text instead of shrinking it."""
        p=self.p;m=p['margin'];W,H=p['page']
        self.first_header=[]
        if self.software:
            x=m;width=self.w;top=84
        else:
            x=m+104.88+24;width=self.w-104.88-24;top=42.52
            para=self.P(escape(p['company']),'meta',fontName=self.bold,fontSize=p.get('company_header_size',self.styles['sub'].fontSize),leading=p.get('company_header_leading',self.styles['sub'].leading),alignment=TA_RIGHT)
            _,height=para.wrap(width,H);self.first_header.append((para,x,top,height));top+=height+3
        for line in p['contact']:
            para=self.P(escape(line),'meta',fontSize=p.get('contact_size',self.styles['meta'].fontSize),leading=p.get('contact_leading',self.styles['meta'].leading),alignment=TA_CENTER if self.software else TA_RIGHT,textColor=self.c('muted'))
            _,height=para.wrap(width,H);self.first_header.append((para,x,top,height));top+=height+1
        self.first_rule=max(top,94 if not self.software else 106)+9
        company=self.P(escape(p['company']),'meta',fontName=self.bold,fontSize=p.get('continuation_company_size',self.styles['meta'].fontSize),leading=p.get('continuation_company_leading',self.styles['meta'].leading))
        ref=self.P(escape(self.job['quote_no'])+'  |  FORMAL QUOTATION','meta',fontSize=p.get('furniture_size',self.styles['meta'].fontSize),leading=p.get('furniture_leading',self.styles['meta'].leading),alignment=TA_RIGHT,textColor=self.c('muted'))
        # Separate lines prevent reference/company collisions with long references.
        _,ch=company.wrap(self.w,H);_,rh=ref.wrap(self.w,H)
        top=37 if not self.software else 26
        self.later_header=[(company,m,top,ch),(ref,m,top+ch+2,rh)]
        self.later_rule=top+ch+2+rh+8
        footer=escape(p['company']+'  |  '+self.job['footer_label'])
        self.footer=self.P(footer,'meta',fontSize=p.get('furniture_size',10),leading=p.get('furniture_leading',12),spaceAfter=0,textColor=self.c('muted'))
        _,self.footer_height=self.footer.wrap(self.w-88,H)
        self.footer_rule=18+self.footer_height+8
        return self.first_rule+14,self.later_rule+12,max(p['bottom'],self.footer_rule+12)
    def header(self,c,doc,first=False):
        p=self.p;j=self.job;W,H=p['page'];m=p['margin'];r=W-m
        c._page_font=self.font;c._page_furniture_size=p.get('furniture_size',10);c._page_margin=m;c._page_footer_y=20
        c.saveState()
        c.setFillColor(self.c('accent'))
        c.rect(m,H-(14 if self.software else 29.76 if first else 26.93),self.w,1.25 if self.software else 3.54 if first else 2.55,fill=1,stroke=0)
        if first:
            logo=ROOT/p['logo'];lw=270 if self.software else 104.88
            with Image.open(logo) as im:lh=lw*im.height/im.width
            x=(W-lw)/2 if self.software else m;y=H-22-lh if self.software else H-42.52-lh
            c.drawImage(str(logo),x,y,width=lw,height=lh,mask='auto')
        for para,x,top,height in (self.first_header if first else self.later_header):
            para.drawOn(c,x,H-top-height)
        rule=self.first_rule if first else self.later_rule
        c.setStrokeColor(self.c('border'));c.setLineWidth(.45);c.line(m,H-rule,r,H-rule)
        c.line(m,self.footer_rule,r,self.footer_rule)
        self.footer.drawOn(c,m,18)
        c.restoreState()
    def heading(self,text):return Heading(self.P(text,'heading'),self.w,self.c('accent'),self.p.get('heading_space_before',9) if not self.software else 10,self.p.get('heading_space_after',6) if not self.software else 8)
    def table(self,data,widths,header=False,style_extra=None):
        padding = self.p.get('flow_table_padding', self.p['table_padding']) if not self.job.get('front_page_break', True) else self.p['table_padding']
        t=Table(data,colWidths=[self.w*x for x in widths],repeatRows=1 if header else 0,hAlign='LEFT',splitByRow=1)
        commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,self.c('border')),
            ('LEFTPADDING',(0,0),(-1,-1),6 if self.software else 4),('RIGHTPADDING',(0,0),(-1,-1),6 if self.software else 4),
            ('TOPPADDING',(0,0),(-1,-1),padding),('BOTTOMPADDING',(0,0),(-1,-1),padding),
            ('ROWBACKGROUNDS',(0,1 if header else 0),(-1,-1),[colors.white,self.c('light')])]
        if header:commands += [('BACKGROUND',(0,0),(-1,0),self.c('table_header')),('NOSPLIT',(0,0),(-1,1))]
        t.setStyle(TableStyle(commands+(style_extra or [])));t.spaceAfter=6 if self.software else self.p.get('table_space_after',7);return t
    def generic_table(self,b):
        raw_rows=b['rows'];ncols=len(b['widths'])
        names={'left':TA_LEFT,'center':TA_CENTER,'right':TA_RIGHT}
        alignments=b.get('alignments') or ['left']*ncols
        if len(alignments)!=ncols or any(a not in names for a in alignments):
            raise ValueError('Table alignments must match the column count and use left/center/right.')
        data=[]
        for ri,row in enumerate(raw_rows):
            converted=[]
            for ci,c in enumerate(row):
                if b.get('header') and ri==0:
                    converted.append(self.P(c,'head',alignment=TA_CENTER))
                else:
                    kw={'alignment':names[alignments[ci]]}
                    if ci==0 and not b.get('header'):kw['fontName']=self.bold
                    converted.append(self.P(c,'cell',**kw))
            data.append(converted)
        fractions=b['widths']
        if not self.software and ncols==2 and self.p.get('generic_two_column_widths'):
            fractions=self.p['generic_two_column_widths']
        widths=[self.w*x for x in fractions]
        pad=12 if self.software else 8
        minima=[max(row[i].minWidth() for row in data)+pad+.1 for i in range(len(widths))]
        extras=sum(max(0,lo-w) for lo,w in zip(minima,widths))
        if extras:
            widths=[max(w,lo) for w,lo in zip(widths,minima)]
            for i in sorted(range(len(widths)),key=lambda i:widths[i]-minima[i],reverse=True):
                take=min(extras,max(0,widths[i]-minima[i]));widths[i]-=take;extras-=take
            if extras>.01:raise ValueError('Table cannot fit unbroken words at the minimum type size.')
        extra=[('VALIGN',(0,0),(-1,-1),'MIDDLE')] if not self.software else None
        return self.table(data,[x/self.w for x in widths],b.get('header',False),extra)

    def lavi_list_item(self, marker, text, numbered=False):
        marker_w=self.p.get('number_marker_width',24.0) if numbered else self.p.get('bullet_marker_width',14.0)
        gutter=self.p.get('list_gutter',5.0)
        marker_font=self.bold if numbered else self.font
        marker_p=ListMarker(marker,marker_w-gutter,marker_font,self.styles['body'].fontSize,self.styles['body'].leading,self.c('ink'))
        text_p=self.P(text.strip(),'body',alignment=TA_LEFT,spaceAfter=0)
        t=Table([[marker_p,text_p]],colWidths=[marker_w,self.w-marker_w],hAlign='LEFT',splitByRow=1)
        t.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
            ('TOPPADDING',(0,0),(-1,-1),self.p.get('list_top_padding',1.5)),('BOTTOMPADDING',(0,0),(-1,-1),self.p.get('list_bottom_padding',3.0)),
        ]))
        t.spaceAfter=0
        return t

    def boq(self,b):
        title=self.P(b['title'],'sub',keepWithNext=False,spaceBefore=6 if self.software else self.p.get('boq_subheading_space_before',7),spaceAfter=4 if self.software else self.p.get('boq_subheading_space_after',4))
        heads=['QTY','UNIT','DESCRIPTION / DELIVERABLE' if self.software else 'DESCRIPTION','UNIT PRICE','AMOUNT']
        data=[[self.P(h,'head') for h in heads]]
        for r in b['items']:
            data.append([self.P(r['qty'],'cell',alignment=TA_CENTER),self.P(r['unit'],'cell',alignment=TA_CENTER),self.P(r['description'],'cell'),self.P(fmt(r['unit_price']),'cell',alignment=TA_RIGHT),self.P(fmt(str(money(r['qty'])*money(r['unit_price']))),'cell',alignment=TA_RIGHT)])
        subtotal=sum(money(r['qty'])*money(r['unit_price']) for r in b['items'])
        data.append(['','',self.P('SECTION SUBTOTAL','cell',fontName=self.bold),'',self.P(fmt(str(subtotal)),'cell',alignment=TA_RIGHT,fontName=self.bold)])
        cmds=[('SPAN',(2,-1),(3,-1)),('BACKGROUND',(2,-1),(-1,-1),self.c('tint')),('NOSPLIT',(0,-2),(-1,-1)),('VALIGN',(0,0),(-1,-1),'MIDDLE')]
        if self.software:
            data.insert(0,[self.P(b['title'],'sub'),'','','',''])
            cmds += [('SPAN',(0,0),(-1,0)),('BACKGROUND',(0,0),(-1,0),self.c('tint')),('LINEABOVE',(0,0),(-1,0),.7,self.c('accent')),('BACKGROUND',(0,1),(-1,1),self.c('table_header')),('NOSPLIT',(0,0),(-1,2))]
        t=self.table(data,self.p['columns'],True,cmds)
        if self.software:t.repeatRows=2
        if self.software:
            content=[t]
        else:
            # Keep the title with the header and first row, not the entire BOQ.
            # Keeping a whole multirow table caused avoidable blank page remainders.
            t.wrap(self.w,100000)
            title_h=title.wrap(self.w,100000)[1]
            minimum=title_h+title.getSpaceBefore()+title.getSpaceAfter()+sum(t._rowHeights[:2])+2
            content=[CondPageBreak(minimum),title,t]
        return content+([self.P(b['note'],'note')] if b.get('note') else [])
    def total_box(self):
        j=self.job
        total_amount=self.P(fmt(j['expected_total']),'sub',fontSize=14,leading=17,alignment=TA_RIGHT) if self.software else self.P(fmt(j['expected_total']),'sub',alignment=TA_RIGHT)
        data=[[self.P('TOTAL CONTRACT PRICE','sub'),total_amount],
              [self.P(j['tax_treatment'].upper(),'label'),self.P(j['amount_words'],'cell',alignment=TA_RIGHT,textColor=self.c('muted'))]]
        return self.table(data,[.34,.66],False,[('NOSPLIT',(0,0),(-1,-1)),('BACKGROUND',(0,0),(-1,-1),self.c('gold')),('BOX',(0,0),(-1,-1),.6,colors.HexColor('#E8D79F')),('INNERGRID',(0,0),(-1,-1),0,self.c('gold'))])
    def lavi_front_cards(self):
        """Balanced two-card client/quotation summary for the LAVI first page."""
        j=self.job;cl=j['client'];p=self.p
        gap=p.get('front_card_gap',12.0)
        card_w=(self.w-gap)/2
        inner=card_w-2*p.get('front_card_padding',9.0)
        key_w=p.get('front_detail_label_width',72.0)
        val_w=inner-key_w
        left_rows=[[self.P('PREPARED FOR','label'),''],
                   [self.P('Client','meta',fontName=self.bold,textColor=self.c('muted')),self.P('<b>'+escape(cl['name'])+'</b>','meta')],
                   [self.P('Address','meta',fontName=self.bold,textColor=self.c('muted')),self.P(escape(cl['address'] or cl['location']),'meta')],
                   [self.P('Attention','meta',fontName=self.bold,textColor=self.c('muted')),self.P(escape(cl['attention']),'meta')],
                   [self.P('Role','meta',fontName=self.bold,textColor=self.c('muted')),self.P(escape(cl['role']),'meta')],
                   [self.P('Project Location','meta',fontName=self.bold,textColor=self.c('muted')),self.P(escape(cl['location']),'meta')]]
        left=Table(left_rows,colWidths=[key_w,val_w],hAlign='LEFT')
        left.setStyle(TableStyle([('SPAN',(0,0),(1,0)),('GRID',(0,0),(-1,-1),0,colors.white),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),1.8),('BOTTOMPADDING',(0,0),(-1,-1),1.8),('LINEBELOW',(0,0),(-1,0),.75,self.c('accent')),('BOTTOMPADDING',(0,0),(-1,0),5.5),('TOPPADDING',(0,1),(-1,1),6.5),('VALIGN',(0,0),(-1,-1),'TOP')]))
        detail_rows=[[self.P('QUOTE DETAILS','label'),''],
                     [self.P('Quotation No.','meta',fontName=self.bold,textColor=self.c('muted')),self.P(escape(j['quote_no']),'meta')],
                     [self.P('Date','meta',fontName=self.bold,textColor=self.c('muted')),self.P(escape(j['date']),'meta')],
                     [self.P('Validity','meta',fontName=self.bold,textColor=self.c('muted')),self.P(f'{j["validity_days"]} calendar days','meta')],
                     [self.P('Pricing','meta',fontName=self.bold,textColor=self.c('muted')),self.P(escape(j['tax_treatment']),'meta')]]
        right=Table(detail_rows,colWidths=[key_w,val_w],hAlign='LEFT')
        right.setStyle(TableStyle([('SPAN',(0,0),(1,0)),('GRID',(0,0),(-1,-1),0,colors.white),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),1.8),('BOTTOMPADDING',(0,0),(-1,-1),1.8),('LINEBELOW',(0,0),(-1,0),.75,self.c('accent')),('BOTTOMPADDING',(0,0),(-1,0),5.5),('TOPPADDING',(0,1),(-1,1),6.5),('VALIGN',(0,0),(-1,-1),'TOP')]))
        outer=Table([[left,'',right]],colWidths=[card_w,gap,card_w],hAlign='LEFT')
        pad=p.get('front_card_padding',9.0)
        outer.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),('BACKGROUND',(0,0),(0,0),self.c('tint')),('BACKGROUND',(2,0),(2,0),self.c('tint2')),('BOX',(0,0),(0,0),.45,self.c('border')),('BOX',(2,0),(2,0),.45,self.c('border')),('LINEABOVE',(0,0),(0,0),1.15,self.c('accent')),('LINEABOVE',(2,0),(2,0),1.15,self.c('accent')),('LEFTPADDING',(0,0),(0,0),pad),('RIGHTPADDING',(0,0),(0,0),pad),('TOPPADDING',(0,0),(0,0),pad),('BOTTOMPADDING',(0,0),(0,0),pad),('LEFTPADDING',(2,0),(2,0),pad),('RIGHTPADDING',(2,0),(2,0),pad),('TOPPADDING',(2,0),(2,0),pad),('BOTTOMPADDING',(2,0),(2,0),pad)]))
        outer.spaceAfter=p.get('front_card_space_after',10.0)
        return outer
    def front(self):
        j,p=self.job,self.p
        eyebrow=self.P('FORMAL QUOTATION','label') if not self.software else self.P('FORMAL QUOTATION','label',fontSize=10,leading=13)
        title=self.P(j['title'],'title')
        subtitle=self.P(j.get('subtitle','Budgetary Technical and Financial Proposal'),'meta',textColor=self.c('muted'),fontSize=11,leading=14) if self.software else self.P(j.get('subtitle','Budgetary Technical and Financial Proposal'),'meta',textColor=self.c('muted'))
        if self.software:
            titlebox=Table([[eyebrow],[title],[subtitle]],colWidths=[self.w],hAlign='LEFT')
            titlebox.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),self.c('light')),('LINEABOVE',(0,0),(-1,0),.9,self.c('accent')),('LINEBELOW',(0,-1),(-1,-1),.5,self.c('dark')),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
            out=[titlebox,Spacer(1,8)]
        else:out=[eyebrow,Spacer(1,3),title,Spacer(1,3),subtitle,Spacer(1,7)]
        cl=j['client'];tax=j['tax_treatment'];valid=f'{j["validity_days"]} calendar days'
        if self.software:
            data=[[self.P('PREPARED FOR','label'),self.P('QUOTE DETAILS','label')],
                  [self.P(f'<b>{escape(cl["name"])}</b><br/>Attention: {escape(cl["attention"])}<br/>{escape(cl["role"])}','meta'),self.P(f'<b>Date:</b> {escape(j["date"])}<br/><b>Quotation No.:</b> {escape(j["quote_no"])}<br/><b>Pricing:</b> {tax}','meta')],
                  [self.P('PROJECT LOCATION','label'),self.P('VALIDITY','label')],
                  [self.P(escape(cl['location']),'meta'),self.P(valid+' from quotation date','meta')]]
            widths=[.55,.45]
        else:
            data=None;widths=None
        if self.software:
            out += [self.table(data,widths,False,[('BACKGROUND',(0,0),(0,-1),self.c('tint')),('BACKGROUND',(1,0),(1,-1),self.c('tint2'))]),Spacer(1,8),self.P(j['salutation'])]
        else:
            out += [self.lavi_front_cards(),self.P(j['salutation'])]
        out += [self.P(s) for s in j.get('introduction',[])]
        if j.get('metrics'):
            metrics=[self.P('<b>'+escape(x[0])+'</b><br/>'+escape(x[1]),'cell',alignment=TA_CENTER) for x in j['metrics']]
            out += [self.table([metrics],[1/len(metrics)]*len(metrics))]
        out.append(self.heading(p['summary_label']))
        groups,_=totals(j)
        data=[[self.P(x,'head') for x in (['SECTION','DESCRIPTION','AMOUNT'] if self.software else ['PROJECT COMPONENT','AMOUNT'])]]
        for name,amount in groups:
            if self.software:data.append([self.P(name.split('.')[0],'cell',alignment=TA_CENTER),self.P(name.split('. ',1)[-1],'cell'),self.P(fmt(str(amount)),'cell',alignment=TA_RIGHT)])
            else:data.append([self.P(name.split('. ',1)[-1],'cell'),self.P(fmt(str(amount)),'cell',alignment=TA_RIGHT)])
        for a in j.get('adjustments',[]):
            data.append(([self.P('','cell')] if self.software else [])+[self.P(a['label'],'cell'),self.P(fmt(a['amount']),'cell',alignment=TA_RIGHT)])
        label='TOTAL CONTRACT PRICE - '+tax.upper()
        data.append(([self.P(label,'cell',fontName=self.bold),'',self.P(fmt(j['expected_total']),'cell',fontName=self.bold,alignment=TA_RIGHT)] if self.software else [self.P(label,'cell',fontName=self.bold),self.P(fmt(j['expected_total']),'cell',fontName=self.bold,alignment=TA_RIGHT)]))
        cmds=[('BACKGROUND',(0,-1),(-1,-1),self.c('gold')),('NOSPLIT',(0,-2),(-1,-1))]
        if self.software:cmds.append(('SPAN',(0,-1),(1,-1)))
        out += [self.table(data,[.088,.647,.265] if self.software else [.745,.255],True,cmds),self.P('Amount in words: '+j['amount_words'],'note')]
        if j.get('boundary'):out += [self.table([[self.P('<b>PROJECT BOUNDARY</b><br/>'+j['boundary'],'note')]], [1],False,[('BACKGROUND',(0,0),(-1,-1),self.c('tint'))])]
        out += [self.P(x) for x in j.get('front_notes',[])]
        # Preserve executive-summary boundaries unless continuous flow is requested.
        if j.get('front_page_break', True):
            out.append(PageBreak())
        return out
    def render(self,path):
        p=self.p;W,H=p['page'];m=p['margin'];out=Path(path);out.parent.mkdir(parents=True,exist_ok=True)
        first_top,later_top,bottom=self.page_geometry()
        doc=BaseDocTemplate(str(out),pagesize=(W,H),title=self.job['title']+' | '+self.job['quote_no'],author=p['company'],allowSplitting=True)
        frames=[Frame(m,bottom,self.w,H-bottom-top,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0,id=str(i)) for i,top in enumerate([first_top,later_top])]
        doc.addPageTemplates([PageTemplate(id='first',frames=[frames[0]],onPage=lambda c,d:self.header(c,d,True)),PageTemplate(id='later',frames=[frames[1]],onPage=self.header)])
        story=[NextPageTemplate('later')]+self.front()
        for bi,b in enumerate(self.job['blocks']):
            k=b['type']
            if k=='heading':
                heading=self.heading(b['text'])
                following=self.job['blocks'][bi+1] if bi+1<len(self.job['blocks']) else {}
                if following.get('type')=='table':
                    table=self.generic_table(following);table.wrap(self.w,100000)
                    rows_to_keep=len(table._rowHeights) if (not self.software and len(following.get('rows',[]))<=4) else min(2,len(table._rowHeights))
                    minimum=heading.wrap(self.w,100000)[1]+heading.spaceBefore+heading.spaceAfter+sum(table._rowHeights[:rows_to_keep])+2
                    story.append(CondPageBreak(minimum));heading.keepWithNext=0
                story.append(heading)
            elif k in ('paragraph','note'):story.append(self.P(b['text'],'note' if k=='note' else 'body'))
            elif k=='boq':story.extend(self.boq(b))
            elif k=='diagram':story.extend([Spacer(1,6),Diagram(b,p,self.w,self.font,self.bold),Spacer(1,9)])
            elif k=='total':story.append(self.total_box())
            elif k=='page_break':story.append(PageBreak())
            elif k=='callout':story.append(self.table([[self.P(b['text'])]],[1],False,[('BACKGROUND',(0,0),(-1,-1),self.c('tint'))]))
            elif k=='list':
                numbered=b.get('numbered',False)
                if not self.software:
                    for i,txt in enumerate(b['items'],b.get('start',1)):
                        story.append(self.lavi_list_item(f'{i}.' if numbered else '\u2022',txt,numbered))
                else:
                    indent=p['number_indent'] if numbered else p['bullet_indent']
                    for i,txt in enumerate(b['items'],b.get('start',1)):
                        st=ParagraphStyle('list',parent=self.styles['body'],leftIndent=indent,firstLineIndent=0,bulletIndent=indent-5 if numbered else 2,
                            bulletAnchor='end' if numbered else 'start',bulletFontName=self.bold if numbered else self.font,bulletFontSize=p['body'][0],spaceAfter=4)
                        story.append(Paragraph(txt,st,bulletText=f'{i}.' if numbered else '\u2022'))
            elif k=='table':
                story.append(self.generic_table(b))
        signature_mode=self.job.get('signature_mode',p.get('default_signature_mode','prepared_only'))
        if signature_mode == 'two_column_prepared_conforme':
            story.append(TwoColumnSignoff(self))
        else:
            signature=self.table([[self.P('PREPARED BY','label')],[self.P('<b>'+escape(self.job['prepared_by']['name'])+'</b><br/>'+escape(self.job['prepared_by']['role'])+'<br/>'+p['display_name'])]],[1],False,[('GRID',(0,0),(-1,-1),0,colors.white),('BACKGROUND',(0,0),(-1,-1),colors.white),('LINEABOVE',(0,0),(-1,0),.65,self.c('accent')),('LEFTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,1),(-1,1),20)])
            story.append(signature)
        doc.build(story,canvasmaker=PageCanvas)
        return out

def render(job,output):return Builder(job).render(output)
