import argparse
import json
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser
import requests


def load_metadata_from_file(file_path):
    with open(file_path, "r") as metadata_file:
        return metadata_file.read()


def load_metadata_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def update_settings_json(idp_data, settings_file="settings.json"):
    with open(settings_file, "r") as f:
        settings = json.load(f)

    settings["idp"] = idp_data["idp"]

    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)


def main():
    parser = argparse.ArgumentParser(
        description="Update settings.json with IdP metadata"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Path to IdP metadata XML file")
    group.add_argument("--url", help="URL to IdP metadata")

    args = parser.parse_args()

    try:
        if args.file:
            metadata = load_metadata_from_file(args.file)
        else:
            metadata = load_metadata_from_url(args.url)

        idp_data = OneLogin_Saml2_IdPMetadataParser.parse(metadata)
        update_settings_json(idp_data)
        print("Successfully updated settings.json with IdP metadata")

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
