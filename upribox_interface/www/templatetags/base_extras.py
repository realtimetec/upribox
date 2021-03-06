__author__ = 'julian'
from django import template
from django.core.urlresolvers import reverse
from lib import utils
from django.utils import timezone
import math
from django.utils.translation import gettext as _
from netaddr import EUI

register = template.Library()


@register.simple_tag
def navactive(request, urls):
    if request.path in (reverse(url) for url in urls.split()):
        return "active"
    return ""


@register.assignment_tag
def onpage(request, urls):
    if request.path in (reverse(url) for url in urls.split()):
        return True
    return False


@register.assignment_tag
def vpn_link_valid(profile):
    return profile.download_slug is not None and profile.download_valid_until is not None and profile.download_valid_until >= timezone.now()


@register.assignment_tag
def get_fact(role, group, fact):
    return utils.get_fact(role, group, fact)


@register.simple_tag
def seconds_until(d):
    s = (d - timezone.now()).total_seconds()
    return s if s > 0 else 0


@register.filter()
def format_seconds_until(d):
    s = round((d - timezone.now()).total_seconds())
    if s <= 0:
        return _("abgelaufen")
    else:
        mins = math.floor(s / 60)
        secs = math.floor(s - (mins * 60))
        return "%02d:%02d" % (mins, secs)


IGNORE = [None, '-']


@register.filter
def get_device_name(device):
    mac_vendor = None
    try:
        mac_vendor = EUI(device.mac).oui.registration().org
    except Exception:
        pass

    names = [device.hostname]
    if device.user_agent.filter(model__isnull=False).first():
        names.append(device.user_agent.filter(model__isnull=False).first().model)
    names.extend([mac_vendor, device.mac])
    try:
        return device.chosen_name or filter(lambda x: x not in IGNORE, names)[0]
    except IndexError:
        return None


@register.assignment_tag
def get_device_names(device):
    mac_vendor = None
    try:
        mac_vendor = EUI(device.mac).oui.registration().org
    except Exception:
        pass

    elems = [device.hostname]
    elems.extend([x.model for x in device.user_agent.all()])
    elems.append(mac_vendor)
    elems.append(device.mac)
    names = []
    # make unique sorted list
    [names.append(x) for x in elems if x not in names]

    return filter(lambda x: x not in IGNORE, names)

@register.filter
def has_pw_field(form):
    for field in form:
        if field.field.widget.input_type == "password":
            return True
    return False
