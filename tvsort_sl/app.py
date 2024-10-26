import json
import logging
import os
import traceback
from collections import Counter
from typing import Dict, Union, List

import daiquiri
import guessit
import patoolib

from tvsort_sl import utils, conf
from tvsort_sl.conf import BASE_DIR
from tvsort_sl.messages import send_email


PROCESS_RUNNING = 'Proses already running'
CONNECTION_ISSUE = 'HTTPConnectionPool'


class TvSort:
    project_name = 'tvsort_sl'
    settings: Dict[str, Union[str, bool]] = {
        "PROJECT_NAME": project_name, "LOG_PATH": os.path.join(BASE_DIR, "logs")
    }
    extensions: Dict[str, List[str]] = {}
    logger = None

    report: Dict[str, Union[Counter, List[str]]] = {"counters": Counter(), "errors": []}

    def __init__(self, is_test=False, **kwargs):
        self.create_logger(**kwargs)

        conf_files = conf.get_conf_file_name(is_test=is_test)
        response = utils.check_project_setup(self.settings, conf_files)
        self.process_response(response)
        if any(message[0] != 'info' for message in response):
            return

        conf.load_setting(self.settings, conf_files)
        conf.load_extensions(self.extensions)
        self.unsorted_path = self.settings.get('UNSORTED_PATH')

    def run(self):
        if utils.is_process_already_running(self.settings.get('DUMMY_FILE_PATH')):
            self.process_response([('error', PROCESS_RUNNING)])
            return

        try:
            utils.create_file(self.settings.get('DUMMY_FILE_PATH'))

            # Scan and Extract all compressed files
            self.scan_archives()

            # Scan and move/copy videos
            self.scan_videos()

            # UPDATE XBMC
            response = utils.update_xbmc(self.settings.get('KODI_IP'))
            self.process_response(response)

            # CLEAN UP
            for folder_path in utils.get_folders(self.unsorted_path):
                response = utils.delete_folder_if_empty(folder_path)
                self.process_response(response)

        # pylint: disable=broad-except
        except Exception as exception:
            self.process_response([('error', traceback.print_exc())])
            self.process_response([('error', str(exception))])

        finally:
            response = utils.delete_file(self.settings.get('DUMMY_FILE_PATH'))
            self.process_response(response)

        return

    def create_logger(self, log_level=logging.INFO):
        daiquiri.setup(
            outputs=(
                daiquiri.output.File(
                    directory=self.settings.get('LOG_PATH'),
                    program_name=self.project_name,
                ),
                daiquiri.output.STDOUT,
            )
        )

        daiquiri.getLogger(program_name=self.project_name).logger.level = log_level
        self.logger = daiquiri.getLogger(
            program_name=self.project_name, log_level=log_level
        )

    def scan_archives(self):
        for file_path in utils.get_files(self.unsorted_path):
            if utils.is_compressed(file_path, self.extensions):
                patoolib.extract_archive(
                    file_path, outdir=self.unsorted_path, verbosity=-1
                )
                self.process_response(['info', f'Extracting {file_path}'])
                response = utils.delete_file(file_path)
                self.process_response(response)

    def scan_videos(self):
        for file_path in utils.get_files(self.unsorted_path):
            self.process_response([('info', f'Checking file: {file_path}')])

            # Garbage
            if utils.is_garbage_file(file_path, self.extensions):
                response = utils.delete_file(file_path)
                self.process_response(response)
                continue

            video = guessit.guessit(
                file_path, options={'expected_title': ['This Is Us']}
            )
            new_path = None

            # Episode
            if utils.is_tv_show(video):
                title = video.get('title')
                if title == 'Season':
                    title = video.get('episode_title')

                show_name = utils.transform_to_path_name(title)
                utils.add_missing_country(video, show_name)
                if video.get('country'):
                    show_name += f'.{video.get("country")}'

                new_path = os.path.join(self.settings.get('TV_PATH'), show_name)
                response = utils.create_folder(new_path)
                self.process_response(response)

            # Movie
            elif utils.is_movie(video):
                new_path = self.settings.get('MOVIES_PATH')

            # Copy / Move the video file
            response = utils.copy_file(
                file_path, new_path, move_file=self.settings.get('MOVE_FILES')
            )
            self.process_response(response)

    @staticmethod
    def if_info_log(msg_type):
        return msg_type == 'info'

    @staticmethod
    def if_error_log(msg_type):
        return msg_type == 'error'

    def process_info_messages(self, msg_text):
        self.logger.info(msg_text)
        if 'Removing file' in msg_text:
            self.report.get('counters')['delete'] += 1
        elif any(text in msg_text for text in ['Moving file', 'Copying file']):
            self.report.get('counters')['move_or_copy'] += 1

    def process_error_messages(self, msg_text):
        self.logger.error(msg_text)
        if msg_text not in self.report.get('errors'):
            self.report.get('errors').append(msg_text)

    def process_response(self, response):
        if not response:
            return

        for messages in response:
            msg_type, msg_text = messages

            if self.if_info_log(msg_type):
                self.process_info_messages(msg_text)

            elif self.if_error_log(msg_type):
                self.process_error_messages(msg_text)

    def is_send_report(self):
        if self.report.get('counters'):
            errors = self.report.get('errors')
            if errors:
                return any(
                    x != PROCESS_RUNNING and CONNECTION_ISSUE not in x for x in errors
                )

        return False

    def email_report(self):
        if self.is_send_report():
            subject = 'TV sort report'
            content = json.dumps(self.report)
            return send_email(subject=subject, content=content)

        return None


if __name__ == "__main__":
    tv_sort = TvSort()
    tv_sort.run()
    tv_sort.email_report()
