from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def hello(c):
    # move the origin up and to the left
    c.translate(inch,inch)
    # define a large font
    c.setFont("Helvetica", 14)
    # choose some colors
    c.setStrokeColorRGB(0.2, 0.1, 0.3)
    c.setFillColorRGB(0.5, 0, 1)
    # draw some lines
    c.line(0,0, 0, 1.7 * inch)
    c.line(0, 0, 1 * inch, 0)
    # draw a rectangle
    c.rect(0.2 * inch, 0.2 * inch, 1 * inch, 1.5 * inch, fill=1)
    # make text go straight up
    c.rotate(90)
    # change color
    c.setFillColorRGB(0, 0, 0.5)
    # say hello (note after rotate the y coord needs to be negative!)
    c.drawString(0.3 * inch, -inch, "Hello World")


def simplePDFget(filename, strVal):
    c = canvas.Canvas(filename)
    c.drawString(100, 700, strVal)

    hello(c)

    c.drawString(300, 400, str(inch))

    c.save()





simplePDFget("f1.pdf", "Test test test 1")