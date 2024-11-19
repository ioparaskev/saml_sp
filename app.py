import argparse
import os
from flask import Flask, request, redirect, session, jsonify, make_response
from onelogin.saml2.auth import OneLogin_Saml2_Auth


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")


def init_saml_auth(req):
    return OneLogin_Saml2_Auth(req, custom_base_path=os.getcwd())


def prepare_flask_request(request):
    url_data = request.args.copy()
    return {
        "https": "on" if request.scheme == "https" else "off",
        "http_host": request.host,
        "script_name": request.path,
        "server_port": request.environ.get("SERVER_PORT", "80"),
        "get_data": url_data,
        "post_data": request.form.copy(),
    }


@app.route("/")
def index():
    if "saml_user_data" in session:
        return jsonify(session["saml_user_data"])
    else:
        return "No SAML data found. Please log in."


@app.route("/metadata/")
def metadata():
    auth = init_saml_auth(prepare_flask_request(request))
    saml_settings = auth.get_settings()
    metadata = saml_settings.get_sp_metadata()
    errors = saml_settings.validate_metadata(metadata)

    if len(errors) > 0:
        return make_response(", ".join(errors), 500)
    return metadata, {"Content-Type": "text/xml"}


@app.route("/acs/", methods=["POST"])
def acs():
    auth = init_saml_auth(prepare_flask_request(request))
    auth.process_response()
    errors = auth.get_errors()

    if len(errors) > 0:
        return f"Error processing SAML response: {errors}", 500

    if auth.is_authenticated():
        session["saml_user_data"] = {
            "name_id_format": auth.get_nameid_format(),
            "name_id": auth.get_nameid(),
            "session_index": auth.get_session_index(),
            "attributes": auth.get_attributes(),
        }
        return redirect("/")
    return "Failed to authenticate.", 403


@app.route("/sls/", methods=["GET", "POST"])
def sls():
    auth = init_saml_auth(prepare_flask_request(request))
    url = auth.process_slo()
    errors = auth.get_errors()

    if len(errors) > 0:
        return f"Error during SLO: {errors}", 500

    session.clear()
    return redirect(url or "/")


@app.route("/login/")
def login():
    auth = init_saml_auth(prepare_flask_request(request))
    return redirect(auth.login())


@app.route("/logout/")
def logout():
    auth = init_saml_auth(prepare_flask_request(request))
    return redirect(auth.logout())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SAML SP server")
    parser.add_argument(
        "--port",
        type=int,
        default=9443,
        help="Port to run the server on (default: 9443)",
    )
    parser.add_argument("--cert", help="Path to HTTPS certificate")
    parser.add_argument("--key", help="Path to HTTPS private key")

    args = parser.parse_args()

    ssl_context = None
    if args.cert and args.key:
        ssl_context = (args.cert, args.key)

    app.run(host="0.0.0.0", port=args.port, ssl_context=ssl_context)
