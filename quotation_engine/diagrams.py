"""Measured, readable vector diagrams with profile-defined readable text and gap-only connectors."""
from xml.sax.saxutils import escape
from reportlab.platypus import Flowable, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor

class Diagram(Flowable):
    def __init__(self, spec, profile, width, regular, bold):
        super().__init__()
        self.spec,self.p,self.width=spec,profile,width
        self.regular,self.bold=regular,bold
        self.gap=18.0;self.col_gap=8.0;self.geometry=[];self.rows=[];self.connectors=[]
        size=profile.get('diagram_font_size',profile.get('minimum_font_size',10))
        def para(text,is_bold=True,align=TA_CENTER,ink='dark'):
            return Paragraph(escape(str(text)),ParagraphStyle('diagram',fontName=bold if is_bold else regular,
                fontSize=size,leading=13 if size>=10 else 11.4,alignment=align,textColor=HexColor(profile.get(ink,ink)),spaceAfter=0))
        self.caption=para(spec.get('caption','LOGICAL SYSTEM ARCHITECTURE'),True,TA_LEFT,'muted')
        _,self.caption_h=self.caption.wrap(width,2000)
        y=self.caption_h+12
        for row in spec['rows']:
            n=len(row['nodes']);cw=(width-(n-1)*self.col_gap)/n
            label=para(row['label'],True,TA_LEFT,'muted') if row.get('label') else None
            label_h=label.wrap(width-20,2000)[1] if label else 0
            measured=[]
            for node in row['nodes']:
                inner=cw-(32 if row.get('label') else 20)
                pars=[para(node['title'],ink='heading_color' if row.get('fill')=='tint' else 'dark')]
                pars += [para(t,False,ink='muted') for t in node.get('subtitle',[])]
                heights=[p.wrap(inner,2000)[1] for p in pars]
                measured.append((pars,heights,inner))
            text_h=max(sum(hs)+3*(len(hs)-1) for _,hs,_ in measured)
            node_h=text_h+20
            h=node_h+(label_h+16 if label else 0)
            self.geometry.append((y,h));self.rows.append((row,label,label_h,measured,node_h,cw))
            y += h+self.gap
        self.height=y-self.gap+3
        if self.height > profile['page'][1]-profile.get('bottom',66)-100:
            raise ValueError('Diagram exceeds a readable page. Split it into semantic diagrams; never shrink text.')

    def draw(self):
        c,p,w,H=self.canv,self.p,self.width,self.height
        c.saveState()
        def color(k):return HexColor(p.get(k,k))
        def box(x,top,width,height,fill,border='border'):
            c.setFillColor(color(fill));c.setStrokeColor(color(border));c.setLineWidth(.7)
            c.roundRect(x,H-top-height,width,height,5,fill=1,stroke=1)
        def line(x1,y1,x2,y2,low,high):
            assert low<y1<high and low<y2<high,'Connector crosses a row.'
            self.connectors.append((x1,y1,x2,y2,low,high))
            c.setStrokeColor(color('heading_color'));c.setLineWidth(.85)
            c.line(x1,H-y1,x2,H-y2)
        def arrow(x,y1,tip,low,high):
            line(x,y1,x,tip,low,high)
            line(x-2.6,tip-3.4,x,tip,low,high);line(x+2.6,tip-3.4,x,tip,low,high)
        self.caption.drawOn(c,0,H-self.caption_h)
        centers=[]
        for idx,((top,h),(row,label,label_h,measured,node_h,cw)) in enumerate(zip(self.geometry,self.rows)):
            xs=[i*(cw+self.col_gap)+cw/2 for i in range(len(measured))];centers.append(xs)
            if label:
                box(0,top,w,h,row.get('fill','tint2'))
                label.drawOn(c,10,H-top-8-label_h)
            nt=top+(label_h+16 if label else 0)
            for i,((pars,heights,inner),node) in enumerate(zip(measured,row['nodes'])):
                x=i*(cw+self.col_gap)
                if not label:box(x,nt,cw,node_h,row.get('fill','tint'))
                elif node.get('outline'):box(x+8,nt,cw-16,node_h,'#FFFFFF','table_header')
                th=sum(heights)+3*(len(heights)-1);y=nt+(node_h-th)/2
                for para,ph in zip(pars,heights):
                    para.drawOn(c,x+(cw-inner)/2,H-y-ph);y+=ph+3
            if idx:
                upper_t,upper_h=self.geometry[idx-1];low=upper_t+upper_h;high=top
                prev,curr=centers[idx-1],xs;mid=low+6
                if len(prev)>1:
                    for cx in prev:line(cx,low+1,cx,mid,low,high)
                    line(prev[0],mid,prev[-1],mid,low,high)
                else:line(w/2,low+1,w/2,mid,low,high)
                if len(curr)>1:
                    line(curr[0],mid,curr[-1],mid,low,high)
                    for cx in curr:arrow(cx,mid,high-1.5,low,high)
                else:arrow(w/2,mid,high-1.5,low,high)
        c.restoreState()
