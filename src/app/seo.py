from djangoseo import seo


class Metadata(seo.Metadata):
    """SEO Metadata."""

    title = seo.Tag(
        head=True,
        max_length=68)
    description = seo.MetaTag(
        max_length=155)
    keywords = seo.KeywordTag()
    heading = seo.Tag(
        name="h1")

    class Meta:
        # use_sites = True
        use_cache = True
        # use_i18n = True
        groups = {
            "optional": ["heading", ]
        }
        seo_models = [
            "accounts",
            "blog",
            "challenges",
            "foro",
            "home",
            "organizations",
        ]
        seo_views = [
            "accounts",
            "blog",
            "challenges",
            "foro",
            "home",
            "organizations",
        ]
        backends = [
            "path",
            "modelinstance",
            "model",
            "view",
        ]
        verbose_name = "SEO Metadata"
        verbose_name_plural = "SEO Metadata"
