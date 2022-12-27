from mwcleric.errors import RetriedLoginAndStillFailed
from mwrogue.esports_client import EsportsClient
from mwrogue.auth_credentials import AuthCredentials
from mwcleric.template_modifier import TemplateModifierBase
from mwparserfromhell import parse
from time import sleep
import re


class TwitterLinkCleanup(TemplateModifierBase):
    def update_template(self, template):
        if not template.has("link"):
            return
        link = template.get("link").value.strip()
        if not re.match(r"^https?://(www\.)?twitter.com", link):
            return
        if "?" not in link:
            return
        template.add("link", link.split("?")[0])
        with open(file="linkcleanup.log", mode="a+", encoding="utf8") as f:
            f.write(f"{link}\n{link.split('?')[0]}\n\n")

    def run(self):
        lmt = 0
        for page in self.page_list:
            if lmt == self.limit:
                break
            if self.startat_page and page.name == self.startat_page:
                self.passed_startat = True
            if not self.passed_startat:
                self._print("Skipping page %s, before startat" % page.name)
                continue
            if page.name in self.skip_pages:
                self._print("Skipping page %s as requested" % page.name)
                continue
            lmt += 1
            self.current_text = page.text()
            self.current_page = page
            self.current_wikitext = parse(self.current_text)
            self.current_text = self.update_plaintext(self.current_text)
            self.update_wikitext(self.current_wikitext)
            newtext = str(self.current_wikitext)

            newtext = self.postprocess_plaintext(newtext)
            if newtext != self.current_page.text() and not self.prioritize_plaintext:
                self._print('Saving page %s...' % page.name)
                sleep(self.lag)
                try:
                    self.site.save(page, newtext, summary=self.summary, tags=self.tags)
                except RetriedLoginAndStillFailed:
                    pass
            elif self.current_text != self.current_page.text():
                self._print('Saving page %s...' % page.name)
                sleep(self.lag)
                self.site.save(page, self.current_text, summary=self.summary, tags=self.tags)
            else:
                self._print('Skipping page %s...' % page.name)


if __name__ == "__main__":
    credentials = AuthCredentials(user_file="bot")
    site = EsportsClient("lol", credentials=credentials, max_retries=0)
    TwitterLinkCleanup(site, ["Source"], summary="Cleaning up twitter links").run()
