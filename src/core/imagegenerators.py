from imagekit import (
    ImageSpec,
    processors,
    register,
    )


class HeaderThumbnail(ImageSpec):
    """Header Thumbnail."""

    processors = [
        processors.ResizeToFill(30, 30),
        processors.Adjust(contrast=1.1, sharpness=1.1),
    ]
    format = "JPEG"
    options = {"quality": 80}


class iFrameThumbnail(ImageSpec):
    """iFrame Thumbnail."""

    processors = [
        processors.ResizeToFill(32, 32),
        processors.Adjust(contrast=1.1, sharpness=1.1),
    ]
    format = "JPEG"
    options = {"quality": 80}


class Thumbnail(ImageSpec):
    """Thumbnail."""

    processors = [
        processors.ResizeToFill(100, 100),
        processors.Adjust(contrast=1.1, sharpness=1.1),
    ]
    format = "JPEG"
    options = {"quality": 80}


class ThumbnailWide(ImageSpec):
    """Thumbnail wide."""

    processors = [
        processors.ResizeToFill(150, 100),
        processors.Adjust(contrast=1.1, sharpness=1.1),
    ]
    format = "JPEG"
    options = {"quality": 80}


class ThumbnailBig(ImageSpec):
    """Thumbnail big."""

    processors = [
        processors.ResizeToFill(150, 150),
        processors.Adjust(contrast=1.1, sharpness=1.1),
    ]
    format = "JPEG"
    options = {"quality": 80}


class ThumbnailBigger(ImageSpec):
    """Thumbnail bigger."""

    processors = [
        processors.ResizeToFill(200, 200),
        processors.Adjust(contrast=1.1, sharpness=1.1),
    ]
    format = "JPEG"
    options = {"quality": 80}


class AvatarThumbnail(ImageSpec):
    """Avatar Thumbnail."""

    processors = [
        processors.ResizeToFill(80, 80),
        processors.Adjust(contrast=1.1, sharpness=1.1),
    ]
    format = "JPEG"
    options = {"quality": 80}


class MediumFill(ImageSpec):
    """Medium fill."""

    processors = [
        processors.ResizeToFill(400, 400)
    ]
    format = "JPEG"
    options = {"quality": 80}


class MediumFillWide(ImageSpec):
    """Medium fill wide."""

    processors = [
        processors.ResizeToFill(600, 400)
    ]
    format = "JPEG"
    options = {"quality": 80}


class MediumFit(ImageSpec):
    """Medium fit."""

    processors = [
        processors.ResizeToFit(400, 400)
    ]
    format = "JPEG"
    options = {"quality": 80}


class Large(ImageSpec):
    """Large."""

    processors = [
        processors.ResizeToFit(960, 960)
    ]
    format = "JPEG"
    options = {"quality": 80}


class GiantFillWide(ImageSpec):
    """Giant fill wide."""

    processors = [
        processors.ResizeToFill(1600, 400)
    ]
    format = "JPEG"
    options = {"quality": 80}


class GiantFitWide(ImageSpec):
    """Giant fill wide."""

    processors = [
        processors.ResizeToFit(1600, 400)
    ]
    format = "JPEG"
    options = {"quality": 80}


register.generator("header:thumbnail", HeaderThumbnail)
register.generator("iframe:thumbnail", iFrameThumbnail)
register.generator("common:thumbnail", Thumbnail)
register.generator("common:thumbnail_wide", ThumbnailWide)
register.generator("common:thumbnail_big", ThumbnailBig)
register.generator("common:thumbnail_bigger", ThumbnailBigger)
register.generator("common:avatar_thumbnail", AvatarThumbnail)
register.generator("common:medium_fill", MediumFill)
register.generator("common:medium_fill_wide", MediumFillWide)
register.generator("common:medium_fit", MediumFit)
register.generator("common:large", Large)
register.generator("common:giant_fill_wide", GiantFillWide)
register.generator("common:giant_fit_wide", GiantFitWide)
