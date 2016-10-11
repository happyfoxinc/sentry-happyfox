# Sentry-HappyFox

Create HappyFox tickets from your Sentry issues page. 

This plugin can be installed to your currently running Sentry instance by:

```
git clone https://github.com/happyfoxinc/sentry-happyfox
python setup.py install
sentry upgrade
```
Restart your sentry server after completing the above steps.

HappyFox Plugin can be found in the `Issue Tracking` section of your Project settings page. The Account URL, API Key and Auth Code have to be configured at first, after the credentials are verified, you can specify the category in which the tickets have to be created.

After the initial setup, in any issue's detail page, you can create a ticket by selecting HappyFox > Create a New Issue, and clicking Submit

