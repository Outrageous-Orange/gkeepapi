# -*- coding: utf-8 -*-
"""
.. moduleauthor:: Kai <z@kwi.li>
"""

__version__ = '0.11.5'

import logging
import re

logger = logging.getLogger(__name__)

try:
    Pattern = re._pattern_type  # pylint: disable=protected-access
except AttributeError:
    Pattern = re.Pattern  # pylint: disable=no-member

from . import exception
from . import node
from .keep import Keep
from .node import Node
from .apis.api import API
from .apis.api_auth import APIAuth
from .apis.keep_api import KeepAPI
from .apis.media_api import MediaAPI
from .apis.reminders_api import RemindersAPI
