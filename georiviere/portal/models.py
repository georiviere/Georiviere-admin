from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.gis.db.models import PolygonField
from django.db import models

from django.utils.translation import gettext_lazy as _

from geotrek.common.mixins import TimeStampedModelMixin

from georiviere.portal.validators import validate_bounds


class MapBaseLayer(models.Model):
    label = models.CharField(max_length=50, unique=True)
    order = models.PositiveSmallIntegerField(default=0)
    url = models.CharField(max_length=255, blank=True, help_text=_("URL"))
    min_zoom = models.PositiveSmallIntegerField(default=0)
    max_zoom = models.PositiveSmallIntegerField(default=22)
    attribution = models.CharField(max_length=255, blank=True,
                                   help_text=_("Attribution of the baselayer. Example : © OpenStreetMap"))
    bounds = models.CharField(max_length=255, blank=True, help_text=_("Bounds"), validators=[validate_bounds])

    class Meta:
        verbose_name = _("Map base layer")
        verbose_name_plural = _("Map base layers")
        ordering = ('label',)

    def __str__(self):
        return self.label


class MapGroupLayer(models.Model):
    label = models.CharField(max_length=50)
    order = models.PositiveSmallIntegerField(default=0)
    portal = models.ForeignKey('portal.Portal',
                               verbose_name=_("Portal"), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Map group")
        verbose_name_plural = _("Map groups")
        ordering = ('label',)
        unique_together = ('label', 'portal')

    def __str__(self):
        return self.label


class MapLayer(models.Model):
    label = models.CharField(max_length=50)
    layer_type = models.CharField(blank=False,
                                  verbose_name=_("Layer type"),
                                  max_length=50, editable=False)
    group_layer = models.ForeignKey('portal.MapGroupLayer',
                                    verbose_name=_("Map group layers"), related_name='layers',
                                    on_delete=models.SET_NULL, null=True, blank=True)
    portal = models.ForeignKey('portal.Portal',
                               verbose_name=_("Portal"), blank=True, related_name='layers', on_delete=models.PROTECT)
    default_active = models.BooleanField(default=False)
    style = models.JSONField(max_length=300, null=False, blank=True, default=dict, help_text=_("Style of the layer"))
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _("Map layer")
        verbose_name_plural = _("Map layers")
        ordering = ('label',)
        unique_together = ('label', 'order', 'group_layer')

    def __str__(self):
        return self.label


class Portal(TimeStampedModelMixin, models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=50, unique=True, help_text=_("Name of the portal"))
    website = models.URLField(verbose_name=_("Website"), max_length=256, unique=True)
    title = models.CharField(verbose_name=_("Title"), max_length=50, help_text=_("Title on Georiviere"),
                             default='')
    description = models.TextField(verbose_name=_("Description"), help_text=_("Description on Georiviere"),
                                   default='')
    main_color = ColorField(verbose_name=_("Main color"), default='#444444',
                            help_text=_("Main color"))
    map_base_layers = models.ManyToManyField('portal.MapBaseLayer', verbose_name=_("Map base layers"))
    min_zoom = models.PositiveSmallIntegerField(default=0)
    max_zoom = models.PositiveSmallIntegerField(default=22)
    spatial_extent = PolygonField(srid=settings.SRID, null=True)

    class Meta:
        verbose_name = _("Portal")
        verbose_name_plural = _("Portals")
        ordering = ('name',)

    def __str__(self):
        return self.name
