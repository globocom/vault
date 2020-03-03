# Vault

## OAuth2

### Registering a new provider

To register an OAuth2 provider, go to `/admin/allaccess/provider/` and click on "Add Provider". Then, fill out the provider's name (ex: 'google', 'facebook' etc), its URLs, its Client ID and its Client Secret. After doing that, users can already authenticate using that new provider.

### Common provider URLs

In case you want to add one of the following providers, we've listed their URLs here. You'll just need to generate the Client ID and Client Secret on those services.

||google|
|---|---|
|Authorization URL|https://accounts.google.com/o/oauth2/v2/auth|
|Access Token URL|https://accounts.google.com/o/oauth2/token|
|Profile URL|https://www.googleapis.com/oauth2/v1/userinfo|

||facebook|
|---|---|
|Authorization URL|https://www.facebook.com/v2.8/dialog/oauth|
|Access Token URL|https://graph.facebook.com/v2.8/oauth/access_token|
|Profile URL|https://graph.facebook.com/v2.8/me?fields=email,name|

### Adding scope for a provider

It's possible that a provider will require a `scope` parameter to deliver the e-mail of the authenticated user. This has already been set for Facebook and Google providers, but if you need to add a different provider that requires that, you can add it in the `OAuthVaultRedirect` class in vault/views.py as per [django-all-access's documentation](https://django-all-access.readthedocs.io/en/v0.5.X/customize-views.html#additional-scope-example).
