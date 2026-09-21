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
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle, Spacer, PageBreak, NextPageTemplate, Flowable
from PIL import Image
from .validation import PROFILES, ROOT, validate, totals, fmt, money
from .diagrams import Diagram

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
            self.setFont(self._page_font,6.1);self.setFillColor(colors.HexColor('#65717E'))
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
    def __init__(self,paragraph,width,color):
        super().__init__();self.paragraph=paragraph;self.width=width;self.color=color
        self.spaceBefore=10;self.spaceAfter=8
    def wrap(self,aW,aH):
        _,h=self.paragraph.wrap(self.width,aH);self.height=h+5;return self.width,self.height
    def draw(self):
        self.paragraph.drawOn(self.canv,0,5)
        self.canv.setStrokeColor(self.color);self.canv.setLineWidth(.65);self.canv.line(0,0,self.width,0)

class Builder:
    def __init__(self,job):
        validate(job);self.job=job;self.p=PROFILES[job['brand']];p=self.p
        self.font,self.bold,self.italic=register_fonts(p)
        self.w=p['page'][0]-2*p['margin'];self.software=job['brand']=='lifes-awesome'
        self.styles={}
        for name,key in [('body','body'),('note','note'),('cell','table'),('heading','heading'),('sub','subheading'),('title','title')]:
            size,leading=p[key]
            self.styles[name]=ParagraphStyle(name,fontName=self.bold if name in ('heading','sub','title') else self.font,fontSize=size,leading=leading,
                textColor=self.c('heading_color' if name=='heading' else ('dark' if name in ('sub','title') else 'ink')),
                alignment=TA_JUSTIFY if name in ('body','note') else TA_LEFT,spaceAfter=6 if name in ('body','note') else 0)
        self.styles['head']=ParagraphStyle('head',fontName=self.bold,fontSize=6.8 if self.software else 6.3,leading=9 if self.software else 7.2,textColor=colors.white,alignment=TA_CENTER)
        self.styles['meta']=ParagraphStyle('meta',fontName=self.font,fontSize=8 if self.software else 7.3,leading=11 if self.software else 9.4,textColor=self.c('ink'))
        self.styles['label']=ParagraphStyle('label',fontName=self.bold,fontSize=7.1 if self.software else 6.5,leading=9,textColor=self.c('heading_color'))
    def c(self,key):return colors.HexColor(self.p.get(key,key))
    def P(self,text,style='body',**kw):
        st=self.styles[style]
        if kw:st=ParagraphStyle(style+'-local',parent=st,**kw)
        return Paragraph(str(text),st)
    def header(self,c,doc,first=False):
        p,j=self.p,self.job;W,H=p['page'];m=p['margin'];r=W-m
        c._page_font=self.font;c._page_margin=m;c._page_footer_y=19 if self.software else 22.1
        c.saveState();c.setFillColor(self.c('accent'));c.rect(m,H-(14 if self.software else 29.76 if first else 26.93),self.w,1.25 if self.software else 3.54 if first else 2.55,fill=1,stroke=0)
        if first:
            logo=ROOT/p['logo'];lw=270 if self.software else 104.88
            with Image.open(logo) as im:lh=lw*im.height/im.width
            x=(W-lw)/2 if self.software else m;y=H-22-lh if self.software else H-42.52-lh
            c.drawImage(str(logo),x,y,width=lw,height=lh,mask='auto')
            if self.software:
                c.setFont(self.font,6.5);c.setFillColor(self.c('muted'))
                for k,line in enumerate(p['contact']):c.drawCentredString(W/2,H-84-k*10,line)
                rule=106
            else:
                c.setFont(self.bold,7.2);c.setFillColor(self.c('dark'));c.drawRightString(r,H-49.61,p['company'])
                c.setFont(self.font,6.4);c.setFillColor(self.c('muted'))
                for k,line in enumerate(p['contact']):c.drawRightString(r,H-60.95-k*9.354,line)
                rule=96.38
        else:
            c.setFont(self.bold,6.9 if self.software else 7.6);c.setFillColor(self.c('dark'));c.drawString(m,H-(29 if self.software else 44.79),p['company'])
            c.setFont(self.font,6.15 if self.software else 6.4);c.setFillColor(self.c('muted'))
            c.drawRightString(r,H-(29 if self.software else 44.79),j['quote_no']+'  |  FORMAL QUOTATION');rule=38 if self.software else 54.43
        c.setStrokeColor(self.c('border'));c.setLineWidth(.45);c.line(m,H-rule,r,H-rule)
        c.line(m,29 if self.software else 32.6,r,29 if self.software else 32.6)
        footer=p['company']+'  |  '+j['footer_label']
        size=5.75 if self.software else 6.2
        if pdfmetrics.stringWidth(footer,self.font,size)>self.w-65:
            raise ValueError('Footer label too long. Supply a concise approved footer_label.')
        c.setFillColor(self.c('muted'));c.setFont(self.font,size);c.drawString(m,19 if self.software else 22.1,footer);c.restoreState()
    def heading(self,text):return Heading(self.P(text,'heading'),self.w,self.c('accent'))
    def table(self,data,widths,header=False,style_extra=None):
        t=Table(data,colWidths=[self.w*x for x in widths],repeatRows=1 if header else 0,hAlign='LEFT',splitByRow=1)
        commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,self.c('border')),
            ('LEFTPADDING',(0,0),(-1,-1),6 if self.software else 4),('RIGHTPADDING',(0,0),(-1,-1),6 if self.software else 4),
            ('TOPPADDING',(0,0),(-1,-1),self.p['table_padding']),('BOTTOMPADDING',(0,0),(-1,-1),self.p['table_padding']),
            ('ROWBACKGROUNDS',(0,1 if header else 0),(-1,-1),[colors.white,self.c('light')])]
        if header:commands += [('BACKGROUND',(0,0),(-1,0),self.c('table_header')),('NOSPLIT',(0,0),(-1,1))]
        t.setStyle(TableStyle(commands+(style_extra or [])));t.spaceAfter=6;return t
    def boq(self,b):
        title=self.P(b['title'],'sub',keepWithNext=True,spaceBefore=6,spaceAfter=4)
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
        return ([t] if self.software else [title,t])+([self.P(b['note'],'note')] if b.get('note') else [])
    def total_box(self):
        j=self.job
        data=[[self.P('TOTAL CONTRACT PRICE','sub'),self.P(fmt(j['expected_total']),'sub',fontSize=14,leading=17,alignment=TA_RIGHT)],
              [self.P(j['tax_treatment'].upper(),'label'),self.P(j['amount_words'],'cell',alignment=TA_RIGHT,textColor=self.c('muted'))]]
        return self.table(data,[.34,.66],False,[('BACKGROUND',(0,0),(-1,-1),self.c('gold')),('BOX',(0,0),(-1,-1),.6,colors.HexColor('#E8D79F')),('INNERGRID',(0,0),(-1,-1),0,self.c('gold'))])
    def front(self):
        j,p=self.job,self.p
        eyebrow=self.P('FORMAL QUOTATION','label',fontSize=8.2,leading=10)
        title=self.P(j['title'],'title')
        subtitle=self.P(j.get('subtitle','Budgetary Technical and Financial Proposal'),'meta',textColor=self.c('muted'),fontSize=8.6 if self.software else 9,leading=12)
        if self.software:
            titlebox=Table([[eyebrow],[title],[subtitle]],colWidths=[self.w],hAlign='LEFT')
            titlebox.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),self.c('light')),('LINEABOVE',(0,0),(-1,0),.9,self.c('accent')),('LINEBELOW',(0,-1),(-1,-1),.5,self.c('dark')),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
            out=[titlebox,Spacer(1,8)]
        else:out=[eyebrow,Spacer(1,4),title,Spacer(1,4),subtitle,Spacer(1,8)]
        cl=j['client'];tax=j['tax_treatment'];valid=f'{j["validity_days"]} calendar days'
        if self.software:
            data=[[self.P('PREPARED FOR','label'),self.P('QUOTE DETAILS','label')],
                  [self.P(f'<b>{escape(cl["name"])}</b><br/>Attention: {escape(cl["attention"])}<br/>{escape(cl["role"])}','meta'),self.P(f'<b>Date:</b> {escape(j["date"])}<br/><b>Quotation No.:</b> {escape(j["quote_no"])}<br/><b>Pricing:</b> {tax}','meta')],
                  [self.P('PROJECT LOCATION','label'),self.P('VALIDITY','label')],
                  [self.P(escape(cl['location']),'meta'),self.P(valid+' from quotation date','meta')]]
            widths=[.55,.45]
        else:
            data=[[self.P('PREPARED FOR','label'),self.P('QUOTE DETAILS','label')],
                [self.P(escape(cl['name'])+'<br/>'+escape(cl['address']),'meta'),self.P(f'Quotation No. {escape(j["quote_no"])}<br/>Date: {escape(j["date"])}<br/>Validity: {valid}<br/>Pricing: {tax}','meta')],
                [self.P(f'Attention: {escape(cl["attention"])}<br/>{escape(cl["role"])}','meta'),self.P('Project Location: '+escape(cl['location']),'meta')]]
            widths=[.5,.5]
        out += [self.table(data,widths,False,[('BACKGROUND',(0,0),(0,-1),self.c('tint')),('BACKGROUND',(1,0),(1,-1),self.c('tint2'))]),Spacer(1,8),self.P(j['salutation'])]
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
        out.append(PageBreak())  # Approved executive-summary/front page boundary only.
        return out
    def render(self,path):
        p=self.p;W,H=p['page'];m=p['margin'];out=Path(path);out.parent.mkdir(parents=True,exist_ok=True)
        doc=BaseDocTemplate(str(out),pagesize=(W,H),title=self.job['title']+' | '+self.job['quote_no'],author=p['company'],allowSplitting=True)
        frames=[Frame(m,p['bottom'],self.w,H-p['bottom']-top,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0,id=str(i)) for i,top in enumerate([p['first_top'],p['later_top']])]
        doc.addPageTemplates([PageTemplate(id='first',frames=[frames[0]],onPage=lambda c,d:self.header(c,d,True)),PageTemplate(id='later',frames=[frames[1]],onPage=self.header)])
        story=[NextPageTemplate('later')]+self.front()
        for b in self.job['blocks']:
            k=b['type']
            if k=='heading':story.append(self.heading(b['text']))
            elif k in ('paragraph','note'):story.append(self.P(b['text'],'note' if k=='note' else 'body'))
            elif k=='boq':story.extend(self.boq(b))
            elif k=='diagram':story.extend([Spacer(1,6),Diagram(b,p,self.w,self.font,self.bold),Spacer(1,9)])
            elif k=='total':story.append(self.total_box())
            elif k=='page_break':story.append(PageBreak())
            elif k=='callout':story.append(self.table([[self.P(b['text'])]],[1],False,[('BACKGROUND',(0,0),(-1,-1),self.c('tint'))]))
            elif k=='list':
                numbered=b.get('numbered',False);indent=p['number_indent'] if numbered else p['bullet_indent']
                for i,txt in enumerate(b['items'],b.get('start',1)):
                    st=ParagraphStyle('list',parent=self.styles['body'],leftIndent=indent,firstLineIndent=0,bulletIndent=indent-5 if numbered else 2,
                        bulletAnchor='end' if numbered else 'start',bulletFontName=self.bold if numbered else self.font,bulletFontSize=p['body'][0],spaceAfter=4)
                    story.append(Paragraph(txt,st,bulletText=f'{i}.' if numbered else '\u2022'))
            elif k=='table':
                data=[[self.P(c,'head' if b.get('header') and ri==0 else 'cell',**({'fontName':self.bold} if ci==0 and not b.get('header') else {})) for ci,c in enumerate(row)] for ri,row in enumerate(b['rows'])]
                story.append(self.table(data,b['widths'],b.get('header',False)))
        signature=self.table([[self.P('PREPARED BY','label')],[self.P('<b>'+escape(self.job['prepared_by']['name'])+'</b><br/>'+escape(self.job['prepared_by']['role'])+'<br/>'+p['display_name'])]],[1],False,[('GRID',(0,0),(-1,-1),0,colors.white),('BACKGROUND',(0,0),(-1,-1),colors.white),('LINEABOVE',(0,0),(-1,0),.65,self.c('accent')),('LEFTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,1),(-1,1),20)])
        story.append(signature)
        doc.build(story,canvasmaker=PageCanvas)
        return out

def render(job,output):return Builder(job).render(output)
