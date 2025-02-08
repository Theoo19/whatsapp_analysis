import fpdf


class PDF(fpdf.FPDF):
    pass


def main():
    pdf = PDF(unit="mm", format="A4")
    pdf.add_page()
    pdf.output("Test.pdf")


if __name__ == '__main__':
    main()
