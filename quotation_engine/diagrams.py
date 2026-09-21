"""Deterministic vector diagrams with computed row positions and gap-only connectors."""
from reportlab.platypus import Flowable
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth

class Diagram(Flowable):
    def __init__(self, spec, profile, width, regular, bold):
        super().__init__()
        self.spec, self.p, self.width = spec, profile, width
        self.regular, self.bold = regular, bold
        self.gap = 18.0
        self.col_gap = 8.0
        self.geometry = []
        y = 23.0  # Caption gets its own lane and clearance.
        for row in spec['rows']:
            count = max(1 + len(n.get('subtitle', [])) for n in row['nodes'])
            h = max(26.0, 13.0 + count * 10.0 + (13.0 if row.get('label') else 0))
            self.geometry.append((y, h))
            y += h + self.gap
        self.height = y - self.gap + 3.0
        self.connectors = []

    def draw(self):
        c, p, w, H = self.canv, self.p, self.width, self.height
        c.saveState()
        def color(k): return HexColor(p.get(k, k))
        def text(s, cx, top, size, bold=True, ink='dark', available=None):
            font = self.bold if bold else self.regular
            tw = stringWidth(s, font, size)
            if available is not None and tw > available - 10:
                raise ValueError(f'Diagram label does not fit; split the label, do not shrink fonts: {s}')
            c.setFillColor(color(ink)); c.setFont(font, size)
            c.drawCentredString(cx, H-top, s)
        def box(x, top, width, height, fill, border='border'):
            c.setFillColor(color(fill)); c.setStrokeColor(color(border)); c.setLineWidth(.7)
            c.roundRect(x, H-top-height, width, height, 5, fill=1, stroke=1)
        def line(x1,y1,x2,y2,low,high):
            assert low < y1 < high and low < y2 < high, 'Connector crosses a row.'
            self.connectors.append((x1,y1,x2,y2,low,high))
            c.setStrokeColor(color('heading_color')); c.setLineWidth(.85)
            c.line(x1,H-y1,x2,H-y2)
        def arrow(x,y1,tip,low,high):
            line(x,y1,x,tip,low,high)
            line(x-2.6,tip-3.4,x,tip,low,high)
            line(x+2.6,tip-3.4,x,tip,low,high)
        c.setFont(self.bold,6.3); c.setFillColor(color('muted'))
        c.drawString(0,H-8,self.spec.get('caption','LOGICAL SYSTEM ARCHITECTURE'))
        centers=[]
        for idx,(row,(top,h)) in enumerate(zip(self.spec['rows'],self.geometry)):
            nodes=row['nodes']; n=len(nodes); cw=(w-(n-1)*self.col_gap)/n
            xs=[i*(cw+self.col_gap)+cw/2 for i in range(n)]; centers.append(xs)
            if row.get('label'):
                box(0,top,w,h,row.get('fill','tint2'))
                c.setFont(self.bold,6.1);c.setFillColor(color('muted'))
                c.drawString(10,H-top-10,row['label'])
            for i,node in enumerate(nodes):
                x=i*(cw+self.col_gap); nt=top+(16 if row.get('label') else 0); nh=h-(20 if row.get('label') else 0)
                if not row.get('label'):
                    box(x,nt,cw,nh,row.get('fill','tint'))
                elif node.get('outline'):
                    box(x+8,nt,cw-16,nh,'#FFFFFF','table_header')
                lines=[node['title']]+node.get('subtitle',[])
                size=6.3 if len(node['title'])>60 else 6.7
                for j,s in enumerate(lines):
                    baseline=nt+(nh-(len(lines)-1)*10)/2+2.3+j*10
                    text(s,xs[i],baseline,size if j==0 else 5.9,j==0,
                         'heading_color' if row.get('fill')=='tint' and j==0 else ('dark' if j==0 else 'muted'),cw-(16 if node.get('outline') else 0))
            if idx:
                upper_t,upper_h=self.geometry[idx-1]; low=upper_t+upper_h; high=top
                prev=centers[idx-1]; curr=xs
                # Merge multiple source cards; split only inside the next inter-row gap.
                mid=low+6
                if len(prev)>1:
                    for cx in prev:line(cx,low+1,cx,mid,low,high)
                    line(prev[0],mid,prev[-1],mid,low,high)
                else:line(w/2,low+1,w/2,mid,low,high)
                if len(curr)>1:
                    line(curr[0],mid,curr[-1],mid,low,high)
                    for cx in curr:arrow(cx,mid,high-1.5,low,high)
                else:arrow(w/2,mid,high-1.5,low,high)
        c.restoreState()
