# twitch-creamery
a twitch-bot for the homies and I to entertain and amuse

## setup

1. Make an account on Twitch for your bot. Its more common than using your actual account.
1. Register an app with Twitch dev under your bot account, https://dev.twitch.tv/console/apps/create , and request a client-id so you can interface with Twitch's API
1. Also, generate the client-secret of the application too.

## code

1. Python 3.x(3.6+): https://www.python.org/downloads/
1. Open a shell on your system: bash, iterm, cmd.exe
1. run `pip install pipenv`
1. change directory to where this project resides: cd ~/your/project/path, or even cd C:\your\project\path
1. now execute `pipenv sync` to sync your local env with the dependencies of this project

## env file

Create a file next to bot.py called ".env" and populate it with your credentials.

See .env.example for reference on what is required and available.

For bot `CLIENT_ID` and `CLIENT_SECRET` the naming convention is:

```shell
YOUR_BOT_NAME_CLIENT_ID= ...
YOUR_BOT_NAME_CLIENT_SECRET= ...
```

## run

```shell
 > cd path\to\code\directory
 path\to\code\directory\> pipenv run python bot.py
```

### default values

The code contains several default values when retrieving environment variables.

Note for coders: this file is in the .gitignore so that nobody accidentally pushes their secrets to the remote repository.

## yaml

Bots are configured with Cogs and other details through a YAML file, default being `bots.yaml`.

An example has been generated for you, called `bots.example.yaml`

```
bot_name:
	prefix: !      # how the bot recognizes commands
	channels:      # list of twitch channels the bot will join
	-   channel_1
	cogs:          # cogs is a list of the cogs the bot will use
	-   cog_name_1 # the name of the cog matching their filenames in the cogs/ directory
	scopes:
	-   all_scopes # if you want to request all possible scopes (default if not specified)
	-   chat:read  # an example of a single scope one could list. See AuthScopes in oauth/user.py
```

cogs are to be placed in the "cogs" directory to be found when parsing the above YAML.

## pubsub how-to

Pubsub is analogous to channel point redemptions, moderator actions, and bit events. At some point, whispers and subscriptions, too.

These features have been implemented as a Cog to be integrated into a bot, like any other, except it requires a unique setup. You are probably now familiar with your API Client credentials being used to generate access and refresh tokens via the OAuth2 Authorization Code Flow, whereby the bot requests permission to act on behalf of your bot's Twitch account. Channel points, bits, and other pubsub events require another user token; that of the owner of the channel to which your bot is "subscribing" to the "publications" (i.e. pubsub).

To make a bot that captures pubsub for a channel one needs to do the following:

* A channel's owner must generate a user access token and provide it. not a bot account; the actual channel where the streams will happen. It might authorize the following permissions, but not all are required.

```
bits:read
channel:read:redemptions
moderator:read:automod_settings
moderator:manage:automod_settings
moderator:manage:banned_users
moderator:read:blocked_terms
moderator:manage:blocked_terms
moderator:read:chat_settings
moderator:manage:chat_settings
```

* Add a bot configuration to bots.yaml like this

```yaml
pubsub:
   cogs:
   -   pubsub
   channels:
   -   thatsamorais
   scopes:
   -   all_scopes
```

* Add the channel name to the `channels` list in the bot's yaml config
* Add an environment variable composed of the channel's name in all caps followed by `_PUBSUB_TOKEN` containing this token, into `.env`, i.e. `CHANNEL_NAME_PUBSUB_TOKEN=user's token`

If you see BADAUTH error codes being emitted, ensure that the token has the correct permissions

## EventSub

Event Subscribing, or EventSub, is a webhook pattern where the bot informs twitch of what signals the bot would like to be sent a request to be notified when they happen.

 |Your Bot| --- subscribe to channel subscriptions ->  |Twitch Webhook Registry|

The subscription request sent to Twitch contains a callback url which MUST be served over TLS, i.e. https.

Note that the EventSub bot MUST be authorized with the target channel's login, not your bot account login. It has to do with the required authorizations to subscribe to these webhooks.

```
https://subdomain.your-domain.com/callback
```

Therefore messages are sent as follows

 |Twitch Webhook Sender| --- POST /callback {event data} -> |DNS| -> |Your Bot HTTP endpoint|

For Twitch to reach your bot server host, which could be running on your local machine or in cloud provider, the machine's IP must be public-facing. 

While you can easily achieve a public facing HTTP endpoint over TLS by hosting a bot in a cloud resource, these solutions can entail tradeoffs since they are on a remote machine. Maybe you do not want to pay for the usage, either. There is another way that requires some setup if one is willing...

### Dynamic DNS with Namecheap

You can use whatever site you want to rent your domain, but because Namecheap has amazing documentation for how to setup Dynamic DNS entries, I have gone that route.

The document linked in the first step, below, describes how to setup a host for dynamic DNS in Namecheap's SaaS UI. Of the ~3 options they present, I prefer the subdomain option, i.e. `subdomain.your-domain.com`. One can be made exclusively for Twitch to keep things tidy.

1. [How do I set up a Host for Dynamic DNS?](https://www.namecheap.com/support/knowledgebase/article.aspx/43/11/how-do-i-set-up-a-host-for-dynamic-dns/) Easy, right? Now to test...
1. [How to dynamically update the host's IP with an HTTP request?](https://www.namecheap.com/support/knowledgebase/article.aspx/29/11/how-to-dynamically-update-the-hosts-ip-with-an-http-request/) One can test this by grabbing the Dynamic DNS password and calling the "update" url with the host, domain, password, and ip parameters. Plugging it into a browser is good enough. Until you see something like the following in response, then check the parameters:

URL:
```
https://dynamicdns.park-your-domain.com/update?host=subdomain&domain=your-domain.com&password=pword&ip=127.0.0.2
```

Response:
```
<?xml version="1.0" encoding="utf-16"?>
<interface-response>
  <Command>SETDNSHOST</Command>
  <Language>eng</Language>
  <IP>127.0.0.2</IP>
  <ErrCount>0</ErrCount>
  <errors />
  <ResponseCount>0</ResponseCount>
  <responses />
  <Done>true</Done>
  <debug><![CDATA[]]></debug>
</interface-response>
```
Error free, and easy. Based on the Namecheap UI displaying the configuration, we now know that the IP can be dynamically assigned.

Next, is to automate this with `ddclient`, the Dynamic DNS client. Download it here:

Linux: https://ddclient.net/#installation

Windows:

Beware what you might download from the internet claiming to be a ddclient for Windows. You might have noticed that Namecheap gave you the option when you enabled Dynamic DNS to download a zip file with a ddclient exe. If you are using another provider then consult with them about what they recommend. I trust Namecheap more than a random app from an internet search. 

There is also Dynu.com: https://www.dynu.com/en-US/Resources/Downloads . Good luck going this route, and please send a PR if you try this containing your documentation. 

From here, your path may differ if not using ddclient on Linux, but the fundamentals are the same.

[How do I configure DDClient?](https://www.namecheap.com/support/knowledgebase/article.aspx/583/11/how-do-i-configure-ddclient/)

The supplied configuration can go directly into `/etc/ddclient.conf` but modified with the values of your setup.

Example `ddclient.conf`:
```
use=web, web=dynamicdns.park-your-domain.com/getip
protocol=namecheap
server=dynamicdns.park-your-domain.com
login=yourdomain.com
password=y0urpw0rd
subdomain
```

Then just run the ddclient in daemon mode:

```
/usr/sbin/ddclient -daemon 300 -syslog
```

You can set this up to run automatically on your machine by adding it to your startup. Otherwise, do not forget to have an updated IP address in your Dynamic DNS record where twitch can reach your service.

Having run the ddclient daemon, or whatever client you used, you will notice that what was previously set to `127.0.0.2` by our test, is now set to your current IP. If not, check that your config params match your URL that previously worked.

What we need next is TLS. If I have not lost you, yet, then congratulations because we're almost there. Nobody said this is simple, but you, unlike those who "want" event subscriptions in their bot, have decided to have event subscriptions in your bot. Now, let's setup nginx and get a certificate installed.

### Setting up nginx

We need our service to support TLS, and this can be achieved with a reverse proxy.

Also worth pointing out why we must do this; Twitchio does not support TLS. This is reasonable because it allows us to choose the solution we want. 

The solution being chosen for this project is `nginx`: https://nginx.org/en/ . Yet, you may use whatever proxy you want.

Linux:

```
sudo apt install nginx
```

The nginx beginner's guide if you please: https://nginx.org/en/docs/beginners_guide.html

The nginx.conf may be in /usr/local/nginx, /etc/nginx/, or /usr/local/etc/nginx depending on your distribution.

Windows:

See this document for how to get it setup: [https://nginx.org/en/docs/windows.html]. Locate the nginx.conf file in the installation directory. Please correct me if wrong.

Test that you see the nginx page when you visit `localhost` in a browser. With a reachable proxy, the certbot can be installed.

Next, the server must be added to `nginx.conf`. 

Below is a config for a domain with dynamic DNS that has a `/callback` endpoint. this goes within the `http` section.

```
http {
	...
	server {
	listen 80;
	server_name subdomain.yourdomain.com;
		location /callback {
			proxy_pass http://127.0.0.1:8080;
		}
	}
	...
}
```

After modifying the configuration you must restart nginx

```
sudo nginx -s reload
```

If you would like, change the port number on proxy_pass. It might not be easy to tell if this is ultimately working, but nginx should be running without errors, and this location should not produce a 404, rather a 502 since the server is not responding.

### Installing certificates with Namecheap

A good starting point for this discussion is: https://certbot.eff.org/ .

From https://certbot.eff.org/instructions, there are some options presented. In our case we want to select `nginx` under "Software" and your OS under "System". Following the instructions presented here is helpful, and it also contains some helpful context around what is being done. Drink that in, and you'll find yourself at the step where we install certbot into nginx. For Linux it looks like: 

```
sudo certbot --nginx
```

### This went horribly wrong

There are things that can be determined to be 

### Cert installation

One must now install the certificate as well. Upon visiting their [comprehensive list of providers](https://certbot.eff.org/hosting_providers) and their support for automatic certificate generation, it informed me of a Namecheap tutorial. So, first ensure that your domain provider is not among those who can provide this for you. You may even find a link to the documentation for your provider that might be helpful.

Now that I have generated the certificate, it needs to be installed, and I am following some instructions linked, here: https://www.namecheap.com/support/knowledgebase/article.aspx/9418/33/installing-an-ssl-certificate-on-your-server-using-cpanel/

At this point all the pieces should be in place. Please do post issues of your experiences with this.

...

## documentation

github: https://github.com/perplexistential/twitch-creamery

TwitchIO:
1. twitchio: https://twitchio.readthedocs.io/en/latest/index.html
2. github: https://github.com/TwitchIO/TwitchIO

PubSub:
1. twitch pubsub API docs: https://dev.twitch.tv/docs/pubsub#topics
1. twitchio: https://twitchio.readthedocs.io/en/latest/exts/pubsub.html

Routines:
	1. twitchio: https://twitchio.readthedocs.io/en/latest/exts/routines.html
