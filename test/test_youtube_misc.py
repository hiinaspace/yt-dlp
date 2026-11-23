#!/usr/bin/env python3

# Allow direct execution
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from yt_dlp.extractor import YoutubeIE
from yt_dlp.extractor.youtube._base import YoutubeBaseInfoExtractor


class TestYoutubeMisc(unittest.TestCase):
    def test_youtube_extract(self):
        assertExtractId = lambda url, video_id: self.assertEqual(YoutubeIE.extract_id(url), video_id)
        assertExtractId('http://www.youtube.com/watch?&v=BaW_jenozKc', 'BaW_jenozKc')
        assertExtractId('https://www.youtube.com/watch?&v=BaW_jenozKc', 'BaW_jenozKc')
        assertExtractId('https://www.youtube.com/watch?feature=player_embedded&v=BaW_jenozKc', 'BaW_jenozKc')
        assertExtractId('https://www.youtube.com/watch_popup?v=BaW_jenozKc', 'BaW_jenozKc')
        assertExtractId('http://www.youtube.com/watch?v=BaW_jenozKcsharePLED17F32AD9753930', 'BaW_jenozKc')
        assertExtractId('BaW_jenozKc', 'BaW_jenozKc')

    def test_extract_relative_time(self):
        ert = YoutubeBaseInfoExtractor.extract_relative_time

        # Abbreviated forms must equal their long-form equivalents.
        self.assertEqual(ert('5d ago'), ert('5 days ago'))
        self.assertEqual(ert('1mo ago'), ert('1 month ago'))
        self.assertEqual(ert('2mo ago'), ert('2 months ago'))
        self.assertEqual(ert('1y ago'), ert('1 year ago'))
        self.assertEqual(ert('1yr ago'), ert('1 year ago'))
        self.assertEqual(ert('3w ago'), ert('3 weeks ago'))
        self.assertEqual(ert('3wk ago'), ert('3 weeks ago'))

        self.assertIsNotNone(ert('30s ago'))
        self.assertIsNotNone(ert('30sec ago'))
        self.assertIsNotNone(ert('10min ago'))
        self.assertIsNotNone(ert('5h ago'))
        self.assertIsNotNone(ert('5hr ago'))

        self.assertIsNotNone(ert('today'))
        self.assertIsNotNone(ert('yesterday'))
        self.assertIsNotNone(ert('now'))

        self.assertEqual(ert('5 days ago'), ert('5 day ago'))

        self.assertIsNotNone(ert('streamed 6 days ago'))
        self.assertIsNotNone(ert('5 seconds ago (edited)'))
        self.assertIsNotNone(ert('updated today'))
        self.assertIsNotNone(ert('8 yr ago'))

        self.assertIsNone(ert('not a date string'))
        self.assertIsNone(ert(''))

        # Small safety check to prevent "drift".
        for unit in YoutubeBaseInfoExtractor._RELATIVE_TIME_UNIT_MAP:
            self.assertIsNotNone(ert(f'1 {unit} ago'), f'unit {unit!r} did not parse')

    def test_extract_loudness(self):
        def pr(config, client=None):
            data = {'playerConfig': {'audioConfig': config}} if config is not None else {}
            if client:
                data['streamingData'] = {'__yt_dlp_innertube_context': {'client': {'clientName': client}}}
            return data

        extract = YoutubeIE._extract_loudness
        # Values recorded from 51GIxXFKbzk and jNQXAC9IVRw
        yamero = {'trackAbsoluteLoudnessLkfs': -6.8400002, 'loudnessTargetLkfs': -14, 'loudnessDb': 7.1599998}
        self.assertEqual(extract([pr(yamero, 'WEB')]), {
            'loudness_lkfs': -6.8400002,
            'loudness_target_lkfs': -14.0,
            'loudness_over_target_db': 7.1599998,
        })
        self.assertEqual(extract([pr({'trackAbsoluteLoudnessLkfs': -23.67, 'loudnessTargetLkfs': -14})]), {
            'loudness_lkfs': -23.67,
            'loudness_target_lkfs': -14.0,
            'loudness_over_target_db': None,
        })
        # Absent data: no fields
        self.assertEqual(extract([pr(None, 'WEB'), {}]), {})
        self.assertEqual(extract([pr({'loudnessTargetLkfs': -14})]), {})
        self.assertEqual(extract([]), {})
        # Web values win over other clients, whatever the order
        other = {'trackAbsoluteLoudnessLkfs': -9.0, 'loudnessTargetLkfs': -14}
        self.assertEqual(extract([pr(other, 'IOS'), pr(yamero, 'WEB')])['loudness_lkfs'], -6.8400002)
        self.assertEqual(extract([pr(other, 'IOS'), pr(yamero)])['loudness_lkfs'], -6.8400002)
        # Other clients are used when the web ones have nothing
        self.assertEqual(extract([pr(None, 'WEB'), pr(other, 'VISIONOS')])['loudness_lkfs'], -9.0)


if __name__ == '__main__':
    unittest.main()
