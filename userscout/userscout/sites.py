"""Site definitions for UserScout.

Each site is a dict:
  name      display name
  url       profile URL template, {u} is the username
  category  rough grouping used in reports
  method    how existence is decided:
              status   -> HTTP 200 means found, 404 means not found
              absent   -> HTTP 200 and `text` is NOT in the body means found
              present  -> HTTP 200 and `text` IS in the body means found
              redirect -> found only if the final URL still contains `final`
  text      marker string(s) for absent/present methods
  check_url optional different URL used for the request (e.g. a JSON API)
  regex     optional username pattern the site accepts; others are skipped
  rank      popularity order, lower is more popular (used by --top)
"""

S = []


def add(name, url, category, method="status", text=None, check_url=None,
        regex=None, final=None):
    S.append({
        "name": name, "url": url, "category": category, "method": method,
        "text": text, "check_url": check_url, "regex": regex, "final": final,
        "rank": len(S) + 1, "fragile": False,
    })


# Social
add("GitHub", "https://github.com/{u}", "coding", check_url="https://api.github.com/users/{u}", regex=r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
add("Reddit", "https://www.reddit.com/user/{u}", "social", method="absent", text=["Sorry, nobody on Reddit goes by that name", "page not found"], check_url="https://old.reddit.com/user/{u}")
add("Telegram", "https://t.me/{u}", "social", method="present", text=["tgme_page_title"], regex=r"^[A-Za-z0-9_]{5,32}$")
add("Instagram", "https://www.instagram.com/{u}/", "social", method="present", text=["og:title"], regex=r"^[A-Za-z0-9._]{1,30}$")
add("X (Twitter)", "https://x.com/{u}", "social", method="present", text=["profile"], check_url="https://nitter.net/{u}", regex=r"^[A-Za-z0-9_]{1,15}$")
add("TikTok", "https://www.tiktok.com/@{u}", "social", method="present", text=["uniqueId"], regex=r"^[A-Za-z0-9._]{2,24}$")
add("YouTube", "https://www.youtube.com/@{u}", "video", regex=r"^[A-Za-z0-9._-]{3,30}$")
add("Twitch", "https://www.twitch.tv/{u}", "video", method="present", text=["og:title"], check_url="https://m.twitch.tv/{u}/profile", regex=r"^[A-Za-z0-9_]{4,25}$")
add("Pinterest", "https://www.pinterest.com/{u}/", "social", method="present", text=["pinterestapp:pins"], regex=r"^[A-Za-z0-9_]{3,30}$")
add("Snapchat", "https://www.snapchat.com/add/{u}", "social", regex=r"^[A-Za-z][A-Za-z0-9._-]{2,14}$")
add("Facebook", "https://www.facebook.com/{u}", "social", method="present", text=["entity_id"])
add("LinkedIn", "https://www.linkedin.com/in/{u}", "social", method="status")
add("Medium", "https://medium.com/@{u}", "blogging")
add("Steam", "https://steamcommunity.com/id/{u}", "gaming", method="absent", text=["The specified profile could not be found"])
add("Tumblr", "https://{u}.tumblr.com", "blogging", regex=r"^[A-Za-z0-9-]{1,32}$")
add("Vimeo", "https://vimeo.com/{u}", "video")
add("SoundCloud", "https://soundcloud.com/{u}", "music")
add("Spotify", "https://open.spotify.com/user/{u}", "music")
add("Flickr", "https://www.flickr.com/people/{u}", "photo")
add("DeviantArt", "https://www.deviantart.com/{u}", "art")
add("Behance", "https://www.behance.net/{u}", "art")
add("Dribbble", "https://dribbble.com/{u}", "art")
add("Quora", "https://www.quora.com/profile/{u}", "social")
add("Pastebin", "https://pastebin.com/u/{u}", "paste")
add("GitLab", "https://gitlab.com/{u}", "coding", check_url="https://gitlab.com/api/v4/users?username={u}", method="present", text=['"id"'])
add("Bitbucket", "https://bitbucket.org/{u}/", "coding")
add("Dev.to", "https://dev.to/{u}", "coding")
add("Hashnode", "https://hashnode.com/@{u}", "blogging")
add("Codeforces", "https://codeforces.com/profile/{u}", "coding")
add("LeetCode", "https://leetcode.com/{u}/", "coding", method="absent", text=["That page doesn"])
add("HackerRank", "https://www.hackerrank.com/{u}", "coding")
add("HackerOne", "https://hackerone.com/{u}", "security", method="absent", text=["Page not found"])
add("Bugcrowd", "https://bugcrowd.com/{u}", "security")
add("TryHackMe", "https://tryhackme.com/p/{u}", "security", method="absent", text=["User not found"])
add("Hack The Box", "https://app.hackthebox.com/users/{u}", "security", method="status")
add("Keybase", "https://keybase.io/{u}", "security", check_url="https://keybase.io/_/api/1.0/user/lookup.json?usernames={u}", method="absent", text=['"them":[null]'])
add("npm", "https://www.npmjs.com/~{u}", "coding")
add("PyPI", "https://pypi.org/user/{u}/", "coding")
add("Docker Hub", "https://hub.docker.com/u/{u}", "coding", check_url="https://hub.docker.com/v2/users/{u}/")
add("Replit", "https://replit.com/@{u}", "coding")
add("CodePen", "https://codepen.io/{u}", "coding")
add("Kaggle", "https://www.kaggle.com/{u}", "coding")
add("Gravatar", "https://gravatar.com/{u}", "social")
add("About.me", "https://about.me/{u}", "social")
add("Linktree", "https://linktr.ee/{u}", "social")
add("Patreon", "https://www.patreon.com/{u}", "social")
add("Ko-fi", "https://ko-fi.com/{u}", "social")
add("Buy Me a Coffee", "https://www.buymeacoffee.com/{u}", "social")
add("WordPress", "https://{u}.wordpress.com", "blogging", regex=r"^[A-Za-z0-9-]{3,60}$")
add("Blogger", "https://{u}.blogspot.com", "blogging", regex=r"^[A-Za-z0-9-]{3,60}$")
add("Substack", "https://{u}.substack.com", "blogging", regex=r"^[A-Za-z0-9-]{2,60}$")
add("Mastodon (mastodon.social)", "https://mastodon.social/@{u}", "social")
add("Bluesky", "https://bsky.app/profile/{u}.bsky.social", "social", check_url="https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor={u}.bsky.social")
add("Chess.com", "https://www.chess.com/member/{u}", "gaming", check_url="https://api.chess.com/pub/player/{u}")
add("Lichess", "https://lichess.org/@/{u}", "gaming", check_url="https://lichess.org/api/user/{u}")
add("Roblox", "https://www.roblox.com/user.aspx?username={u}", "gaming", check_url="https://users.roblox.com/v1/users/search?keyword={u}&limit=10", method="present", text=['"name":"{u}"'])
add("Minecraft (NameMC)", "https://namemc.com/profile/{u}", "gaming", check_url="https://api.mojang.com/users/profiles/minecraft/{u}", regex=r"^[A-Za-z0-9_]{3,16}$")
add("Xbox Gamertag", "https://xboxgamertag.com/search/{u}", "gaming")
add("Itch.io", "https://{u}.itch.io", "gaming", regex=r"^[A-Za-z0-9-]{2,40}$")
add("Speedrun.com", "https://www.speedrun.com/users/{u}", "gaming")
add("Bandcamp", "https://bandcamp.com/{u}", "music")
add("Mixcloud", "https://www.mixcloud.com/{u}/", "music")
add("Goodreads", "https://www.goodreads.com/{u}", "books")
add("Letterboxd", "https://letterboxd.com/{u}/", "video")
add("MyAnimeList", "https://myanimelist.net/profile/{u}", "gaming")
add("Wattpad", "https://www.wattpad.com/user/{u}", "blogging")
add("Product Hunt", "https://www.producthunt.com/@{u}", "social")
add("Hacker News", "https://news.ycombinator.com/user?id={u}", "social", method="absent", text=["No such user."])
add("Disqus", "https://disqus.com/by/{u}/", "social")
add("Imgur", "https://imgur.com/user/{u}", "photo")
add("500px", "https://500px.com/p/{u}", "photo")
add("Unsplash", "https://unsplash.com/@{u}", "photo")
add("Fiverr", "https://www.fiverr.com/{u}", "freelance")
add("Upwork", "https://www.upwork.com/freelancers/~{u}", "freelance")
add("Etsy", "https://www.etsy.com/shop/{u}", "shopping")
add("eBay", "https://www.ebay.com/usr/{u}", "shopping")
add("Slideshare", "https://www.slideshare.net/{u}", "social")
add("Scribd", "https://www.scribd.com/{u}", "social")
add("Gumroad", "https://{u}.gumroad.com", "shopping", regex=r"^[A-Za-z0-9-]{2,40}$")

add("Codeberg", "https://codeberg.org/{u}", "coding")
add("Lobsters", "https://lobste.rs/u/{u}", "social")
add("Hugging Face", "https://huggingface.co/{u}", "coding")
add("Wikipedia", "https://en.wikipedia.org/wiki/User:{u}", "social")
add("Gitee", "https://gitee.com/{u}", "coding")
add("Codewars", "https://www.codewars.com/users/{u}", "coding")
add("Duolingo", "https://www.duolingo.com/profile/{u}", "social", check_url="https://www.duolingo.com/2017-06-30/users?username={u}", method="present", text=['"id"'])


# Sites that sit behind a login wall, aggressive bot protection or rate limits.
# Results from them cannot be trusted from a typical script, so they are skipped
# unless --include-fragile is given, and any hit is labelled "unverified".
FRAGILE = {
    "Reddit", "Instagram", "X (Twitter)", "Facebook", "LinkedIn", "Pinterest",
    "Medium", "Twitch", "Spotify", "Behance", "Quora", "Hashnode", "Codeforces",
    "LeetCode", "HackerRank", "TryHackMe", "Hack The Box", "npm", "PyPI",
    "CodePen", "Kaggle", "Ko-fi", "Buy Me a Coffee", "WordPress", "Blogger",
    "Xbox Gamertag", "Speedrun.com", "Bandcamp", "Mixcloud", "Letterboxd",
    "Product Hunt", "Imgur", "500px", "Unsplash", "Fiverr", "Upwork", "Etsy",
    "eBay", "Slideshare", "Scribd", "Roblox",
}
for _s in S:
    _s["fragile"] = _s["name"] in FRAGILE
