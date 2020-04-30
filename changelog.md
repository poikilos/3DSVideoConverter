# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [git] - 2020-04-30
### Removed
- Including DLLs in the repo causes license issues.
- Including ffmpeg and ffprobe is ridiculous--together they are 118.6MB.
```
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch ffmpeg/ffmpeg.exe" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch ffmpeg/ffprobe.exe" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch FFMPEG/ffmpeg.exe" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch FFMPEG/ffprobe.exe" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch FontAwesome.WPF.dll" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch IronPython.dll" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch IronPython.Modules.dll" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch IronPython.Wpf.dll" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch Microsoft.Dynamic.dll" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch Microsoft.Scripting.dll" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch StdLib.dll" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch Xceed.Wpf.Toolkit.dll" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch FFMPEG/FONTS/fonts.conf" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch ffmpeg/fonts/fonts.conf" --prune-empty --tag-name-filter cat -- --all

```
- Including pyc files in the repo is incorrect.
```
FILTER_BRANCH_SQUELCH_WARNING=1 find * -type f -iname "*.pyo" -exec git filter-branch --force --index-filter "git rm --cached --ignore-unmatch {}" --prune-empty --tag-name-filter cat -- --all \;
FILTER_BRANCH_SQUELCH_WARNING=1 find * -type f -iname "*.pyc" -exec git filter-branch --force --index-filter "git rm --cached --ignore-unmatch {}" --prune-empty --tag-name-filter cat -- --all \;
```
- After the above filtering the .git directory was still 35.9 MB though
  the rest of the repo was 2.2MB. Therefore:
```
wget -O ~/.local/bin/gitlistobjectbysize.sh https://gist.githubusercontent.com/magnetikonline/dd5837d597722c9c2d5dfa16d8efe5b9/raw/c2322721c2f328fa829fc5557b090939e877df6b/gitlistobjectbysize.sh
chmod +x ~/.local/bin/gitlistobjectbysize.sh
gitlistobjectbysize.sh
# shows:
# 100644 blob 0616c9791340d1e9c97da3f614861505f4a1578c   74912    OpenSourceLicenseTerms.txt
# 100644 blob 6cfa60d71d67e82e8ea8333637c7a4fbf904e739   66409    Lib/subprocess.py
# 100644 blob 5d55797cabe98a273c32b0418517abca03dca275   52661    3DS.ico
# 100644 blob 948256a3e19538aab8801de964ab6391ca184ba3   48454    Lib/threading.py
# 100644 blob 2de7f372325081c727edcabd2317bee0b2de96c0   47129    license-IronPython.txt
# 100644 blob e5e63e3c362376eb5b39e9a0c82b46a8160187cb   37421    Lib/encodings/mac_arabic.py
# 100644 blob 615a36c0c4e0e4653a8b01935ff84c6e0074335a   37208    Lib/codecs.py
# 100644 blob c004282d167337344a085ebc93bcca2c1e704145   35956    Lib/encodings/cp852.py
# 100644 blob ca96653ad87242c831c8c10b290ded7b265fb06f   35635    Lib/encodings/cp860.py
# 100644 blob 2c080e5443043ddd9b8a7534fcbf930a101efe8d   35635    Lib/encodings/cp737.py
# 100644 blob ce08f10f5bab100da46dc7841c478c538b75ebff   35587    Lib/encodings/cp861.py
# 100644 blob b246a491a2d75427ba989505f412781e3145590a   35572    Lib/encodings/cp865.py
# 100644 blob 800ae5021e26dbcb50ba775e2f2665b43fd52c4b   35518    Lib/encodings/cp437.py
# 100644 blob eadb989e13891629a246168cadf70040b7cb050b   35429    Lib/encodings/cp775.py
# 100644 blob 70e5139838294d4b6d17f17b2986f56edff5718d   35350    Lib/encodings/cp866.py
# 100644 blob fc8dfa5fdec3d4dbd2fdc12787e30c3153b0177f   35206    Lib/encodings/cp863.py
# 100644 blob b110f4ece721fed699e8cfdad2d4f924fb1867cb   35059    Lib/encodings/cp850.py
# 100644 blob 427a20d7da1e5c04329d9b40237b0a71c2e98dfd   34969    Lib/encodings/cp858.py
# 100644 blob d337e5be1a0436a502f758fcdc1159ee5088874d   34858    Lib/encodings/cp857.py
# 100644 blob f72e8cc5d63278100727c1c262ba1c22725d8d19   34804    Lib/encodings/cp855.py
# 100644 blob 9733ada1d765437dece8dc85d253a5a5ae5eb9e8   34609    Lib/encodings/cp864.py
# 100644 blob ac81345349ffbf96875ba25cc05bf118b640b137   34324    Lib/encodings/cp862.py
# 100644 blob 59e33186e9876a09d07bb576bebbb4cccb22e043   33910    Lib/encodings/cp869.py
# 100644 blob 024bb1d1b8619cedaf40d5cc1f1d75b351e0fd3b   28540    Lib/collections.py
# and many more in Lib.
# Therefore:
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch OpenSourceLicenseTerms.txt" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter "git rm --cached --ignore-unmatch OpenSourceLicenseTerms.txt" --prune-empty --tag-name-filter cat -- --all
FILTER_BRANCH_SQUELCH_WARNING=1 find Lib -type f -exec git filter-branch --force --index-filter "git rm --cached --ignore-unmatch {}" --prune-empty --tag-name-filter cat -- --all \;
```
- `git push origin --force --all`

## [git] - 2020-04-30
### Added
- Start from https://github.com/jhheo/3DSVideoConverter

### Changed
- Rename all-uppercase files and directory to lowercase.
- Split library licenses into separate files for clarity.

### Removed
(repo was formerly 163.9 MB)
- The try block around the whole program is rediculous
- Requiring CLR and IronPython is ridiculous for a trivial program.
