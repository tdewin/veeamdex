#!/usr/bin/env python3

from PIL import Image
import argparse
import os

def convert_png_to_ico(png_path, output_path):
    image = Image.open(png_path)
    image.save(output_path, format='ICO')
    print(f"Converted '{png_path}' to '{output_path}'")

def main():
    parser = argparse.ArgumentParser(description="Convert a PNG image to ICO format.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input PNG file")
    parser.add_argument("-o", "--output", required=True, help="Path to save the output ICO file")
    args = parser.parse_args()

    convert_png_to_ico(args.input, args.output)

if __name__ == "__main__":
    main()


