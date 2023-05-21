import tweepy
import os
from mwrogue.esports_client import EsportsClient
from mwrogue.auth_credentials import AuthCredentials
import re
import json
from datetime import datetime, timedelta
import pytz
from mwcleric.errors import RetriedLoginAndStillFailed
from mwclient.errors import APIError
import requests


class TweetsBackup(object):
    TIMEZONE = pytz.timezone("PST8PDT")
    REDIRECT_TEXT = "#REDIRECT[[Archive Twitter:{}]]\n{{{{TwitterArchivePage|is_redirect=Yes|date={}}}}}"
    SUMMARY = "Automatically creating Twitter Archive pages"
    ARCHIVED_TWEET_TEMPLATE = "{{{{ArchivedTweet{}}}}}"
    REFERENCE_TEXT = "{{{{TweetReference|id={}|type={}|text={}}}}}"
    RECENT_DAYS = 40

    def __init__(self, site: EsportsClient, commons_site: EsportsClient):
        self.twitter_client = tweepy.Client(os.environ.get("TWITTER_BEARER_TOKEN"), wait_on_rate_limit=True)
        self.site = site
        self.commons_site = commons_site
        self.pages = None
        self.tweet_ids = []
        self.tweet_content = {}
        self.tweet_dates = {}
        self.done_tweet_dates = []
        self.archived_tweets = None
        self.dropped_tweets = []

    def run2(self):
        self.open_tweet_ids()
        self.open_dropped_tweets()
        self.open_tweet_content()
        self.query_archived_tweets()
        self.fetch_and_process_tweets()
        self.save_tweet_content()
        self.save_dropped_tweets()
        self.set_tweet_dates()
        self.make_archive_pages()

    def run(self):
        self.get_recently_edited_pages_from_wiki()
        self.get_links_from_wiki()
        self.save_tweet_ids()
        self.open_dropped_tweets()
        self.open_tweet_content()
        self.query_archived_tweets()
        self.fetch_and_process_tweets()
        self.save_tweet_content()
        self.save_dropped_tweets()
        self.set_tweet_dates()
        self.make_archive_pages()

    def save_tweet_ids(self):
        with open(file="tweetids.json", mode="w+", encoding="utf8") as f:
            json.dump(self.tweet_ids, f, ensure_ascii=False)

    def open_tweet_ids(self):
        if not os.path.isfile("tweetids.json"):
            with open(file="tweetids.json", mode="w+", encoding="utf8") as f:
                json.dump([], f, ensure_ascii=False)
        with open(file="tweetids.json", mode="r+", encoding="utf8") as f:
            self.tweet_ids = json.load(f)

    def save_tweet_content(self):
        with open(file="tweetcontent.json", mode="w+", encoding="utf8") as f:
            json.dump(self.tweet_content, f, ensure_ascii=False)

    def open_tweet_content(self):
        if not os.path.isfile("tweetcontent.json"):
            with open(file="tweetcontent.json", mode="w+", encoding="utf8") as f:
                json.dump({}, f, ensure_ascii=False)
        with open(file="tweetcontent.json", mode="r+", encoding="utf8") as f:
            self.tweet_content = json.load(f)

    def save_dropped_tweets(self):
        with open(file="dropped.json", mode="w+", encoding="utf8") as f:
            json.dump(self.dropped_tweets, f, ensure_ascii=False)

    def open_dropped_tweets(self):
        if not os.path.isfile("dropped.json"):
            with open(file="dropped.json", mode="w+", encoding="utf8") as f:
                json.dump([], f, ensure_ascii=False)
        with open(file="dropped.json", mode="r+", encoding="utf8") as f:
            self.dropped_tweets = json.load(f)

    def get_pages_from_wiki(self):
        main_ns_pages = self.site.client.allpages(namespace="0")
        data_ns_pages = self.site.client.allpages(namespace="10008")
        self.pages = {"main": main_ns_pages, "data": data_ns_pages}

    def get_recently_edited_pages_from_wiki(self):
        main_ns_revs_gen = self.site.recentchanges_by_interval(60 * 24 * self.RECENT_DAYS, namespace="0")
        data_ns_revs_gen = self.site.recentchanges_by_interval(60 * 24 * self.RECENT_DAYS, namespace="10008")
        revs = [_ for _ in main_ns_revs_gen] + [_ for _ in data_ns_revs_gen]
        self.pages = {"main": []}
        for rev in revs:
            if rev['title'] not in self.pages["main"]:
                self.pages["main"].append(rev['title'])

    def get_links_from_wiki(self):
        for ns_pages in self.pages.values():
            for page in ns_pages:
                if isinstance(page, str):
                    page = self.site.client.pages[page]
                print(f"Searching in {page.name}")
                for link in page.extlinks():
                    if "twitter" not in link or "status" not in link:
                        continue
                    link_re_search = re.search(r"status/([0-9]+)", link)
                    if not link_re_search:
                        with open(file="backuptweets.log", mode="a+", encoding="utf8") as f:
                            f.write(f"Tweet id could not be found {link}\n")
                        continue
                    tweet_id = int(link_re_search[1])
                    if tweet_id not in self.tweet_ids:
                        self.tweet_ids.append(tweet_id)

    def fetch_and_process_tweets(self):
        for i, tweet_id in enumerate(self.tweet_ids):
            try:
                if str(tweet_id) in self.tweet_content or str(tweet_id) in self.archived_tweets:
                    continue
                if tweet_id in self.dropped_tweets:
                    continue
                resp = self.twitter_client.get_tweet(id=tweet_id,
                                                     media_fields="url",
                                                     tweet_fields="created_at,referenced_tweets",
                                                     expansions="attachments.media_keys,author_id,referenced_tweets.id")
                if resp.data is None:
                    self.dropped_tweets.append(tweet_id)
                    continue
                media = []
                references = []
                reference_types = {}
                if resp.data.referenced_tweets is not None:
                    for reference in resp.data.referenced_tweets:
                        reference_types[int(reference.id)] = reference.type
                if "media" in resp.includes:
                    for media_item in resp.includes["media"]:
                        media.append({"type": media_item.type, "url": media_item.url})
                if "tweets" in resp.includes:
                    for tweet in resp.includes["tweets"]:
                        references.append({"text": tweet.text, "id": tweet.id, "type": reference_types[tweet.id]})
                self.tweet_content[tweet_id] = {"text": resp.data.text,
                                                "author_username": resp.includes["users"][0]["username"],
                                                "media": media,
                                                "referenced_tweets": references,
                                                "created_at": datetime.timestamp(resp.data.created_at)}
                i += 1
                print(f"{i}/{len(self.tweet_ids)}")
            except tweepy.errors.BadRequest:
                self.dropped_tweets.append(tweet_id)
                continue

    def query_archived_tweets(self):
        response = self.site.cargo_client.query(
            tables="TwitterArchive=TA",
            fields="TA.TweetId",
            where="TA.TweetId IS NOT NULL"
        )
        self.archived_tweets = [item["TweetId"] for item in response]

    def sorted_tweet_content(self):
        return dict(sorted(self.tweet_content.items(), key=lambda x: x[1]["created_at"])).items()

    def set_tweet_dates(self):
        for tweet_id, tweet_data in self.sorted_tweet_content():
            if str(tweet_id) in self.archived_tweets:
                continue
            tweet_date = datetime.fromtimestamp(tweet_data["created_at"]).astimezone(self.TIMEZONE).strftime("%Y-%m-%d")
            if tweet_date not in self.tweet_dates:
                self.tweet_dates[tweet_date] = {}
            self.tweet_dates[tweet_date][tweet_id] = tweet_data

    def create_redirect(self, sunday, day):
        self.site.save_title(title=f"Archive Twitter:{datetime.strftime(day, '%Y-%m-%d')}",
                             text=self.REDIRECT_TEXT.format(datetime.strftime(sunday, '%Y-%m-%d'),
                                                            datetime.strftime(day, '%Y-%m-%d')),
                             summary=self.SUMMARY)
        print(f"Saved redirect {datetime.strftime(day, '%Y-%m-%d')}")

    @staticmethod
    def concat_args(lookup: list):
        ret = ''
        for pair in lookup:
            pair: dict
            for key in pair.keys():
                if pair[key] is None:
                    ret = ret + '|{}= '.format(key)
                else:
                    ret = ret + '|{}= {} '.format(key, str(pair[key]))
        return ret

    def make_one_tweet_output(self, tweet_id, tweet_data):
        username = tweet_data["author_username"]
        tweet_args = [
                {"id": str(tweet_id)},
                {"username": username},
                {"text": tweet_data["text"].replace("\n", "<br>").replace("|", "{{!}}")},
                {"creation": datetime.fromtimestamp(tweet_data["created_at"]).astimezone(self.TIMEZONE).strftime("%Y-%m-%d %H:%M")}
            ]
        for i, reference in enumerate(tweet_data["referenced_tweets"]):
            i += 1
            tweet_args.append(
                {f"reference{i}": self.REFERENCE_TEXT.format(reference["id"],
                                                             reference["type"],
                                                             reference["text"].replace("\n", "<br>")
                                                             .replace("|", "{{!}}")
                                                             )
                 })
        if any(media["type"] == "video" for media in tweet_data["media"]):
            tweet_args.append({"video": "Yes"})
        i = 0
        media_links = []
        for media in tweet_data["media"]:
            if media["type"] != "photo":
                continue
            i += 1
            url = media["url"]
            extension = url.split(".")[-1]
            self.upload_file_to_commons(url, i, tweet_id, extension, username)
            filename = f"Twitter_{username}_{tweet_id}_{i}.{extension}"
            media_links.append(filename)
        if media_links:
            tweet_args.append({"media": ",".join(media_links)})

        return self.ARCHIVED_TWEET_TEMPLATE.format(self.concat_args(tweet_args))

    def save_archive_page(self, sunday):
        sunday_str = datetime.strftime(sunday, '%Y-%m-%d')
        output = ["{{TOCFlat}}", f"{{{{TwitterArchivePage|date={sunday_str}|is_redirect=No}}}}"]
        for day in self.all_days_in_week(sunday):
            if not self.is_sunday(day):
                self.create_redirect(sunday, day)
            day_str = datetime.strftime(day, '%Y-%m-%d')
            self.done_tweet_dates.append(day_str)
            output.append(f"\n== {day.strftime('%b %d')} ==")
            if day_str not in self.tweet_dates:
                continue
            for tweet_id, tweet_data in self.tweet_dates[day_str].items():
                output.append(self.make_one_tweet_output(tweet_id, tweet_data))
        try:
            self.site.save_title(title=f"Archive Twitter:{datetime.strftime(sunday, '%Y-%m-%d')}",
                                 text="\n".join(output),
                                 summary=self.SUMMARY)
        except RetriedLoginAndStillFailed:
            print(f"Skipping {datetime.strftime(sunday, '%Y-%m-%d')}")
            return
        print(f"Saved {datetime.strftime(sunday, '%Y-%m-%d')}")

    def insert_tweets(self, page, day):
        day_object = datetime.strptime(day, "%Y-%m-%d")
        day_short = day_object.strftime('%b %d')
        page = self.site.client.pages[page]
        page_text = page.text()
        for tweet_id, tweet_data in self.tweet_dates[day].items():
            page_text = page_text.replace(f"== {day_short} ==",
                                          f"== {day_short} ==\n{self.make_one_tweet_output(tweet_id, tweet_data)}")
        try:
            self.site.save(page=page,
                           text=page_text,
                           summary="Inserting new tweets")
            print(f"Inserting in {day}")
        except RetriedLoginAndStillFailed:
            print(f"Skipping {day}")
            return

    def make_archive_pages(self):
        for tweet_date in self.tweet_dates.keys():
            if tweet_date in self.done_tweet_dates:
                continue
            if self.is_tweet_date_in_cargo(tweet_date):
                self.insert_tweets(self.site.cache.get_target(f"Archive Twitter:{tweet_date}"), tweet_date)
            else:
                sunday = self.corresponding_sunday(tweet_date)
                self.save_archive_page(sunday)

    def is_tweet_date_in_cargo(self, tweet_date):
        response = self.site.cargo_client.query(
            tables="TwitterArchivePages=TAP",
            fields="TAP.PageDate",
            where=f"TAP.PageDate = '{tweet_date}'",
            limit=1
        )
        if not response:
            return False
        return True

    @staticmethod
    def cast_to_datetime(string):
        if type(string) == datetime:
            return string
        return datetime.strptime(string, "%Y-%m-%d")

    def is_sunday(self, day):
        if self.cast_to_datetime(day).weekday() == 6:
            return True
        return False

    def corresponding_sunday(self, day):
        day = self.cast_to_datetime(day)
        while True:
            if day.weekday() == 6:
                return day
            day -= timedelta(days=1)

    def all_days_in_week(self, sunday):
        sunday = self.cast_to_datetime(sunday)
        for i in range(7):
            yield sunday
            sunday += timedelta(days=1)

    def upload_file_to_commons(self, url, index, tweet_id, extension, username):
        image = requests.get(f"{url}?name=small").content
        with open(file=f"image.{extension}", mode="wb") as f:
            f.write(image)
        try:
            self.commons_site.upload(file=f"image.{extension}",
                                     filename=f"Twitter_{username}_{tweet_id}_{index}.{extension}",
                                     description="[[Category:Twitter Backup Images]]", ignore_warnings=True)
        except APIError as e:
            if e.code == "fileexists-no-change":
                pass
        os.remove(f"image.{extension}")


if __name__ == "__main__":
    credentials = AuthCredentials(user_file="bot")
    lol_site = EsportsClient("lol", credentials=credentials, max_retries=0, retry_interval=0)
    credentials_me = AuthCredentials(user_file="me")
    commons_site = EsportsClient("commons", credentials=credentials_me)
    TweetsBackup(lol_site, commons_site).run()
