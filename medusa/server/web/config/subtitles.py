# coding=utf-8

"""Configure Subtitle searching."""

from __future__ import unicode_literals

import os

from medusa import (
    app,
    config,
    logger,
    subtitles,
    ui,
)
from medusa.server.web.config.handler import Config
from medusa.server.web.core import PageTemplate

from tornroutes import route


@route('/config/subtitles(/?.*)')
class ConfigSubtitles(Config):
    """
    Handler for Subtitle Search configuration
    """
    def __init__(self, *args, **kwargs):
        super(ConfigSubtitles, self).__init__(*args, **kwargs)

    def index(self):
        """
        Changed to a Vue Route.
        """
        return PageTemplate(rh=self, filename='index.mako').render()

    def saveSubtitles(self, use_subtitles=None, subtitles_plugins=None, subtitles_languages=None, subtitles_dir=None, subtitles_perfect_match=None,
                      service_order=None, subtitles_history=None, subtitles_finder_frequency=None, subtitles_erase_cache=None,
                      subtitles_multi=None, embedded_subtitles_all=None, subtitles_extra_scripts=None, subtitles_pre_scripts=None, subtitles_hearing_impaired=None,
                      addic7ed_user=None, addic7ed_pass=None, legendastv_user=None, legendastv_pass=None, opensubtitles_user=None, opensubtitles_pass=None,
                      subtitles_keep_only_wanted=None, embedded_subtitles_unknown_lang=None, subtitles_stop_at_first=None):
        """
        Save Subtitle Search related settings
        """
        results = []

        config.change_SUBTITLES_FINDER_FREQUENCY(subtitles_finder_frequency)
        app._init_scheduler(
            app_prop='USE_SUBTITLES',
            scheduler='subtitles_finder_scheduler',
            enabled=config.checkbox_to_value(use_subtitles)
        )
        app.SUBTITLES_ERASE_CACHE = config.checkbox_to_value(subtitles_erase_cache)
        app.SUBTITLES_LANGUAGES = [code.strip() for code in subtitles_languages.split(',') if code.strip() in subtitles.subtitle_code_filter()] if subtitles_languages else []
        app.SUBTITLES_DIR = subtitles_dir
        app.SUBTITLES_PERFECT_MATCH = config.checkbox_to_value(subtitles_perfect_match)
        app.SUBTITLES_HISTORY = config.checkbox_to_value(subtitles_history)
        app.IGNORE_EMBEDDED_SUBS = config.checkbox_to_value(embedded_subtitles_all)
        app.ACCEPT_UNKNOWN_EMBEDDED_SUBS = config.checkbox_to_value(embedded_subtitles_unknown_lang)
        app.SUBTITLES_STOP_AT_FIRST = config.checkbox_to_value(subtitles_stop_at_first)
        app.SUBTITLES_HEARING_IMPAIRED = config.checkbox_to_value(subtitles_hearing_impaired)
        app.SUBTITLES_MULTI = 1 if len(app.SUBTITLES_LANGUAGES) > 1 else config.checkbox_to_value(subtitles_multi)
        app.SUBTITLES_KEEP_ONLY_WANTED = config.checkbox_to_value(subtitles_keep_only_wanted)
        app.SUBTITLES_EXTRA_SCRIPTS = [x.strip() for x in subtitles_extra_scripts.split('|') if x.strip()]
        app.SUBTITLES_PRE_SCRIPTS = [x.strip() for x in subtitles_pre_scripts.split('|') if x.strip()]

        # Subtitles services
        services_str_list = service_order.split()
        subtitles_services_list = []
        subtitles_services_enabled = []
        for cur_service_str in services_str_list:
            cur_service, cur_enabled = cur_service_str.split(':')
            subtitles_services_list.append(cur_service)
            subtitles_services_enabled.append(int(cur_enabled))

        app.SUBTITLES_SERVICES_LIST = subtitles_services_list
        app.SUBTITLES_SERVICES_ENABLED = subtitles_services_enabled

        app.ADDIC7ED_USER = addic7ed_user or ''
        app.ADDIC7ED_PASS = addic7ed_pass or ''
        app.LEGENDASTV_USER = legendastv_user or ''
        app.LEGENDASTV_PASS = legendastv_pass or ''
        app.OPENSUBTITLES_USER = opensubtitles_user or ''
        app.OPENSUBTITLES_PASS = opensubtitles_pass or ''

        app.instance.save_config()
        # Reset provider pool so next time we use the newest settings
        subtitles.get_provider_pool.invalidate()

        if results:
            for x in results:
                logger.log(x, logger.ERROR)
            ui.notifications.error('Error(s) Saving Configuration',
                                   '<br>\n'.join(results))
        else:
            ui.notifications.message('Configuration Saved', os.path.join(app.CONFIG_FILE))

        return self.redirect('/config/subtitles/')
