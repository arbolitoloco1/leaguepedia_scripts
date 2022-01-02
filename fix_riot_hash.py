import mwparserfromhell
from mwrogue.esports_client import EsportsClient
from mwrogue.auth_credentials import AuthCredentials

credentials = AuthCredentials(user_file="bot")
site = EsportsClient("lol", credentials=credentials)

response = site.cargo_client.query(
    tables="PostgameJsonMetadata=PJM",
    fields="PJM.RiotHash, PJM._pageName=Page",
    where='PJM.RiotHash IS NOT NULL AND PJM.RiotHash LIKE "%&%"'
)

for item in response:
    page = site.client.pages[item["Page"]]
    page_text = page.text()
    page_wikitext = mwparserfromhell.parse(page_text)
    for template in page_wikitext.filter_templates():
        if template.has("RiotHash"):
            hash = str(template.get("RiotHash").value.strip())
            if hash != "":
                fixed_hash = hash.split("&")[0]
                print(fixed_hash)
                template.add("RiotHash", fixed_hash)
    page.edit(str(page_wikitext), summary="Fixing RiotHash")
