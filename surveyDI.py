from argparse import ArgumentParser
import surveyDI_lib
from config import logger
from config import OPUT_QR, OPUT_SQ, OPUT_Q, OPUT_R, OPUT_S




def parse_cli_opts():
    global args

    parser = ArgumentParser(description='''convert the CSV files in the input\ 
directory to a format that can be easily be imported into a database''')
    parser.add_argument('-i', '--input_dir', 
                        help='Directory containing input csv files', 
                        required=True)
    parser.add_argument('-o', '--output_dir', 
                        help='Directory that will contain output files', 
                        default=".")
    args = parser.parse_args()


def main():
    global args

    parse_cli_opts()


if __name__ == "__main__":
    main()
