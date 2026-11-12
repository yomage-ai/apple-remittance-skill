#!/usr/bin/env python3
"""Crop actual browser pixels; optionally append the same page's native full-page capture."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-window', required=True)
    parser.add_argument('--tabs-bottom', type=int, required=True,
                        help='Measured source-pixel boundary between tabs and real address toolbar')
    parser.add_argument('--content-top', type=int,
                        help='Measured source-pixel boundary between address toolbar and web content')
    parser.add_argument('--full-page', help='Native full-page screenshot of exactly the same page at identical width')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    target = Path(args.output)
    if target.exists() or target.suffix.lower() != '.png':
        parser.error('output must be a new .png path')
    with Image.open(args.raw_window) as source:
        source.load()
        if not 0 < args.tabs_bottom < source.height - 400:
            parser.error('invalid tabs-bottom source-pixel boundary')
        if args.full_page:
            if args.content_top is None or not args.tabs_bottom < args.content_top < source.height:
                parser.error('full-page mode requires the actual content-top boundary')
            header = source.crop((0, args.tabs_bottom, source.width, args.content_top)).convert('RGB')
            with Image.open(args.full_page) as body:
                body.load()
                if body.width != source.width:
                    parser.error('window and native full-page widths differ; recapture, never scale')
                result = Image.new('RGB', (body.width, header.height + body.height))
                result.paste(header, (0, 0))
                result.paste(body.convert('RGB'), (0, header.height))
        else:
            if args.content_top is not None:
                parser.error('content-top applies only to full-page mode')
            result = source.crop((0, args.tabs_bottom, source.width, source.height)).convert('RGB')
        result.save(target, format='PNG')
    print(target)


if __name__ == '__main__':
    main()
