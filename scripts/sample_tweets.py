from argparse import ArgumentParser
from pathlib import Path


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('files', nargs='+', help='list of files from which we will sample')
    parser.add_argument('output_dir', help='output dir for the new files (')
    parser.add_argument('--every', default=8, type=int, help='take every nth tweet id')
    # parser.add_argument('--skip', )  # TODO if we sample again, but to skip those sampled earlier
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in args.files:
        filepath = Path(filepath).resolve()
        with filepath.open('r', encoding='utf-8') as f:
            ids = [line.strip() for line in f.read().strip('\n').split('\n') if line.strip()]

        sampled_ids = ids[::args.every]

        with open(output_dir / (filepath.stem + '-subsampled' + filepath.suffix), 'w', encoding='utf-8') as f:
            f.write('\n'.join(sampled_ids) + '\n')
