import argparse
import sql 

parser = argparse.ArgumentParser()
parser.add_argument(action = "view")
parser.add_argument(action = "describe")
parser.add_argument(directory)

def view_csv_schema(directory[str]):
    