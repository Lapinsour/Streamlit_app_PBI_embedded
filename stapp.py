import streamlit as st
import requests
import msal

# ==============================
# 🔧 CONFIGURATION
# ==============================


DATASET_ID = "6d0e2103-de16-4df7-9db3-4c1edda058a2"

TENANT_ID = "d7c9c94d-28a2-4298-a72e-b1bee01d5b58"
CLIENT_ID = "750222b4-4621-4168-993b-f81c5a18028f"
CLIENT_SECRET = "~l18Q~3NEMxZBPT3.ND0g4sehRzGNfD0VexKnaQ6"
GROUP_ID = "6af085ad-ae79-4abe-a118-e392a87f4cb5"
REPORT_ID = "658be3a7-7e2e-4c85-99a4-abdc0d09dbd2"

AUTHORITY_URL = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]

POWER_BI_API = "https://api.powerbi.com/v1.0/myorg"

# ==============================
# 🔐 AUTHENTIFICATION AAD
# ==============================

def get_access_token():
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY_URL,
        client_credential=CLIENT_SECRET,
    )

    result = app.acquire_token_for_client(scopes=SCOPE)

    if "access_token" not in result:
        raise Exception(f"Erreur auth AAD : {result}")

    return result["access_token"]

# ==============================
# 🎟️ GENERATION EMBED TOKEN
# ==============================

def get_embed_token(username="user@test.com", role="Role1"):
    access_token = get_access_token()

    url = f"{POWER_BI_API}/groups/{GROUP_ID}/reports/{REPORT_ID}/GenerateToken"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    body = {
        "accessLevel": "View"
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception(f"Erreur token Power BI : {response.text}")

    return response.json()["token"]

# ==============================
# 🌐 STREAMLIT UI
# ==============================

st.set_page_config(layout="wide")

st.title("📊 Power BI Embedded (minimal)")

try:
    token = get_embed_token()

    embed_url = f"https://app.powerbi.com/reportEmbed?reportId=658be3a7-7e2e-4c85-99a4-abdc0d09dbd2&autoAuth=true&ctid=d7c9c94d-28a2-4298-a72e-b1bee01d5b58"
    st.write(embed_url)
    html_code = f"""
<html>
  <head>
    <script src="https://cdn.jsdelivr.net/npm/powerbi-client@2.23.1/dist/powerbi.min.js"></script>
  </head>
  <body>
    <div id="reportContainer" style="height:900px;"></div>

    <script>
      var models = window['powerbi-client'].models;

      var embedConfig = {{
        type: 'report',
        id: '{REPORT_ID}',
        embedUrl: 'https://app.powerbi.com/reportEmbed?reportId={REPORT_ID}&groupId={GROUP_ID}',
        accessToken: '{token}',
        tokenType: models.TokenType.Embed
      }};

      var container = document.getElementById('reportContainer');
      powerbi.embed(container, embedConfig);
    </script>
  </body>
</html>
"""

    st.components.v1.html(html_code, height=900)

except Exception as e:
    st.error(f"Erreur : {e}")
