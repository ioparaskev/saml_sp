Simple SAML SP
==============

This is a simple SAML Service Provider (SP) that can be used to test your IdP settings.

# Usage

Generate SAML certificates:

```
openssl req -x509 -newkey rsa:4096 -new -nodes -x509 -days 365 -keyout certs/saml/sp.key -out certs/saml/sp.crt  
```

(optionally) Generate https certificates:

```
openssl req -x509 -newkey rsa:4096 -new -nodes -x509 -days 365 -keyout certs/http/https_key.pem -out certs/http/https_cert.pem
```

Update settings.json with your IdP metadata:
If you have the IdP metadata XML file, you can update the settings.json file with the IdP metadata:

```
python idp_settings.py --file idp_metadata.xml
```

If you have the IdP metadata URL, you can update the settings.json file with the IdP metadata:

```
python idp_settings.py --url https://idp.example.com/metadata.xml
```

Update settings.json with your SP certificates, entity ID and (optionally) NameID format:

```
python sp_settings.py --cert_path certs/saml --entityid https://localhost:9443 --nameid-format urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress
```

Run the SP server with optional HTTPS certificates path and port:

```
python app.py --cert certs/http/https_cert.pem --key certs/http/https_key.pem --port 9443
```

Visit <entityid>/login to login and see the returned SAML attributes
