from mwrogue.esports_client import EsportsClient
from mwrogue.auth_credentials import AuthCredentials


def run(site: EsportsClient, namespace_id, silent=False):
    for page in site.client.allpages(namespace=namespace_id):
        page.purge()
        if not silent:
            print(f"Purged {page.name}")


if __name__ == "__main__":
    credentials = AuthCredentials(user_file="me")
    lol_site = EsportsClient("lol", credentials=credentials)
    run(lol_site, "10006")

