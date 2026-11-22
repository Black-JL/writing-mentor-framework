#!/usr/bin/env python3
"""
Build a folder of MADE-UP sample files for testing. No real writer's work is used.

    python tests/make_samples.py <folder>

Creates:
  assignment.docx, rubric.pdf
  submissions/            three made-up writers, export-style names
    rivera_1001_5001_report.docx    paragraphs split across runs, accents, a pasted note
    rivera_1001_5002_model.xlsx     two sheets, formulas, copied-down formulas, a chart
    rivera_1001_4999_model.xlsx     an older version of the same workbook
    okafor_1002_5003_essay.pdf      text PDF
    okafor_1002_5004_old.doc        not a real .doc (must be reported, not crash)
    okafor_1002_5005_old.xls        not a real .xls (must be reported, not crash)
    lindqvist_LATE_1003_5006_broken.xlsx   damaged file (must be reported, not crash)
    lindqvist_LATE_1003_5007_notes.docx
  rounds/round1/rivera_report.docx, rounds/round2/rivera_report.docx
"""
import sys
import zipfile
from pathlib import Path

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def docx(path, paragraphs):
    """paragraphs: list of lists of run texts."""
    body = ''.join(
        '<w:p>' + ''.join(f'<w:r><w:t xml:space="preserve">{r}</w:t></w:r>' for r in runs) + '</w:p>'
        for runs in paragraphs)
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('[Content_Types].xml',
                   '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                   '</Types>')
        z.writestr('_rels/.rels',
                   '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                   '</Relationships>')
        z.writestr('word/document.xml',
                   f'<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="{W}"><w:body>{body}</w:body></w:document>')


def xlsx(path):
    """Two sheets. Calc!C2:C4 is one formula copied down (a 'shared' formula). One bar chart."""
    S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    P = 'http://schemas.openxmlformats.org/package/2006/relationships'
    CT = 'http://schemas.openxmlformats.org/package/2006/content-types'

    def cell(ref, value=None, formula=None, text=None, extra=''):
        if text is not None:
            return f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>'
        f = f'<f{extra}>{formula}</f>' if formula else (f'<f{extra}/>' if extra else '')
        v = f'<v>{value}</v>' if value is not None else ''
        return f'<c r="{ref}">{f}{v}</c>'

    data = ('<row r="1">' + cell('A1', text='Year') + cell('B1', text='Nominal GDP') + cell('C1', text='Price index') + '</row>'
            '<row r="2">' + cell('A2', 2021) + cell('B2', 100) + cell('C2', 1.00) + '</row>'
            '<row r="3">' + cell('A3', 2022) + cell('B3', 110) + cell('C3', 1.05) + '</row>'
            '<row r="4">' + cell('A4', 2023) + cell('B4', 121) + cell('C4', 1.10) + '</row>')
    calc = ('<row r="1">' + cell('A1', text='Year') + cell('C1', text='Real GDP (São Paulo método)') + '</row>'
            '<row r="2">' + cell('A2', 2021, 'Data!A2') + cell('C2', 100, 'Data!B2/Data!C2', extra=' t="shared" ref="C2:C4" si="0"') + '</row>'
            '<row r="3">' + cell('A3', 2022, 'Data!A3') + cell('C3', 104.76, extra=' t="shared" si="0"') + '</row>'
            '<row r="4">' + cell('A4', 2023, 'Data!A4') + cell('C4', 110, extra=' t="shared" si="0"') + '</row>'
            '<row r="6">' + cell('A6', text='Growth') + cell('C6', 0.1, '$C$4/$C$2-1') + '</row>')

    def sheet(rows, drawing=False):
        d = f'<drawing r:id="rId1"/>' if drawing else ''
        return f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="{S}" xmlns:r="{R}"><sheetData>{rows}</sheetData>{d}</worksheet>'

    chart = ('<?xml version="1.0" encoding="UTF-8"?>'
             '<c:chartSpace xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
             'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><c:chart>'
             '<c:title><c:tx><c:rich><a:p><a:r><a:t>Real GDP by year</a:t></a:r></a:p></c:rich></c:tx></c:title>'
             '<c:plotArea><c:barChart><c:barDir val="col"/><c:ser><c:idx val="0"/><c:order val="0"/>'
             '<c:cat><c:numRef><c:f>Calc!$A$2:$A$4</c:f></c:numRef></c:cat>'
             '<c:val><c:numRef><c:f>Data!$B$2:$B$4</c:f></c:numRef></c:val>'
             '</c:ser><c:axId val="1"/><c:axId val="2"/></c:barChart>'
             '<c:catAx><c:axId val="1"/><c:crossAx val="2"/></c:catAx><c:valAx><c:axId val="2"/><c:crossAx val="1"/></c:valAx>'
             '</c:plotArea></c:chart></c:chartSpace>')
    drawing = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<xdr:wsDr xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing" '
               'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
               'xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:r="' + R + '">'
               '<xdr:twoCellAnchor><xdr:from><xdr:col>4</xdr:col><xdr:colOff>0</xdr:colOff><xdr:row>1</xdr:row><xdr:rowOff>0</xdr:rowOff></xdr:from>'
               '<xdr:to><xdr:col>10</xdr:col><xdr:colOff>0</xdr:colOff><xdr:row>15</xdr:row><xdr:rowOff>0</xdr:rowOff></xdr:to>'
               '<xdr:graphicFrame macro=""><xdr:nvGraphicFramePr><xdr:cNvPr id="2" name="Chart 1"/><xdr:cNvGraphicFramePr/></xdr:nvGraphicFramePr>'
               '<xdr:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/></xdr:xfrm>'
               '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/chart">'
               '<c:chart r:id="rId1"/></a:graphicData></a:graphic></xdr:graphicFrame><xdr:clientData/></xdr:twoCellAnchor></xdr:wsDr>')

    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('[Content_Types].xml',
                   f'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="{CT}">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                   '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                   '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                   '<Override PartName="/xl/drawings/drawing1.xml" ContentType="application/vnd.openxmlformats-officedocument.drawing+xml"/>'
                   '<Override PartName="/xl/charts/chart1.xml" ContentType="application/vnd.openxmlformats-officedocument.drawingml.chart+xml"/>'
                   '</Types>')
        z.writestr('_rels/.rels',
                   f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{P}">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                   '</Relationships>')
        # Sheet order in the workbook is Data, Calc — but their files are numbered the other
        # way round, to catch code that assumes sheet1.xml is the first sheet.
        z.writestr('xl/workbook.xml',
                   f'<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="{S}" xmlns:r="{R}"><sheets>'
                   '<sheet name="Data" sheetId="1" r:id="rId2"/><sheet name="Calc" sheetId="2" r:id="rId1"/>'
                   '</sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels',
                   f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{P}">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                   '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
                   '</Relationships>')
        z.writestr('xl/worksheets/sheet1.xml', sheet(calc, drawing=True))
        z.writestr('xl/worksheets/sheet2.xml', sheet(data))
        z.writestr('xl/worksheets/_rels/sheet1.xml.rels',
                   f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{P}">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing" Target="../drawings/drawing1.xml"/>'
                   '</Relationships>')
        z.writestr('xl/drawings/drawing1.xml', drawing)
        z.writestr('xl/drawings/_rels/drawing1.xml.rels',
                   f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{P}">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart" Target="../charts/chart1.xml"/>'
                   '</Relationships>')
        z.writestr('xl/charts/chart1.xml', chart)


def pdf(path, lines):
    """A minimal one-page text PDF."""
    text = ' '.join(f'({ln}) Tj T*' for ln in lines)
    stream = f'BT /F1 11 Tf 14 TL 72 720 Td {text} ET'.encode('latin-1')
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>',
            b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>',
            b'<< /Length ' + str(len(stream)).encode() + b' >>\nstream\n' + stream + b'\nendstream',
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    out = bytearray(b'%PDF-1.4\n')
    offsets = []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += f'{i} 0 obj\n'.encode() + body + b'\nendobj\n'
    xref = len(out)
    out += f'xref\n0 {len(objs) + 1}\n0000000000 65535 f \n'.encode()
    for off in offsets:
        out += f'{off:010d} 00000 n \n'.encode()
    out += f'trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
    Path(path).write_bytes(out)


ESSAY = [
    'Inflation and real output, 2021 to 2023.',
    'This essay compares nominal and real GDP for a made-up economy.',
    'Nominal GDP rose from 100 to 121 over the period, an increase of 21 percent.',
    'After adjusting for prices, real GDP rose 10 percent, from 100 to 110.',
    'The gap between the two numbers is the effect of rising prices.',
    'The analysis uses the price index in the Data sheet as the deflator.',
    'A longer series would show whether this growth rate is typical.',
]


def build(root):
    root = Path(root)
    sub = root / 'submissions'
    sub.mkdir(parents=True, exist_ok=True)

    docx(root / 'assignment.docx', [
        ['Assignment: Real versus nominal growth'],
        ['Hand in a short report (Word or PDF) and the Excel workbook with your calculations.'],
        ['Compare nominal and real GDP for 2021–2023 and explain the difference.'],
    ])
    pdf(root / 'rubric.pdf', [
        'Rubric (20 points)',
        'Data and calculations (10): formulas correct, real vs nominal handled.',
        'Argument (5): claims match the numbers.',
        'Writing (5): clear, concrete, active verbs.',
    ])

    docx(sub / 'rivera_1001_5001_report.docx', [
        ['Real GDP ', 'grew ', '10 percent between 2021 and 2023.'],
        ['Nominal GDP grew faster — 21 percent — because prices rose. ', 'Müller’s café index agrees.'],
        ['The chart in my workbook shows real GDP by year.'],
    ])
    xlsx(sub / 'rivera_1001_5002_model.xlsx')
    xlsx(sub / 'rivera_1001_4999_model.xlsx')
    pdf(sub / 'okafor_1002_5003_essay.pdf', ESSAY)
    (sub / 'okafor_1002_5004_old.doc').write_bytes(b'not really a word file')
    (sub / 'okafor_1002_5005_old.xls').write_bytes(b'not really an excel file')
    (sub / 'lindqvist_LATE_1003_5006_broken.xlsx').write_bytes(b'PK\x03\x04 damaged')
    docx(sub / 'lindqvist_LATE_1003_5007_notes.docx', [
        ['Growth was ', 'significant', '.'],
        ['Prices went up a lot so the economy is doing well.'],
    ])

    for rnd, extra in (('round1', 'Real GDP grew a lot.'),
                       ('round2', 'Real GDP grew 10 percent, from 100 to 110, after deflating by the price index.')):
        d = root / 'rounds' / rnd
        d.mkdir(parents=True, exist_ok=True)
        docx(d / 'rivera_report.docx', [[extra]])
    return root


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('usage: make_samples.py <folder>')
    print(build(sys.argv[1]))
