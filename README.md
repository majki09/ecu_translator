# ECU Translator
Script for translating strings in DDT ECU files. It is mostly useful for [ddt4all](https://github.com/cedricp/ddt4all) 
and I have created it to translate french ECU files to english. It uses google translate module to translate strings. 

## Disclaimer
This script is just an experiment. I have made it for my own purposes.
If you find it useful, go ahead and use it, but remember - **I'm not taking any responsibility! Only responsible is you.**

## Local dictionary
After using google the translation will be saved into locally saved dictionary file.
- it is a locally saved CSV file with *.dict* extension,
- it can be modified even in notepad,
- it is used everytime before calling google to translate.

# Usage
    python translate.py --file "ECU_FILE" --lang en

where:
- **ECU_FILE** - your ecu file to translate, it can be ended with *.json* or *.json.layout*,
- **lang** - destination language, use only 2 characters ('en' and not 'eng').

The script will generate both *json* and *json.layout* files with *_translated* ending.

# TO DO:
- quality of translations - google translator is not always good enough, sometimes manual translations are better,
- logging to log file.