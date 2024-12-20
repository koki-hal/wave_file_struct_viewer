## Wave sound file structure viewer

This script will show the structure of wave sound file(s). It's not that this script supports all kind of wave structure.  
This script expectes "Linear pulse code modulation(Linear PCM)" file(s).

This script currently shows the following information:

- RIFF header
- fmt chunk
- LIST chunk
	- INFO chunk
		- IART tag
		- ICRD tag
		- INAM tag
		- IPRT tag
		- ISFT tag
		- IURL tag
- fact chunk
- data chunk

## Usage

python wave_file_struct_viewer.py [-h] WAV-file [WAV-file ...]

ex)  
python wave_file_struct_viewer.py test1.wav test2.wav test_?.wav test-*.wav


## Reference

- [RIFF File Structure](https://johnloomis.org/cpe102/asgn/asgn1/riff.html)  
- [RIFF Tags](https://exiftool.org/TagNames/RIFF.html)  
- [Wave file format](https://www.recordingblogs.com/wiki/wave-file-format)  
- [Format chunk (of a Wave file)](https://www.recordingblogs.com/wiki/format-chunk-of-a-wave-file)  
- [Fact chunk (of a Wave file)](https://www.recordingblogs.com/wiki/fact-chunk-of-a-wave-file)

