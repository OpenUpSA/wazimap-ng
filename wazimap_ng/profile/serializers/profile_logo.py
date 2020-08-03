from .. import models

def ProfileLogoSerializer(profile):
    try:
        logo = models.Logo.objects.get(profile=profile)
        url = logo.url if logo.url and logo.url.strip() != "" else "/"
        return {
            "image": f"{logo.logo.url}",
            "url": url
        }
    except models.Logo.DoesNotExist:
        return {
            "image": "",
            "url": "/"
        }
