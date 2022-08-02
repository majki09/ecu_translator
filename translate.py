import argparse
import csv
import json
from googletrans import Translator as gTranslator


class Translator():
    def __init__(self, ecu, lang_out, lang_in="fr"):
        self.lang_input = lang_in
        self.lang_output = lang_out
        self.ecu = ecu

        self.local_dict = {}
        self.local_dict_filename = f"{lang_in}_{lang_out}.dict"
        self.local_dict_open_file()

        self.gtranslator = gTranslator()
        self.gtranslator.service_urls = ["translate.google.pl"]

    def local_dict_open_file(self):
        try:
            open(self.local_dict_filename, "r")
        except FileNotFoundError:
            open(self.local_dict_filename, "w")

        with open(self.local_dict_filename, "r", newline='', encoding='latin1') as local_dict_file:
            local_dict_reader = csv.reader(local_dict_file)
            for row in local_dict_reader:
                if len(row) > 0:
                    k, v = row
                    self.local_dict[k] = v

    def local_dict_append_to_file(self, item):
        with open(self.local_dict_filename, "a", newline='', encoding='latin1') as local_dict_file:
            local_dict_writer = csv.writer(local_dict_file)
            local_dict_writer.writerow(item)

    def local_dict_save_file(self):
        with open(self.local_dict_filename, "w", newline='', encoding='latin1') as local_dict_file:
            local_dict_writer = csv.writer(local_dict_file)
            local_dict_writer.writerows(self.local_dict.items())

    def local_dict_lookup(self, word: str):
        if word in self.local_dict:
            return self.local_dict[word]
        else:
            return False

    def translate(self, text: str):
        if text == "":
            return ""
        if text == " ":
            return " "

        # lookup for text in local dictionary file
        out = self.local_dict_lookup(word=text)
        if out is False:
            # if not found in local dictionary, ask google translator
            out = self.gtranslator.translate(text=text, dest=self.lang_output, src=self.lang_input).text

            # get rid of /u200b ZERO-WIDTH spaces
            out = out.replace(u'\u200b', '')

            print(f"\"{text}\"\ttranslated to\t\"{out}\"")

            self.local_dict[text] = out

            # append translation into local dictionary file
            self.local_dict_append_to_file(item=(text, out))

        return out

    def translate_requests(self):
        print("TRANSLATING REQUESTS SECTION:")
        for i, request in enumerate(self.ecu.requests):
            print(f"{(i+1) / len(self.ecu.requests) * 100:.0f}% \t {i + 1}/{len(self.ecu.requests)}")
            # translate name
            new_request = self.translate(request["name"])
            request["name"] = new_request

            # translate sendbyte_dataitems if exist
            if "sendbyte_dataitems" in request:
                new_sendbyte_dataitems = {}
                for dataitem in request["sendbyte_dataitems"]:
                    new_dataitem = self.translate(dataitem)
                    new_sendbyte_dataitems[new_dataitem] = request["sendbyte_dataitems"][dataitem]

                # replace whole "sendbyte_dataitems" to translated one
                request["sendbyte_dataitems"] = new_sendbyte_dataitems

            # translate receivebyte_dataitems if exist
            if "receivebyte_dataitems" in request:
                new_receivebyte_dataitems = {}
                for dataitem in request["receivebyte_dataitems"]:
                    new_dataitem = self.translate(dataitem)
                    new_receivebyte_dataitems[new_dataitem] = request["receivebyte_dataitems"][dataitem]

                # replace whole "receivebyte_dataitems" to translated one
                request["receivebyte_dataitems"] = new_receivebyte_dataitems

        print("TRANSLATING REQUESTS SECTION FINISHED.")

    def translate_data(self):
        excluded_lists = ["Jour"]
        print("TRANSLATING DATA SECTION:")

        new_data = {}
        for i, (k, v) in enumerate(self.ecu.data.items()):
            print(f"{(i+1) / len(self.ecu.data) * 100:.0f}% \t {i + 1}/{len(self.ecu.data)}")
            # translate name
            new_data_name = self.translate(k)

            # translate lists if exist
            if "lists" in v and k not in excluded_lists:
                new_lists = {}
                for list in v["lists"]:
                    new_list = self.translate(v["lists"][list])
                    new_lists[list] = new_list

                # replace whole "lists" to translated one
                v["lists"] = new_lists

            new_data[new_data_name] = v

        # replace all 'data' to translated ones
        self.ecu.data = new_data

        print("TRANSLATING DATA SECTION FINISHED.")

    def translate_categories(self):
        print("TRANSLATING CATEGORIES SECTION:")

        # translate category name
        new_categories = {}
        for i, category in enumerate(self.ecu.categories):
            print(f"{(i+1) / len(self.ecu.categories) * 100:.0f}% \t {i + 1}/{len(self.ecu.categories)}")
            new_category_name = self.translate(category)
            new_category = self.ecu.categories[category]

            # translate all screens
            for i, name in enumerate(new_category):
                new_name = self.translate(name)
                new_category[i] = new_name

            # replace whole category to translated one
            new_categories[new_category_name] = new_category

        # replace all categories to translated ones
        self.ecu.categories = new_categories

        print("TRANSLATING CATEGORIES SECTION FINISHED.")

    def translate_screens(self):
        print("TRANSLATING SCREENS SECTION:")

        # translate all screens
        new_screens = {}
        for i, screen in enumerate(self.ecu.screens):
            print(f"{(i+1) / len(self.ecu.screens) * 100:.0f}% \t {i + 1}/{len(self.ecu.screens)}")
            new_screen_name = self.translate(screen)
            new_screen = self.ecu.screens[screen]

            # translate all inputs
            for input in new_screen["inputs"]:
                new_text = self.translate(input["text"])
                input["text"] = new_text
                new_request = self.translate(input["request"])
                input["request"] = new_request

            # translate all labels
            for label in new_screen["labels"]:
                new_text = self.translate(label["text"])
                label["text"] = new_text

            # translate all presends
            for presend in new_screen["presend"]:
                new_presend = self.translate(presend["RequestName"])
                presend["RequestName"] = new_presend

            # translate all buttons
            for button in new_screen["buttons"]:
                new_text = self.translate(button["text"])
                button["text"] = new_text

                # translate 'sends'
                for send in button["send"]:
                    new_requestname = self.translate(send["RequestName"])
                    send["RequestName"] = new_requestname

            # translate all displays
            for display in new_screen["displays"]:
                new_text = self.translate(display["text"])
                display["text"] = new_text
                new_request = self.translate(display["request"])
                display["request"] = new_request

            # replace whole screen to translated one
            new_screens[new_screen_name] = new_screen

        # replace all screens to translated ones
        self.ecu.screens = new_screens

        print("TRANSLATING SCREENS SECTION FINISHED.")

    def translate_all(self):
        self.translate_data()
        self.translate_requests()
        self.translate_categories()
        self.translate_screens()

        self.ecu.file_json["data"] = self.ecu.data
        self.ecu.file_json["requests"] = self.ecu.requests

        self.ecu.file_layout["categories"] = self.ecu.categories
        self.ecu.file_layout["screens"] = self.ecu.screens

        return self.ecu


class Ecu:
    def __init__(self, input_filename: str = ""):
        self.input_filename = input_filename
        self.filename_json = self.input_filename.split('.json')[0] + ".json"
        self.filename_layout = self.input_filename.split('.json')[0] + ".json.layout"
        self.file_layout = None
        self.file_json = None
        self.name = ""
        self.requests = {}
        self.data = {}
        self.screens = {}
        self.categories = {}

    def file_open_json(self):
        with open(self.filename_json, "r") as file:
            self.file_json = json.load(file)
            self.name = self.file_json["ecuname"]
            self.requests = self.file_json["requests"]
            self.data = self.file_json["data"]

    def file_open_layout(self):
        with open(self.filename_layout, "r") as file:
            self.file_layout = json.load(file)
            self.screens = self.file_layout["screens"]
            self.categories = self.file_layout["categories"]

    def file_save_json(self):
        with open(self.filename_json + "_translated", "w") as outfile:
            outfile.write(json.dumps(self.file_json, indent=1))

    def file_save_layout(self):
        with open(self.filename_layout + "_translated", "w") as outfile:
            outfile.write(json.dumps(self.file_layout, indent=1))


def main():
    # Parsing command line parameters
    args_parser = argparse.ArgumentParser(description="Script for translating strings in DDT ECU files.")
    args_parser.add_argument("--file", "-f", required=True, metavar="C:\\file.layout", type=str,
                             help="Provides file to translate.")
    args_parser.add_argument("--lang", "-l", required=True, metavar="en", type=str,
                             help="Output language to translate.")

    args = args_parser.parse_args()

    ecu = Ecu(input_filename=args.file)
    ecu.file_open_json()
    ecu.file_open_layout()

    translator = Translator(ecu, lang_out=args.lang)
    translator.lang_output = args.lang

    translator.translate_all()

    print("SAVING FILES...")
    ecu.file_save_json()
    ecu.file_save_layout()
    print("SAVING FILES FINISHED.")


if __name__ == "__main__":
    main()
