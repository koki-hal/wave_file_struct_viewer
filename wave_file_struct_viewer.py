import argparse
import os
import sys
import wave
from dataclasses import dataclass


def color_red():
    print('\033[31m')
    pass


def color_normal():
    print('\033[0m')
    pass


@dataclass
class RIFFHeader:           # 12 bytes
    FourCC: str             # 4 bytes strings
    data_size: int          # 4 byte integer
    data_type: str          # 4 bytes strings

@dataclass
class ChunkHeader:          # 8 bytes
    chunk_id: str           # 4 bytes strings
    chunk_size: int         # 4 byte integer

@dataclass
class FmtChunk:             # 16 bytes
    sound_fmt_type: int     # 2 byte integer
    channels: int           # 2 byte integer
    sampling_rate: int      # 4 byte integer
    ave_bytes_per_sec: int  # 4 byte integer
    block_size: int         # 2 byte integer
    bits_per_sample: int    # 2 byte integer

@dataclass
class InfoTag:              # 4 bytes
    info_tag: str           # 4 bytes strings

@dataclass
class SubChunk:
    sub_chunk_data: str     # variable length


def read_data(f, size):
    databuf = f.read(size)
    datalen = len(databuf)
    if datalen != size:
        return None
    return databuf


def analize_riff_header(f):
    if (databuf := read_data(f, 12)) is None:
        color_red()
        print('Unknown error. Process terminated.')
        color_normal()
        sys.exit(1)

    header = RIFFHeader(*wave.struct.unpack('<4sI4s', databuf))

    print(f'FourCC    : "{header.FourCC.decode()}"')
    print(f'data size : {header.data_size:,} (= filesize - 8)')
    print(f'data type : "{header.data_type.decode()}"')

    if header.FourCC != b'RIFF':
        color_red()
        print()
        print('Error:')
        print('  This is NOT a "Resource Interchange File Format(RIFF)" file.')
        print('  This application does not support this format.')
        color_normal()
        return False

    if header.data_type != b'WAVE':
        color_red()
        print()
        print('Error:')
        print('  This is NOT a "RIFF waveform Audio Format(WAVE)" file.')
        print('  This application does not support this format.')
        color_normal()
        return False

    return True


def analize_fmt_chunk(f):
    if (databuf := read_data(f, 16)) is None:
        color_red()
        print('Unknown error. Process terminated.')
        color_normal()
        sys.exit(1)

    fmt = FmtChunk(*wave.struct.unpack('<HHIIHH', databuf))

    print(f'  sound format type     : {fmt.sound_fmt_type}', end='')
    if   fmt.sound_fmt_type == 1:  print(f' - Linear pulse code modulation(Linear PCM)')
    elif fmt.sound_fmt_type == 2:  print(f' - Microsoft ADPCM')
    elif fmt.sound_fmt_type == 3:  print(f' - IEEE float')
    elif fmt.sound_fmt_type == 6:  print(f' - ITU G.711 a-law')
    elif fmt.sound_fmt_type == 7:  print(f' - ITU G.711 µ-law')
    else:                          print(f' - Unknown')

    print(f'  channels              : {fmt.channels}', end='')
    if   fmt.channels == 1:  print(f' - monaural')
    elif fmt.channels == 2:  print(f' - stereo')
    else:                    print()

    print(f'  sampling rate         : {fmt.sampling_rate:,}')
    print(f'  average bytes per sec : {fmt.ave_bytes_per_sec:,} (= sampling rate * block size)')
    print(f'  block size            : {fmt.block_size} (= channels * bits per sample / 8)')
    print(f'  bits per sample       : {fmt.bits_per_sample}')

    if fmt.sound_fmt_type != 1:
        color_red()
        print()
        print('Error:')
        print('  This is NOT a "Linear pulse code modulation(Linear PCM)" file.')
        print('  This application does not support this format.')
        color_normal()
        return False

    return True


def analize_wav_structure(wav_file):
    with open(wav_file, 'rb') as f:
        if not analize_riff_header(f):
            return

        print()

        while databuf := f.read(8):
            if len(databuf) != 8:
                color_red()
                print('Unknown error. Process terminated.')
                color_normal()
                sys.exit(1)

            chunk = ChunkHeader(*wave.struct.unpack('<4sI', databuf))

            if chunk.chunk_id == b'fmt ':
                print(f'chunk_id   : "{chunk.chunk_id.decode()}"')
                print(f'chunk_size : {chunk.chunk_size:,}')

                if not analize_fmt_chunk(f):
                    return

                if chunk.chunk_size > 16:
                    color_red()
                    print()
                    print('Error:')
                    print('  This file has an extra chunk.')
                    print('  This application does not support this format.')
                    print('  Linear PCM should NOT have an extra chunk.')
                    color_normal()

                    seek_size = chunk.chunk_size - 16
                    f.seek(seek_size, os.SEEK_CUR)
                    if seek_size % 2 == 1:
                        # skip padding byte
                        f.seek(1, os.SEEK_CUR)

                print()

            elif chunk.chunk_id == b'data':
                print(f'chunk_id  : "{chunk.chunk_id.decode()}"')
                print(f'data_size : {chunk.chunk_size:,}')
                # skip data chunk
                f.seek(chunk.chunk_size, os.SEEK_CUR)

                print()

            elif chunk.chunk_id == b'LIST':
                print(f'chunk_id   : "{chunk.chunk_id.decode()}"')
                print(f'chunk_size : {chunk.chunk_size:,}')

                print()

                if (databuf := read_data(f, 4)) is None:
                    color_red()
                    print('Unknown error. Process terminated.')
                    color_normal()
                    sys.exit(1)
                info_tag = InfoTag(*wave.struct.unpack('<4s', databuf))
                print(f'info_tag : "{info_tag.info_tag.decode()}"')

                print()

            else:
                print(f'sub chunk id   : "{chunk.chunk_id.decode()}"')
                print(f'sub chunk size : {chunk.chunk_size:,}')

                unpack_format = f'<{chunk.chunk_size}s'

                if chunk.chunk_id == b'IART':
                    if (databuf := read_data(f, chunk.chunk_size)) is None:
                        color_red()
                        print('Unknown error. Process terminated.')
                        color_normal()
                        sys.exit(1)
                    chunk_data = SubChunk(*wave.struct.unpack(unpack_format, databuf))
                    print(f'  Artist : "{chunk_data.sub_chunk_data.decode()}"')
                    pass

                elif chunk.chunk_id == b'ICRD':
                    if (databuf := read_data(f, chunk.chunk_size)) is None:
                        color_red()
                        print('Unknown error. Process terminated.')
                        color_normal()
                        sys.exit(1)
                    chunk_data = SubChunk(*wave.struct.unpack(unpack_format, databuf))
                    print(f'  Creation date : "{chunk_data.sub_chunk_data.decode()}"')
                    pass

                elif chunk.chunk_id == b'INAM':
                    if (databuf := read_data(f, chunk.chunk_size)) is None:
                        color_red()
                        print('Unknown error. Process terminated.')
                        color_normal()
                        sys.exit(1)
                    chunk_data = SubChunk(*wave.struct.unpack(unpack_format, databuf))
                    print(f'  Title : "{chunk_data.sub_chunk_data.decode()}"')
                    pass

                elif chunk.chunk_id == b'IPRT':
                    if (databuf := read_data(f, chunk.chunk_size)) is None:
                        color_red()
                        print('Unknown error. Process terminated.')
                        color_normal()
                        sys.exit(1)
                    chunk_data = SubChunk(*wave.struct.unpack(unpack_format, databuf))
                    print(f'  Part : "{chunk_data.sub_chunk_data.decode()}"')
                    pass

                elif chunk.chunk_id == b'ISFT':
                    if (databuf := read_data(f, chunk.chunk_size)) is None:
                        color_red()
                        print('Unknown error. Process terminated.')
                        color_normal()
                        sys.exit(1)
                    chunk_data = SubChunk(*wave.struct.unpack(unpack_format, databuf))
                    print(f'  Software : "{chunk_data.sub_chunk_data.decode()}"')
                    pass

                elif chunk.chunk_id == b'IURL':
                    if (databuf := read_data(f, chunk.chunk_size)) is None:
                        color_red()
                        print('Unknown error. Process terminated.')
                        color_normal()
                        sys.exit(1)
                    chunk_data = SubChunk(*wave.struct.unpack(unpack_format, databuf))
                    print(f'  URL : "{chunk_data.sub_chunk_data.decode()}"')
                    pass

                else:
                    if chunk.chunk_id == b'fact':
                        color_red()
                        print()
                        print('Error:')
                        print('  This file has a "fact chunk" that means data is compressed.')
                        print('  This application does not support compressed data.')
                        color_normal()
                        pass

                    # skip unknown chunk
                    f.seek(chunk.chunk_size, os.SEEK_CUR)

                # skip padding byte
                if chunk.chunk_size % 2 == 1:
                    f.seek(1, os.SEEK_CUR)

                print()

    pass


app_name = 'wave_file_struct_viewer'
app_description = 'Show struucture of WAV file(s).'

parser = argparse.ArgumentParser(
        prog=app_name,
        description=app_description,
        add_help=False,
        allow_abbrev=False,
    )

parser.add_argument('-h', '--help', action='help', help='Show this help message and exit.')
parser.add_argument('wav_files', type=str, nargs='+', metavar='WAV-file', help='Specify one or more WAV file(s).')

args = parser.parse_args()
wav_files = args.wav_files


def main():
    for wav_file in wav_files:
        # check if file exists
        if not os.path.exists(wav_file):
            color_red()
            print(f'Error: File "{wav_file}" does not exist.')
            color_normal()
            continue

        # get file size
        try:
            file_size = os.path.getsize(wav_file)
        except OSError as e:
            color_red()
            print(f'Error getting size of file {wav_file}: {e}')
            color_normal()

        print('=' * 40)
        print(f'WAV file  : {wav_file}')
        print(f'File size : {file_size:,} bytes')
        print()

        analize_wav_structure(wav_file)
    pass


if __name__ == '__main__':
    main()
    pass


