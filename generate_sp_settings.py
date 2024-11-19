import argparse
import json
import os


def load_certificate(cert_path):
    """Load and format X.509 certificate content."""
    with open(cert_path, "r") as f:
        cert_content = f.read()
    # Remove any whitespace and ensure proper formatting
    cert_content = (
        cert_content.replace("\n", "")
        .replace("-----BEGIN CERTIFICATE-----", "")
        .replace("-----END CERTIFICATE-----", "")
    )
    return f"-----BEGIN CERTIFICATE-----{cert_content}-----END CERTIFICATE-----"


def load_private_key(key_path):
    """Load and format private key content."""
    with open(key_path, "r") as f:
        key_content = f.read()
    # Remove any whitespace and ensure proper formatting
    key_content = (
        key_content.replace("\n", "")
        .replace("-----BEGIN PRIVATE KEY-----", "")
        .replace("-----END PRIVATE KEY-----", "")
    )
    return f"-----BEGIN PRIVATE KEY-----{key_content}-----END PRIVATE KEY-----"


def update_sp_urls(entity_id, nameid_format):
    """Generate SP URL configurations based on entity ID."""
    return {
        "entityId": entity_id,
        "assertionConsumerService": {
            "url": f"{entity_id}/acs",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
        },
        "singleLogoutService": {
            "url": f"{entity_id}/sls/",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        },
        "NameIDFormat": nameid_format,
    }


def get_default_settings():
    """Return default settings structure"""
    return {
        "strict": True,
        "debug": True,
        "sp": {},
        "idp": {}
    }


def update_settings_json(
    cert_content=None,
    key_content=None,
    entity_id=None,
    nameid_format=None,
    settings_file="settings.json",
):
    # Create or load settings
    if not os.path.exists(settings_file):
        settings = get_default_settings()
    else:
        with open(settings_file, "r") as f:
            settings = json.load(f)
    
    # Ensure sp section exists
    if "sp" not in settings:
        settings["sp"] = {}
    
    # Update SP settings
    if cert_content and key_content:
        settings["sp"]["x509cert"] = cert_content
        settings["sp"]["privateKey"] = key_content
    
    if entity_id:
        sp_urls = update_sp_urls(entity_id, nameid_format)
        settings["sp"].update(sp_urls)
    elif nameid_format:
        settings["sp"]["NameIDFormat"] = nameid_format
    
    # Write back to file with proper formatting
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)


def main():
    parser = argparse.ArgumentParser(
        description="Update settings.json with SP certificate and private key"
    )
    parser.add_argument(
        "--cert_path", help="Directory path containing sp.crt and sp.key files"
    )
    parser.add_argument("--entityid", help="Base URL for SP entity ID and endpoints")
    parser.add_argument(
        "--nameid-format",
        default="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        help="NameIDFormat for SP (default: urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress)",
    )

    args = parser.parse_args()

    if (
        not args.cert_path
        and not args.entityid
        and args.nameid_format == parser.get_default("nameid-format")
    ):
        parser.error(
            "At least one of --cert_path, --entityid, or --nameid-format must be provided"
        )

    try:
        cert_content = None
        key_content = None

        if args.cert_path:
            cert_file = os.path.join(args.cert_path, "sp.crt")
            key_file = os.path.join(args.cert_path, "sp.key")

            # Verify files exist
            if not os.path.exists(cert_file):
                raise FileNotFoundError(f"Certificate file not found: {cert_file}")
            if not os.path.exists(key_file):
                raise FileNotFoundError(f"Private key file not found: {key_file}")

            # Load and format certificate and private key
            cert_content = load_certificate(cert_file)
            key_content = load_private_key(key_file)

        # Update settings.json
        update_settings_json(
            cert_content=cert_content,
            key_content=key_content,
            entity_id=args.entityid,
            nameid_format=args.nameid_format,
        )
        print("Successfully updated settings.json")

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
